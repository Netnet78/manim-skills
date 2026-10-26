---
name: manim-render
description: >-
  Render and export Manim scenes to MP4, MOV, WebM, GIF, PNG stills, or PNG
  sequences; configure CLI flags, quality presets, transparent backgrounds,
  OpenGL live preview, sections, caching, manim.cfg, and tempconfig.
version: 0.22.0
---

# Rendering, CLI Flags, Output Formats & Configuration

Use this skill when running `manim` from the CLI or Python scripts, selecting output formats, rendering transparent videos/GIFs/stills, configuring `manim.cfg` or `tempconfig`, managing cache, or exporting presentation sections. See [manim-best-practices](../manim-best-practices/SKILL.md) for other topics.

## 1. Core CLI Invocation & Quality Presets

```bash
# Default command is `render` (`manim [OPTIONS] FILE [SCENES...]`)
manim -ql scene.py MyScene
# Inside a local uv project without activated venv:
uv run manim -ql scene.py MyScene
```

| Flag | Long Option | Resolution | FPS | Output Subfolder | Best For |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `-ql` | `--quality l` | 854 × 480 | 15 | `480p15/` | Rapid agent iteration & layout checks |
| `-qm` | `--quality m` | 1280 × 720 | 30 | `720p30/` | Smooth draft previews & notebooks |
| `-qh` | `--quality h` | 1920 × 1080 | 60 | `1080p60/` | Standard HD production (default) |
| `-qp` | `--quality p` | 2560 × 1440 | 60 | `1440p60/` | 2K QHD export |
| `-qk` | `--quality k` | 3840 × 2160 | 60 | `2160p60/` | 4K UHD export |

Custom resolution / FPS override:
```bash
# 9:16 Vertical Video (1080x1920 @ 60fps):
manim -r 1080,1920 --fps 60 scene.py VerticalShort
```
*(Note: When changing aspect ratio, also set `config.frame_width = 9; config.frame_height = 16` in code or `manim.cfg` if you want vertical coordinate proportions.)*

---

## 2. Unified Output Selection (`--format`, v0.22+)

> [!WARNING]
> Legacy output flags `--write_to_movie`, `-i`/`--save_as_gif`, `-g`/`--save_pngs`, `--force_window`, `--custom_folders`, `--flush_cache`, and `-f` **were removed in Manim v0.22.0**. Always use `--format` instead.

| `--format` Value | Artifact Produced & Behavior |
| :--- | :--- |
| `auto` *(default)* | Produces `.mp4` for opaque scenes, `.mov` when `-t`/`--transparent` is set, a fallback last-frame `.png` if the scene has no `play`/`wait` calls, and no file during OpenGL live preview (`-l`). |
| `mp4` | H.264 MP4 video (raises error if `-t` transparent or if scene has zero `play`/`wait` calls). |
| `mov` | QuickTime MOV (supports alpha transparency with `-t`). |
| `webm` | WebM video (supports alpha transparency with `-t`). |
| `gif` | Animated GIF (supports alpha transparency with `-t`). |
| `png` *(or `-s`)* | Fast-forwards all animations and writes **only the last frame** to `media/images/<module>/`. |
| `png-sequence` | Renders every frame as numbered PNGs in `media/images/<module>/<Scene>/0000.png`... |
| `none` | Evaluates the scene without writing a primary media file. |

### Common Export Recipes
```bash
# Fast last-frame still image (high quality):
manim -sqh scene.py MyScene
# Equivalent explicit form:
manim --format=png -qh scene.py MyScene

# Animated GIF:
manim --format=gif -qm scene.py MyScene

# Transparent video (MOV by default, or WebM):
manim -t -qh scene.py MyScene
manim -t --format=webm -qh scene.py MyScene

# Every frame as PNG sequence:
manim --format=png-sequence -qm scene.py MyScene

# Dry run (verify Python/Manim execution without writing media):
manim --dry_run scene.py MyScene
```

