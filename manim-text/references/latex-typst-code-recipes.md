# Advanced LaTeX, Typst & Code Highlighting Recipes

## 1. Custom LaTeX Packages & Font Templates (`TexTemplate`)

When using commands outside standard AMS packages (e.g., `\mathscr`, `\cancel`, `\bra`, `\ce`, TikZ):

```python
template = TexTemplate()
template.add_to_preamble(r"\usepackage{mathrsfs, cancel, physics}")

eq = MathTex(
    r"\mathscr{L}\{f(t)\} = \int_0^\infty \cancel{1} \cdot f(t)e^{-st}\,dt",
    tex_template=template,
)
```

Built-in font & language templates:
- `TexFontTemplates.french_cursive`, `TexFontTemplates.libertine`, `TexFontTemplates.palatino`, `TexFontTemplates.fourier_utopia`, `TexFontTemplates.droid_sans`, `TexFontTemplates.biolinum`
- `TexTemplateLibrary.ctex` (Chinese + LaTeX), `TexTemplateLibrary.threeb1b`

---

## 2. Debugging Complex `MathTex` Sub-Indices (`index_labels`)

When `{{ ... }}` or `substrings_to_isolate` isn't practical (e.g., coloring numerator vs denominator inside `\binom{2n}{n+2}` or a large `\sqrt{...}`), temporarily render `index_labels` with `-s -ql` to see exact glyph indices:

```python
expr = MathTex(r"\binom{2n}{n+2}", font_size=96)
# Temporarily add index overlay during development:
debug_labels = index_labels(expr[0])
self.add(expr, debug_labels)

# Once indices are known, remove debug_labels and slice directly:
expr[0][1:3].set_color(YELLOW)   # "2n"
expr[0][3:6].set_color(RED)      # "n+2"
```

### `substrings_to_isolate` Gotcha
`eq.set_color_by_tex("x", YELLOW)` only matches **complete submobject tex strings**, not arbitrary characters inside a single unsplit string! Always isolate first:
```python
poly = MathTex(
    r"p(x) = a_2 {x}^2 + a_1 x + a_0",
    substrings_to_isolate=["x"],     # Note: wrap superscripted/subscripted {x}^2 in braces so LaTeX remains valid when split!
)
poly.set_color_by_tex("x", YELLOW)
```

---

## 3. Custom Pygments Color Theme for `Code` (v0.21+)

In Manim v0.21+, `Code` delegates all syntax, foreground, background, and line-number colors to Pygments. Subclass any built-in style via `Code.get_pygments_style(name)`:

```python
from pygments.token import Comment, Keyword, Name, Number, String

BaseStyle = Code.get_pygments_style("monokai")


class CatppuccinStyle(BaseStyle):
    background_color = "#1e1e2e"
    line_number_color = "#6c7086"
    styles = {
        **BaseStyle.styles,
        Comment: "italic #6c7086",
        Keyword: "bold #cba6f7",
        Name.Function: "#89b4fa",
        String: "#a6e3a1",
        Number: "#fab387",
    }


listing = Code(
    code_string="def square(x: int) -> int:\n    # compute x^2\n    return x * x",
    language="python",
    formatter_style=CatppuccinStyle,
    background="window",
)
```
To override **only** the box fill/stroke without subclassing `Style`, pass `background_config={"fill_color": "#11111b", "stroke_color": "#45475a"}`.

---

## 4. Animated Line-by-Line Code Walkthrough Highlighting

Inspect `Code` structure cleanly (`code_mob.code_lines` / `Paragraph` lines inside `code_mob`) to slide a highlight bar across lines of code:

```python
class CodeWalkthrough(Scene):
    def construct(self):
        src = "x = 10\ny = x * 2\nprint(x + y)"
        listing = Code(
            code_string=src,
            language="python",
            formatter_style="monokai",
            background="window",
        )
        self.play(FadeIn(listing))

        # Access rendered code lines Paragraph (last submobject of Code: [bg, line_nums, code_lines] or [bg, code_lines]):
        code_lines = listing[-1]

        def make_line_highlight(line_idx: int) -> SurroundingRectangle:
            bar = SurroundingRectangle(
                code_lines[line_idx],
                color=YELLOW,
                fill_color=YELLOW,
                fill_opacity=0.18,
                stroke_width=1.5,
                buff=0.06,
            )
            bar.stretch_to_fit_width(listing[0].width - 0.3)
            bar.move_to([listing[0].get_x(), code_lines[line_idx].get_y(), 0])
            return bar

        hl = make_line_highlight(0)
        self.play(FadeIn(hl))
        for idx in (1, 2):
            self.play(Transform(hl, make_line_highlight(idx)), run_time=0.6)
        self.wait(0.5)
```

---

## 5. Lists, Titles & Terminal Typing

```python
# Title with full-width underline pinned to top of frame:
header = Title("Eigenvalues & Eigenvectors", include_underline=True, font_size=44)

# BulletedList (supports dot_buff in v0.21+):
bullets = BulletedList(
    " Preserves span along eigen-directions",
    r" Scales vectors by factor $\lambda$",
    " Determinant equals product of eigenvalues",
    font_size=34,
    buff=0.35,
    dot_buff=0.25,
).next_to(header, DOWN, buff=0.6)

self.play(Write(header))
for row in bullets:
    self.play(FadeIn(row, shift=RIGHT * 0.3), run_time=0.6)
# Dim non-active bullets to focus attention:
self.play(bullets.animate.fade_all_but(1, opacity=0.3))

# Realistic terminal typing with blinking cursor (v0.19+):
cmd = Text("uv run manim -qh scene.py", font="Consolas", font_size=32)
cursor = Rectangle(
    color=GREEN, fill_color=GREEN, fill_opacity=1.0,
    width=0.18, height=cmd.height * 1.1,
).move_to(cmd[0])
self.play(TypeWithCursor(cmd, cursor, time_per_char=0.06, leave_cursor_on=True))
self.play(Blink(cursor, blinks=2))
```
