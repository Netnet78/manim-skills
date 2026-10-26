---
name: manim-text
description: >-
  Render text, equations, formulas, numbers, and syntax-highlighted code in
  Manim using Pango (Text, MarkupText), LaTeX (Tex, MathTex, TransformMatchingTex),
  Typst (Typst, MathTypst), Code listings, and Variable/DecimalNumber mobjects.
version: 0.22.0
---

# Rendering Text, Equations (LaTeX & Typst), Numbers & Code

Use this skill whenever adding typography, mathematical formulas, step-by-step equation derivations, dynamic numbers, or syntax-highlighted source code. See [manim-best-practices](../manim-best-practices/SKILL.md) for other topics.

## Choosing the Right Text Engine

| Engine | Classes | System Requirement | Best For |
| :--- | :--- | :--- | :--- |
| **Pango** | `Text`, `MarkupText`, `Paragraph` | Built-in (`ManimPango`) | UI titles, labels, multilingual Unicode (CJK/Arabic/Emoji), custom `.ttf`/`.otf` fonts |
| **Typst** *(v0.21+)* | `Typst`, `MathTypst` | `pip install "manim[typst]"` *(no LaTeX needed!)* | Fast math & rich markup without installing multi-GB TeX distributions |
| **LaTeX** | `Tex`, `MathTex`, `Title`, `BulletedList` | System LaTeX (`MiKTeX` / `MacTeX` / `TeX Live`) | Classic 3Blue1Brown equations, `TransformMatchingTex`, specialized TeX packages |
| **Pygments + Pango** | `Code` | Built-in (`Pygments`) | Syntax-highlighted source code blocks & window cards |

---

## 1. Plain & Styled Text Without LaTeX (`Text` & `MarkupText`)

```python
title = Text(
    "Gradient Descent",
    font="Noto Sans",            # Inspect installed fonts via manimpango.list_fonts()
    font_size=56,                # Default font_size is 48
    weight=BOLD,                 # NORMAL, LIGHT, BOLD, HEAVY, ULTRABOLD
    slant=NORMAL,                # NORMAL, ITALIC, OBLIQUE
    t2c={"Gradient": BLUE, "Descent": TEAL},   # Substring or slice {"[0:8]": BLUE} coloring
    disable_ligatures=True,      # Ensures 1-to-1 character indexing (avoids "fi"/"fl" merging!)
)

# Gradient text:
hero = Text("ManimCE", gradient=(BLUE, PURPLE, PINK), font_size=72)

# Custom local .ttf/.otf font file:
with register_font("assets/fonts/JetBrainsMono-Regular.ttf"):
    mono = Text("x = 42", font="JetBrains Mono")
```

> [!IMPORTANT]
> **Indexing `Text` Submobjects**: Whitespace characters produce no glyphs and are stripped from submobject indices (`len(Text("a b")) == 2`), and font ligatures (`fi`, `fl`) merge two characters into one glyph unless `disable_ligatures=True` is set! For complex inline styling, prefer `MarkupText`:

```python
 rich = MarkupText(
     f'Optimize <span fgcolor="{YELLOW}" weight="bold">loss</span> with <u>learning rate</u> η',
     font_size=36,
 )
```
*(In `MarkupText`, always escape literal `<`, `>`, and `&` as `&lt;`, `&gt;`, `&amp;`!)*

---

## 2. Equations & Markup With Typst (`Typst` & `MathTypst`, v0.21+)

Requires `uv add "manim[typst]"` (bundles the Typst compiler; no system TeX required).

```python
# General Typst markup + label selection (#box[...] <label>):
doc = Typst(
    r"#box[*Theorem 1.*] <thm> Every convergent sequence is bounded.",
    font_size=40,
)
doc.select("thm").set_color(YELLOW)

# Display math + Manim {{ expr : label }} / positional {{ expr }} selection:
eq = MathTypst(
    r"{{ a^2 + b^2 : lhs }} = {{ c^2 }}",
    font_size=68,
)
eq.select("lhs").set_color(BLUE)
eq.select(1).set_color(GREEN)     # 0-indexed unnamed/all {{ ... }} groups
```
*(Note: The `{{ ... }}` shorthand is supported on `MathTypst`; in `Typst`, use native Typst `#box[...] <label>` syntax.)*