---

## 3. Preview, Partial Slicing, Reproducibility & Cache

- **Post-render preview (`-p` / `--preview`)**: Opens the finished video/image in the host viewer after rendering (works identically for Cairo and OpenGL). Only use `-p` when a human user wants the player launched; omit `-p` in automated agent test runs.
- **Reveal in file browser**: `--show_in_file_browser` (replaces removed `-f`).
- **OpenGL interactive live preview (`-l` / `--live-preview`)**:
  ```bash
  manim --renderer=opengl -l scene.py MyScene
  # Record MP4 simultaneously while viewing live preview:
  manim --renderer=opengl -l --format=mp4 scene.py MyScene
  ```
- **Render specific `self.play()` slice (`-n`)**:
  ```bash
  manim -ql -n 4,8 scene.py MyScene   # Render only animations #4 through #8 (0-indexed)
  manim -ql -n 5 scene.py MyScene     # Render from animation #5 to the end
  ```
  *(Updaters and state mutations from skipped earlier animations still execute so frame #4 starts in the exact right state!)*
- **Render all scenes in file (`-a` / `--write_all`)**: `manim -ql -a scene.py`
- **Custom output filename (`-o` / `--output_file`)**: `manim -o intro --format=mp4 scene.py MyScene` *(cannot be combined with `-a` or multiple scene names; format suffix is enforced automatically)*.
- **Background color override (`-c` / `--background_color`)**: `manim -c WHITE scene.py MyScene`
- **Deterministic random seed (v0.20+)**: `manim --seed 42 scene.py MyScene`
- **Clear segment cache (v0.22+)**:
  ```bash
  manim cache clear scene.py MyScene
  ```
- **Parallel segment encoding (v0.21+)**: Overlap video encoding with frame rendering on multi-core machines:
  ```bash
  manim --max-inflight-encoders 4 --encoder-queue-size 8 -qh scene.py MyScene
  ```

---

## 4. Default Output Directory Structure

```text
project/
├── scene.py
└── media/
    ├── images/
    │   └── scene/
    │       ├── MyScene_ManimCE_v0.22.0.png      # -s / --format=png
    │       └── MyScene/0000.png                 # --format=png-sequence
    ├── videos/
    │   └── scene/
    │       └── 1080p60/
    │           ├── MyScene.mp4
    │           ├── partial_movie_files/MyScene/ # Cached per-play() segments
    │           └── sections/                    # Created when --save_sections is set
    ├── texts/                                   # Cached Pango SVGs
    └── Tex/                                     # Cached LaTeX SVGs
```

---

## 5. Presentation Sections (`Scene.next_section`)

Split a single scene into separate sub-videos (for slide decks like `manim-slides` or NLE editing) and/or skip heavy finished parts during iteration:

```python
class LectureScene(Scene):
    def construct(self):
        # Initial default section starts automatically
        s = Square()
        self.play(Create(s))

        # Skip rendering this completed section while iterating on later ones:
        self.next_section("transform step", skip_animations=True)
        self.play(Transform(s, Circle()))

        # Active section being developed:
        self.next_section("final fade", section_type="default.normal")
        self.play(FadeOut(s))
```

Export per-section videos + JSON index (`sections/<SceneName>.json`):
```bash
manim --save_sections -qh scene.py LectureScene
```
> [!NOTE]
> Every section must contain **at least one animation or `self.wait()`**; sections with only `self.add(...)` produce no frames and are omitted from section output. Read exact section video filenames from `<SceneName>.json`'s `"video"` field.

---

## 6. Deep Configuration, Custom Encoding & Programmatic Renders

For `manim.cfg` cascading precedence, custom directory templates, `[video_encoder]` codec/CRF tuning, programmatic `tempconfig({...})` rendering, OpenGL `interactive_embed()`, and `Manager` lifecycle details, load [configuration-and-encoding.md](./references/configuration-and-encoding.md).
