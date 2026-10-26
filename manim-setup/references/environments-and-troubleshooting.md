# Environments, Troubleshooting & ManimGL Migration Reference

## TinyTeX Minimal LaTeX Package List

If installing full TeX Live / MacTeX is impractical, install [TinyTeX](https://yihui.org/tinytex/) and install Manim's required TeX packages via `tlmgr`:

```bash
tlmgr install \
  amsmath babel-english cbfonts-fd cm-super count1to ctex doublestroke \
  dvisvgm everysel fontspec frcursive fundus-calligra gnu-freefont \
  jknapltx latex-bin mathastext microtype multitoc physics preview \
  prelim2e ragged2e relsize rsfs setspace standalone tipa wasy \
  wasysym xcolor xetex xkeyval
```

---

## Google Colaboratory & Binder Setup

### Google Colab Setup Cell
Run in a cell, then **Restart Runtime** before importing `manim`:

```python
!sudo apt update
!sudo apt install -y libcairo2-dev \
    texlive texlive-latex-extra texlive-fonts-extra \
    texlive-latex-recommended texlive-science \
    tipa libpango1.0-dev
!pip install manim
```

After restarting the runtime, run `from manim import *` in one cell and use `%%manim -qm -v WARNING SceneName` at the top of scene cells. Videos embed automatically in Colab.

### Custom Binder Dockerfile
Place alongside `.ipynb` files in a public repository:
```dockerfile
FROM docker.io/manimcommunity/manim:stable
COPY --chown=manimuser:manimuser . /manim
```

### Persistent Docker Container (for Custom `tlmgr` Packages)
Note: `manimcommunity/manim` includes minimal TeX Live without `ctex`. To persist extra TeX packages:
```bash
docker run -it --name my-manim -v "/full/path:/manim" manimcommunity/manim:stable bash
# Inside container: tlmgr install ctex && exit
docker start my-manim
docker exec -it my-manim manim -qm scene.py MyScene
```
On Linux hosts, pass `--user="$(id -u):$(id -g)"` to `docker run` so generated `media/` files are owned by your host user.

---

## Pinning or Switching Python Versions with `uv`

ManimCE supports Python 3.9–3.13+. If a third-party dependency needs a specific Python version:
```bash
uv init --python 3.12 manimations
cd manimations
uv add manim
```
In an existing project, update `requires-python = ">=3.12"` in `pyproject.toml`, then run:
```bash
uv python pin 3.12
uv sync
```

---

## Common Installation & Runtime Errors

### 1. `"there are no scenes inside that module"`
1. Verify the `.py` file was saved and the class inherits from `Scene` (or a `Scene` subclass like `ThreeDScene`, `MovingCameraScene`).
2. Check for **`manimgl` binary collision**: both `manim` (Community) and `manimgl` (3b1b) install a `manim` executable!
   - Run `manim --version`. If it does **not** start with `Manim Community v...`, `manimgl` overwrote `manim`.
   - Fix: run `manimce ...`, `python -m manim ...`, `uv run manim ...`, or reinstall `manim` in an isolated virtual environment.

### 2. Manim Only Renders a Single Black Frame
- Check the method spelling inside your `Scene` subclass: it **must** be `def construct(self):` (not `contruct`, `build`, or `render`).
- Ensure mobjects are actually added via `self.add(...)` or introduced via `self.play(Create(...))` / `self.play(FadeIn(...))`.

### 3. `dvisvgm` Error: "does not support converting PDF to SVG"
Manim requires `dvisvgm >= 2.4` with PostScript specials enabled:
1. Run `dvisvgm --version` and `dvisvgm -l`.
2. Confirm `ps  dvips PostScript specials` appears in `dvisvgm -l`.
3. If missing, check `dvisvgm -h` for `--libgs=filename`. Locate your system Ghostscript shared library (`gsdll64.dll` on Windows, `libgs.so` on Linux, `libgsl.dylib` on macOS) and set `LIBGS`:
   - Bash: `export LIBGS=/path/to/libgs.so`
   - PowerShell: `$env:LIBGS = "C:\path\to\gsdll64.dll"`
   Verify with `dvisvgm -V1`.

### 4. Missing Letters / Symbols in `Tex` or `MathTex`
Rebuild LaTeX font maps:
```bash
fmtutil -sys --all
```
Or switch to `Typst` / `MathTypst` (`uv add "manim[typst]"`) if LaTeX font setup is broken.

### 5. Anaconda `ImportError: Symbol not found` in `cairo`
Anaconda's default channel ships an incompatible `cairo` build. Reinstall `pycairo` from `conda-forge`:
```bash
conda install -c conda-forge pycairo
```

### 6. `manimpango/cmanimpango.c` Not Found During Source Build
Occurs on architectures without pre-built `ManimPango` wheels when Cython is missing:
```bash
pip install Cython
# Ensure system Pango/Cairo dev headers + pkg-config are installed, then retry
```

---

## Migrating Code from `manimgl` / Legacy Manim to ManimCE

Identify the source dialect from the import line:
- `from manim import *` -> **ManimCE** (already target dialect)
- `from manimlib import *` -> **ManimGL**
- `from manimlib.imports import *` or `from big_ol_pile_of_manim_imports import *` -> **Legacy ManimCairo**

### Key Translation Rules
1. **Replace `CONFIG` Dictionaries** (dropped in ManimCE v0.2.0):
   ```python
   # OLD (ManimGL / Legacy)
   class CustomShape(VMobject):
       CONFIG = {
           "stroke_color": RED,
           "fill_opacity": 0.7,
           "custom_param": 42,
       }

   # NEW (ManimCE)
   class CustomShape(VMobject):
       def __init__(
           self,
           stroke_color=RED,
           fill_opacity=0.7,
           custom_param=42,
           **kwargs,
       ):
           self.custom_param = custom_param
           super().__init__(
               stroke_color=stroke_color,
               fill_opacity=fill_opacity,
               **kwargs,
           )
   ```
   For `Scene` subclasses, put pre-animation setup in `def setup(self):` (avoid overriding `Scene.__init__` unless calling `super().__init__(**kwargs)`).

2. **Common Class & Method Renames**:
   | ManimGL / Legacy | ManimCE Equivalent |
   | :--- | :--- |
   | `ShowCreation(m)` | `Create(m)` |
   | `Uncreate(m)` / `ShowCreationThenDestruction(m)` | `Uncreate(m)` / `ShowPassingFlash(m)` |
   | `TextMobject(...)` / `TexText(...)` | `Tex(...)` (LaTeX) or `Text(...)` (Pango) |
   | `TexMobject(...)` | `MathTex(...)` |
   | `GraphScene` (removed) | `Axes(...)` inside a standard `Scene` (`ax.plot(...)`) |
   | `ax.get_graph(fn)` | `ax.plot(fn)` |
   | `SmallDot(...)` | `Dot(radius=0.04, ...)` |
   | `mob.set_width(w)` / `mob.get_width()` | `mob.width = w` / `mob.scale_to_fit_width(w)` / `mob.width` |
   | `mob.set_height(h)` / `mob.get_height()` | `mob.height = h` / `mob.scale_to_fit_height(h)` / `mob.height` |
   | `InteractiveScene` / `self.frame` | `MovingCameraScene` with `self.camera.frame` (or `--renderer=opengl` with `self.interactive_embed()`) |
