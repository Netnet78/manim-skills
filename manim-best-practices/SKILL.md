---
name: manim-best-practices
description: >-
  Router and core best practices for Manim Community Edition (ManimCE v0.22+).
  Use whenever creating, editing, rendering, migrating, or debugging Python
  mathematical and technical animations with Manim (`from manim import *`).
version: 0.22.0
---

# Manim Community Edition — Best Practices & Skill Router

This is the entry-point skill for **Manim Community Edition (`manim` / ManimCE, stable v0.22.0)**. Load the specialized sub-skills below based on your current task.

## Skill Router

| Task / Domain | Skill to Load |
| :--- | :--- |
| Install Manim (`uv`, `pip`, Conda, Docker, Jupyter/Colab), scaffold projects, fix `dvisvgm`/Pango/LaTeX errors, or migrate from `manimgl` | [manim-setup](../manim-setup/SKILL.md) |
| Render CLI flags, `--format` options (`mp4`, `mov`, `webm`, `gif`, `png`, `png-sequence`), OpenGL live preview (`-l`), `manim.cfg`, `tempconfig`, caching, or sections | [manim-render](../manim-render/SKILL.md) |
| Shapes, geometry, positioning (`next_to`, `align_to`, `to_edge`), `VGroup` layout (`arrange`, `arrange_in_grid`), styling, colors, `Table`, `Matrix`, `Graph`, SVG/images | [manim-mobjects](../manim-mobjects/SKILL.md) |
| `self.play()`, `.animate`, `Transform` vs `ReplacementTransform`, `LaggedStart`/`Succession`, `rate_functions`, `ValueTracker`, updaters, `Mobject.always`, custom `Animation` | [manim-animations](../manim-animations/SKILL.md) |
| `Text`, `MarkupText` (Pango), `Tex`, `MathTex` (LaTeX, `{{ ... }}` isolation, `TransformMatchingTex`), `Typst`/`MathTypst` (TeX-free), `Code` listings, `DecimalNumber`/`Variable` | [manim-text](../manim-text/SKILL.md) |
| 2D plotting (`Axes`, `NumberPlane`, `PolarPlane`, `ComplexPlane`, `BarChart`), `LinearTransformationScene`, vector fields, `MovingCameraScene`, `ZoomedScene`, 3D (`ThreeDScene`, `Surface`) | [manim-math-3d](../manim-math-3d/SKILL.md) |
| Audio (`add_sound`), `.srt` subcaptions, `manim-voiceover` synced TTS/mic narration & bookmarks, and Manim plugins | [manim-voiceover](../manim-voiceover/SKILL.md) |
| Search live `docs.manim.community` via ReadTheDocs API, fetch raw `.rst.txt`/`.md.txt` sources, or inspect local Python signatures | [manim-docs](../manim-docs/SKILL.md) |

---

## Critical Rules (Always Apply — Overrides Outdated Training Data)