---

## 3. Equations With LaTeX (`Tex` & `MathTex`)

Always pass **raw strings (`r"..."`)** so backslashes (`\frac`, `\beta`, `\\`) are never eaten by Python escapes!

- **`MathTex(...)`**: Already inside an `align*` math environment! **Never wrap `MathTex` strings in `$...$`**, and use `&` / `\\` directly for multi-line aligned derivations:
  ```python
  deriv = MathTex(
      r"f(x) &= (x + 1)^2 \\",
      r"&= x^2 + 2x + 1",
      font_size=48,
  )
  ```
- **`Tex(...)`**: Starts in LaTeX **text mode**; wrap inline math in `$...$`:
  ```python
  statement = Tex(r"For all $x \in \mathbb{R}$, we have $e^{ix} = \cos x + i\sin x$.")
  ```

### Isolating Terms & Morphing Equations (`{{ ... }}` & `TransformMatchingTex`)
Enclose tokens in **`{{ ... }}`** (preceded by start-of-string or whitespace!) so `TransformMatchingTex` smoothly glides matching symbols into their new positions:

```python
eq1 = MathTex(r"{{ a^2 }} + {{ b^2 }} = {{ c^2 }}")
eq2 = MathTex(r"{{ a^2 }} = {{ c^2 }} - {{ b^2 }}")

self.play(Write(eq1))
self.wait(0.5)
self.play(
    TransformMatchingTex(
        eq1,
        eq2,
        key_map={"+": "-"},       # Morph '+' directly into '-' instead of cross-fading!
        path_arc=90 * DEGREES,
    )
)
```
> [!TIP]
> **Whitespace Rule for `{{`**: Manim only treats `{{` as a split opener at index 0 or right after whitespace. Thus `r"\frac{{{n}}}{k}"` or `r"x^{{2}}"` will **not** split accidentally; if you *want* to split inside braces, add spaces: `r"x^{ {{2}} }"`.

---

## 4. Syntax-Highlighted Source Code (`Code`, Rewritten in v0.19/v0.21)

> [!WARNING]
> Legacy parameters `file_name`, `code`, `style`, `font`, `insert_line_no`, `margin`, and `paragraph_config={"color": ...}` **do NOT exist or are ignored** in modern ManimCE!

```python
snippet = '''def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
    return -1'''

code_mob = Code(
    code_string=snippet,                     # Or code_file="algo.py"
    language="python",                       # Always specify explicitly!
    formatter_style="monokai",               # Inspect all via Code.get_styles_list()
    tab_width=4,
    add_line_numbers=True,
    line_numbers_from=1,
    background="window",                     # "rectangle" (default) or macOS-style "window"
    background_config={"stroke_color": GRAY_C},
    paragraph_config={"font": "Consolas"},   # Font family/line_spacing ONLY; colors come from formatter_style!
).scale(0.8)
```

---

## 5. Dynamic Numbers (`DecimalNumber`, `Integer`, `Variable`)

```python
# Live "x = 2.00" readout backed by an internal ValueTracker (x_var.tracker):
x_var = Variable(2.0, r"x", num_decimal_places=2)
fx_var = Variable(4.0, r"x^2", num_decimal_places=2)
VGroup(x_var, fx_var).arrange(DOWN, aligned_edge=LEFT).to_corner(UL)

fx_var.add_updater(lambda v: v.tracker.set_value(x_var.tracker.get_value() ** 2))

self.add(x_var, fx_var)
self.play(x_var.tracker.animate.set_value(5.0), run_time=2.5, rate_func=linear)
```

---

## 6. Advanced Recipes (`TexTemplate`, `index_labels`, Custom Pygments Styles, Code Line Highlighting)

Load [latex-typst-code-recipes.md](./references/latex-typst-code-recipes.md) for custom LaTeX preambles (`mathscr`, `physics`, `tikz`, `ctex`), `TexFontTemplates`, `index_labels()` glyph debugging, custom Pygments `Style` classes for `Code`, and animated line-by-line code walkthroughs.
