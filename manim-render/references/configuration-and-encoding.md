# Configuration, Custom Encoding, Programmatic Rendering & Render Lifecycle

## 1. Configuration Precedence (Lowest to Highest)

Manim resolves configuration into its global `config` (`ManimConfig`) singleton in this strict order:
1. **Library-wide default config** (shipped inside `manim` — never edit).
2. **User-wide `manim.cfg`**:
   - Windows: `%APPDATA%\Manim\manim.cfg` (`~/AppData/Roaming/Manim/manim.cfg`)
   - macOS / Linux: `~/.config/manim/manim.cfg`
3. **Folder-wide `manim.cfg`** (located in the **same folder as the target `.py` scene file**, NOT the current working directory!) **OR** explicit `--config_file path/to/custom.cfg` (which ignores the folder-wide `manim.cfg`).
4. **CLI flags** (`-qh`, `--format=webm`, `-c`, etc.).
5. **Programmatic assignments** in Python (`config.background_color = WHITE` or `with tempconfig({...}):`).

Inspect active resolved configuration at any time:
```bash
manim cfg show
manim render --help
```

---

## 2. Authoring `manim.cfg`

Folder-wide config files **must** be named `manim.cfg`. Option names under `[CLI]` match the **long names** of CLI flags:

```ini
[CLI]
quality = high_quality
frame_rate = 60
background_color = #1e1e2e
background_opacity = 1.0
format = auto
preview = False
save_sections = False
max_files_cached = 200
max_inflight_encoders = 4
encoder_queue_size = 8

# Custom directory layout with placeholders (replaces removed --custom_folders)
media_dir = ./media
video_dir = {media_dir}/videos/{module_name}/{quality}
images_dir = {media_dir}/images/{module_name}
sections_dir = {video_dir}/sections
partial_movie_dir = {video_dir}/partial_movie_files/{scene_name}
tex_dir = {media_dir}/Tex
text_dir = {media_dir}/texts
log_dir = {media_dir}/logs

[video_encoder]
codec = libx264
pixel_format = yuv420p

[video_encoder.options]
crf = 18
preset = slow

[media]
loglevel = ERROR

[logger]
logging_level = INFO
```

### Custom Video Encoding via CLI (v0.22+)
```bash
manim render \
  --video-codec libx264 \
  --pixel-format yuv420p \
  --encoder-option crf=18 \
  --encoder-option preset=slow \
  scene.py MyScene
```
- `codec` and `pixel_format` default to `auto` (automatically choosing H.264 `yuv420p` for MP4, PNG/qtrle/ProRes-compatible alpha for transparent MOV, VP9 `yuva420p` for transparent WebM, etc.).
- Passing any `--encoder-option KEY=VALUE` on the CLI replaces the entire `[video_encoder.options]` map from `manim.cfg`.
- Encoder settings are part of segment cache hashes, so changing `crf` or `codec` cleanly invalidates and re-encodes cached segments.

---

## 3. Programmatic Rendering & `tempconfig`

When rendering scenes directly from Python (e.g., batch generation scripts, tests, or web backends), **instantiate the `Scene` inside `tempconfig`** because output & session specifications are snapshotted during `Scene.__init__()`:

```python
from manim import *


class GeneratedScene(Scene):
    def __init__(self, title_text: str = "Hello", **kwargs):
        self.title_text = title_text
        super().__init__(**kwargs)

    def construct(self):
        self.play(Write(Text(self.title_text)))
        self.wait(0.5)


if __name__ == "__main__":
    with tempconfig(
        {
            "quality": "medium_quality",
            "format": "mp4",
            "preview": False,
            "output_file": "greeting_video",
        }
    ):
        scene = GeneratedScene(title_text="Programmatic Render")
        scene.render()
        output_path = scene.renderer.file_writer.final_file_path
        print(f"Rendered file at: {output_path}")
```

> [!IMPORTANT]
> In Manim v0.22+, rendering no longer mutates `config.output_file`. Always read the final artifact path from `scene.renderer.file_writer.final_file_path`.

---

## 4. Aspect Ratio & Frame Geometry Configuration

`config` keeps `frame_width`, `frame_height`, `frame_x_radius`, and `frame_y_radius` internally synchronized:

```python
# Vertical 9:16 video (TikTok / YouTube Shorts / Reels)
config.pixel_width = 1080
config.pixel_height = 1920
config.frame_width = 9.0
config.frame_height = 16.0

# Square 1:1 post
config.pixel_width = 1080
config.pixel_height = 1080
config.frame_width = 8.0
config.frame_height = 8.0
```

Useful read-only/derived properties during `construct()`:
- `config.frame_width`, `config.frame_height`
- `config.frame_x_radius` (`frame_width / 2`), `config.frame_y_radius` (`frame_height / 2`)
- `config.pixel_width`, `config.pixel_height`, `config.frame_rate`
- `config.top`, `config.bottom`, `config.left_side`, `config.right_side`

---

## 5. Cairo vs OpenGL Renderers & Interactive Mode

- **Cairo (`--renderer=cairo`, default)**: Mature, rock-solid 2D vector & SVG/TeX rendering, deterministic static/moving background caching. Best default for 95% of 2D and basic 3D educational videos.
- **OpenGL (`--renderer=opengl`)**: GPU-accelerated shader pipeline supporting true 3D depth/surfaces (`OpenGLSurface`), real-time live window (`-l`), and interactive IPython shell (`self.interactive_embed()`):
  ```python
  class InteractiveDemo(Scene):
      def construct(self):
          c = Circle()
          self.play(Create(c))
          self.interactive_embed()  # Opens interactive IPython + mouse orbit/pan window
  ```
  Run with: `manim --renderer=opengl -l scene.py InteractiveDemo`.
  *(If `interactive_embed()` raises `sqlite3.ProgrammingError` due to IPython history threads, pin `IPython==8.0.1` or disable IPython SQLite history.)*

---

## 6. Render Lifecycle Summary (`Manager`, v0.22+)

1. `Scene.__init__()` instantiates `CairoRenderer` or `OpenGLRenderer`, snapshots `self.session_spec` and `self.output_plan`, and initializes `SceneFileWriter` (backed by `pyav`/`libav`).
2. `scene.render()` delegates to `scene.manager` (`Manager`), executing:
   - `scene.setup()` -> override this in custom `Scene` base classes instead of `__init__` when no custom args are needed.
   - `scene.construct()` -> user screenplay; each `self.play()` / `self.wait()` computes a play hash, checks `partial_movie_files/` cache, steps `t ∈ np.arange(0, run_time, 1 / frame_rate)`, runs `Animation.interpolate` + mobject/scene updaters, and streams `uint8` RGBA `(H, W, 4)` frames to `VideoSegmentEncoder`.
   - `scene.tear_down()` -> post-render hook before finalization.
   - `manager.post_construct()` -> joins any in-flight partial encoders, concatenates segments + mixes audio into `final_file_path`, and triggers preview (`-p`) if requested.