### 1. Never Confuse Manim Flavors
There are three **incompatible** Python packages named "Manim":
- **Manim Community Edition (ManimCE — USE THIS)**: PyPI `manim`, imported as `from manim import *`. CLI `manim --version` prints `Manim Community v...`.
- **ManimGL (3b1b's experimental fork — DO NOT MIX)**: PyPI `manimgl`, imported as `from manimlib import *`. Uses `InteractiveScene`, `ShowCreation`, `TexText`, `CONFIG = {...}`.
- **Legacy ManimCairo (pre-2020 — OBSOLETE)**: `from manimlib.imports import *` or `from big_ol_pile_of_manim_imports import *`.

**Never generate legacy/ManimGL APIs in ManimCE code:**
- `ShowCreation(mob)` -> **`Create(mob)`**
- `TextMobject(...)` / `TexText(...)` -> **`Tex(...)`** (LaTeX), **`Text(...)`** (Pango), or **`Typst(...)`** (Typst)
- `TexMobject(...)` -> **`MathTex(...)`** (LaTeX) or **`MathTypst(...)`** (Typst)
- `CONFIG = {...}` class dicts -> **Removed**. Define `__init__(self, ..., **kwargs)` or `setup(self)` or class attributes.

### 2. Modern ManimCE v0.19–v0.22 Breaking-Change Guardrails
- **Unified `--format` CLI (v0.22+)**: Old output flags (`-i`/`--save_as_gif`, `-g`/`--save_pngs`, `--write_to_movie`, `--force_window`, `--custom_folders`, `--flush_cache`, `-f`) **were removed in v0.22**.
  - Use `--format=gif`, `--format=png` (or `-s` for last frame), `--format=png-sequence`, `--format=webm`, `--format=mov`, `--format=mp4`, or `--format=none`.
  - `-p` (`--preview`) opens the finished file after rendering (both Cairo and OpenGL).
  - `-l` (`--live-preview`) opens an interactive live window (`--renderer=opengl -l`). Note: `-ql` means `-q l` (low quality), whereas standalone `-l` means `--live-preview`.
  - Clear partial movie cache via `manim cache clear scene.py SceneName` (not `--flush_cache`).
- **Rewritten `Code` Mobject (v0.19+ / v0.21+)**: Old `Code(file_name=..., code=..., style=..., font=..., insert_line_no=...)` **raises `TypeError`**. Use:
  ```python
  Code(
      code_string="def f(x):\n    return x**2",  # or code_file="path.py"
      language="python",
      formatter_style="vim",                     # see Code.get_styles_list()
      add_line_numbers=True,
      background="rectangle",                    # "rectangle" or "window"
      background_config={"stroke_color": WHITE},
      paragraph_config={"font": "Noto Sans Mono"},  # Note: color key here is ignored; use formatter_style
  )
  ```
- **`SurroundingRectangle` Keyword Arguments (v0.19+)**: Accepts `*mobjects` variadically, so `SurroundingRectangle(mob, RED, 0.3)` **raises an error**. Always pass keyword arguments: `SurroundingRectangle(mob, color=RED, buff=0.3)`.
- **`rate_functions` Exports**: Common functions (`smooth`, `linear`, `there_and_back`, `rush_into`, `rush_from`, `wiggle`, `double_smooth`) are in `from manim import *`, **but standard easings (`ease_in_sine`, `ease_out_cubic`, `ease_in_out_quad`, etc.) are NOT exported globally**—always access them via `rate_functions.ease_in_out_sine`.
- **`Sector` Radius (v0.19+)**: `Sector(radius=2, angle=PI/2)` (removed `outer_radius`/`inner_radius`; use `AnnularSector(inner_radius=1, outer_radius=2, angle=PI/2)` for rings).
- **`Scene.next_section` & `ManimColor.from_hex` (v0.19+)**: Parameter `type=` renamed to `section_type=`; `hex=` renamed to `hex_str=`.
- **No External FFmpeg Required (v0.19+) & TeX-Free Math Option (v0.21+)**: Video encoding uses bundled `pyav` wheels automatically, and `pip install "manim[typst]"` provides `Typst` / `MathTypst` math typesetting without installing LaTeX.

---

## Coordinate System & Visual Layout Discipline

Manim's default 16:9 canvas has origin `ORIGIN = [0, 0, 0]` at the **center of the screen**:
- **Horizontal (`RIGHT` = `+x`, `LEFT` = `-x`)**: `config.frame_width` = $14\frac{2}{9} \approx 14.22$ units (`x` spans `[-7.11, +7.11]`).
- **Vertical (`UP` = `+y`, `DOWN` = `-y`)**: `config.frame_height` = `8.0` units (`y` spans `[-4.0, +4.0]`).
- **Depth (`OUT` = `+z` toward viewer, `IN` = `-z` away)**: `[0, 0, ±1]`.

To prevent overlapping mobjects and off-screen clipping:
1. **Respect Safe Margins**: Keep content within `x ∈ [-6.5, 6.5]`, `y ∈ [-3.5, 3.5]` (`mob.to_edge(UP, buff=0.5)`).
2. **Never Leave Everything at `ORIGIN`**: Newly instantiated mobjects default to `[0, 0, 0]`. Always position via `VGroup(...).arrange(...)`, `.next_to(...)`, `.to_edge(...)`, or `axes @ (x, y)`.
3. **Clamp Wide Elements**: Long equations, `Table`, or `Code` blocks easily exceed frame bounds. Guard width/height explicitly:
   ```python
   if mob.width > config.frame_width - 1.2:
       mob.scale_to_fit_width(config.frame_width - 1.2)
   if mob.height > config.frame_height - 1.0:
       mob.scale_to_fit_height(config.frame_height - 1.0)
   ```
4. **Clear Stale Scene Elements**: Before introducing a new visual beat, `FadeOut` or `Transform` prior mobjects so text never stacks on top of earlier text.
5. **Default Fill Opacity Is `0.0`**: Geometric `VMobject` shapes (`Circle`, `Square`, `Polygon`) have stroke only (`fill_opacity=0`) unless you pass `fill_opacity=0.5` or `.set_fill(COLOR, opacity=...)`.

---

## Agent Development & Verification Workflow

Never render full 1080p60 (`-qh`) or 4K (`-qk`) videos while iterating unless explicitly requested by the user:

1. **Syntax & Logic Smoke Check (Fastest, no files written)**:
   ```bash
   manim --dry_run scene.py SceneName
   # (Prefix with `uv run` if inside a uv-managed project: `uv run manim ...`)
   ```
2. **Visual Layout Check via Last-Frame PNG (`-s -ql`)**:
   ```bash
   manim -s -ql scene.py SceneName
   ```
   Inspect the generated image in `media/images/<module>/SceneName_ManimCE_*.png` to verify spacing, alignment, LaTeX/Typst rendering, and frame margins. For multi-beat scenes, place temporary `return` statements or use `--format=png-sequence -ql` to check key frames.
3. **Low-Quality Motion Verification (`-ql`, 854x480 @ 15fps)**:
   ```bash
   manim -ql scene.py SceneName
   ```
   Use `-n <start>,<end>` (e.g., `manim -ql -n 3,6 scene.py SceneName`) to re-render only specific `self.play()` calls when tuning a long scene.
4. **Final Production Export (Only when ready or requested)**:
   ```bash
   manim -qh scene.py SceneName   # 1920x1080 @ 60fps
   ```
