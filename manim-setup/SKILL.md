---
name: manim-setup
description: >-
  Install Manim Community Edition, scaffold new Manim projects, configure uv,
  pip, Conda, Docker, or Jupyter/Colab environments, install LaTeX or Typst,
  troubleshoot installation errors, and migrate ManimGL code to ManimCE.
version: 0.22.0
---

# Manim Setup, Project Scaffolding & Environments

Use this skill when setting up a new Manim project, installing dependencies, running health checks, using Jupyter `%%manim` magic, or resolving installation/version conflicts. For general scene authoring, see [manim-best-practices](../manim-best-practices/SKILL.md).

## 1. Recommended Local Setup (`uv`)

ManimCE (v0.19+) bundles video encoding via `pyav` wheels—**no external `ffmpeg` binary installation is required**. The officially recommended workflow uses [`uv`](https://docs.astral.sh/uv/):

### System Prerequisites (Before `uv add manim`)
- **Windows**: No system libraries needed for prebuilt wheels. If `uv add manim` asks for MSVC, install **Microsoft C++ Build Tools** with the *Desktop development with C++* workload.
- **macOS**: Install Cairo and `pkg-config` via Homebrew:
  ```bash
  brew install cairo pkg-config
  ```
- **Linux**: Install C build tools, Python headers, Cairo, and Pango headers:
  - Debian/Ubuntu: `sudo apt update && sudo apt install build-essential python3-dev libcairo2-dev libpango1.0-dev`
  - Fedora: `sudo dnf install python3-devel pkg-config cairo-devel pango-devel`
  - Arch: `sudo pacman -Syu base-devel cairo pango`

### Initialize Project & Install Manim
Inspect the current workspace first:
- **New directory**:
  ```bash
  uv init my-manim-project
  cd my-manim-project
  uv add manim
  ```
- **Existing Python/`uv` directory**:
  ```bash
  uv add manim
  ```
- **Optional TeX-free math typesetting via Typst (v0.21+)**:
  ```bash
  uv add "manim[typst]"
  ```
  Bundles the Typst compiler directly—no system TeX or Typst binary needed for `Typst` / `MathTypst` mobjects.

- **Optional LaTeX installation (Required only for `Tex`, `MathTex`, and default `Matrix` / `Axes` math labels)**:
  - **Windows**: Install [MiKTeX](https://miktex.org/download)
  - **macOS**: Install [MacTeX](https://www.tug.org/mactex/)
  - **Linux**: `sudo apt install texlive-full` (Debian/Ubuntu) or `sudo dnf install texlive-scheme-full` (Fedora)
  - **Minimal TinyTeX**: See exact package list in [environments-and-troubleshooting.md](./references/environments-and-troubleshooting.md).

### Verify Installation
Always verify the environment before rendering complex scenes:
```bash
uv run manim --version
uv run manim checkhealth
```
> [!IMPORTANT]
> When Manim is installed in a local `uv` project without activating `.venv`, prefix all CLI commands with `uv run` (`uv run manim -ql main.py MyScene`). Confirm the first output line begins with `Manim Community v...`.

---

## 2. Scaffolding Files & Starter Scene

Manim provides a built-in project template command, or you can create `main.py` and `manim.cfg` directly:

```bash
uv run manim init project my-project --default
# Or insert a new scene into an existing file:
uv run manim new scene main.py
```

Minimal clean starter (`main.py`):
```python
from manim import *


class QuickCheck(Scene):
    def construct(self):
        circle = Circle(radius=1.2, color=BLUE, fill_opacity=0.5)
        label = Text("Manim Ready", font_size=36).next_to(circle, DOWN, buff=0.4)
        self.play(Create(circle), FadeIn(label, shift=UP * 0.2))
        self.wait(0.5)
```

Validate with a fast still render:
```bash
uv run manim -s -ql main.py QuickCheck
```

---

## 3. Alternative Environments (Summary)

- **Global `uv` tool**: `uv tool install manim` (exposes `manim` globally; locate interpreter for IDE autocomplete via `uv tool dir`).
- **Conda / Mamba / Pixi**:
  ```bash
  conda create -n manim-env && conda activate manim-env
  conda install -c conda-forge manim
  # Or with pixi: pixi init && pixi add manim
  ```
- **Docker**:
  ```bash
  docker run --rm -it -v "/abs/path/to/dir:/manim" manimcommunity/manim:stable manim -qm scene.py MyScene
  ```
  *(Never pass `-p` or `--show_in_file_browser` inside headless Docker containers.)*
- **JupyterLab / Notebooks (`%%manim` magic)**:
  ```python
  from manim import *
  ```
  ```python
  %%manim -qm -v WARNING SquareToCircle

  class SquareToCircle(Scene):
      def construct(self):
          s, c = Square(), Circle(color=PINK, fill_opacity=0.5)
          self.play(Create(s))
          self.play(Transform(s, c))
          self.wait()
  ```

---

## 4. Troubleshooting & ManimGL Migration

Load [environments-and-troubleshooting.md](./references/environments-and-troubleshooting.md) when encountering:
- `"there are no scenes inside that module"` (`manim` vs `manimgl` executable collision)
- `dvisvgm` / PostScript (`LIBGS`) PDF-to-SVG failures or missing LaTeX glyphs (`fmtutil -sys --all`)
- `ManimPango` / `pycairo` wheel build errors or Anaconda Cairo symbol conflicts
- Google Colab & Binder setup cells
- Translating `manimgl` (`from manimlib import *`, `CONFIG = {...}`) scripts to ManimCE
