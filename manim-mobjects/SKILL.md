---
name: manim-mobjects
description: >-
  Create, position, align, group, style, and color Manim Mobjects and VMobjects,
  including geometric shapes, arrows, braces, boolean operations, VGroup/Group
  grid layouts, SVGs, images, Tables, Matrices, and Graph/DiGraph networks.
version: 0.22.0
---

# Mobjects, Positioning, Grouping, Styling & Structured Visuals

Use this skill whenever constructing visual elements, arranging layouts without overlap, styling strokes/fills/colors, or building structured diagrams (`Table`, `Matrix`, `Graph`, `SVGMobject`, `ImageMobject`). See [manim-best-practices](../manim-best-practices/SKILL.md) for other topics.

## 1. Mobject Hierarchy & Crucial Distinctions

- **`Mobject`**: Abstract base class (`points` array, `submobjects` tree, bounding box, `z_index`). Plain `Mobject()` renders nothing on screen.
- **`VMobject` (Vectorized Mobject)**: Almost all shapes, text, LaTeX, Typst, graphs, and SVG imports inherit from `VMobject`. Stores cubic Bézier curves as quadruples of 3D points (`[anchor1, handle1, handle2, anchor2]`). Supports `.set_fill()` and `.set_stroke()`.
- **`ImageMobject`**: Raster image / `uint8` NumPy pixel array (`(H, W)` grayscale, `(H, W, 3)` RGB, or `(H, W, 4)` RGBA). **Not** a `VMobject`!
- **`VGroup` vs `Group`**:
  - **`VGroup(*vmobjects)`**: Container for **`VMobject` instances only** (supports generators since v0.19: `VGroup(Dot() for _ in range(8))`). Propagates `.set_fill()`, `.set_stroke()`, and vector animations (`Create`, `Write`).
  - **`Group(*mobjects)`**: Required whenever grouping mixed mobject types (e.g., an `ImageMobject` or `Surface` alongside `Text` or `SurroundingRectangle`). Passing an `ImageMobject` to `VGroup` raises `TypeError`!

---

## 2. Positioning, Alignment & Layout (Zero-Overlap Patterns)

Most `Mobject` methods mutate `self` in-place **and** return `self` for fluent method chaining (`Square().scale(0.8).to_edge(UP)`).

### Absolute & Relative Placement
```python
mob.move_to(ORIGIN)                       # Center at [0, 0, 0] (or another mobject's center)
mob.move_to([2, -1, 0], aligned_edge=UL)  # Place mob's UL corner at [2, -1, 0]
mob.shift(2 * RIGHT + 0.5 * UP)           # Relative translation
mob.next_to(ref_mob, DOWN, buff=0.35, aligned_edge=LEFT)  # Place below ref_mob, left-aligned
mob.align_to(ref_mob, UP)                 # Match top bounding-box border with ref_mob's top
mob.to_edge(LEFT, buff=0.5)               # Snap to screen edge (default buff=0.5)
mob.to_corner(UR, buff=0.5)               # Snap to UL, UR, DL, or DR screen corner
```

### Automatic Group Layouts (`arrange` & `arrange_in_grid`)
Prefer `arrange()` and `arrange_in_grid()` over manual coordinate arithmetic:

```python
# Vertical left-aligned bullet/equation stack:
stack = VGroup(line1, line2, line3).arrange(DOWN, buff=0.35, aligned_edge=LEFT)

# Structured grid layout:
cards = VGroup( Square(side_length=1.2) for _ in range(6) )
cards.arrange_in_grid(
    rows=2,
    cols=3,
    buff=(0.6, 0.5),             # (col_buff, row_buff) or single float
    cell_alignment=ORIGIN,       # Align items inside cells (e.g., LEFT, UP, ORIGIN)
    flow_order="rd",             # "rd" (right-then-down), "dr" (down-then-right), etc.
)
```

### Sizing & Matching Another Mobject
```python
mob.scale(0.75)                          # Uniform scale (pass scale_stroke=True on VMobject to scale stroke width too)
mob.scale_to_fit_width(5.0)              # Proportional resize to target width (or: mob.width = 5.0)
mob.scale_to_fit_height(3.0)             # Proportional resize to target height (or: mob.height = 3.0)
mob.stretch_to_fit_width(5.0)            # Non-proportional horizontal stretch
mob.match_width(other_mob)               # Also: match_height, match_x, match_y, match_color, match_points
```

### Querying Anchors & Coordinates
- Bounding box points: `mob.get_center()`, `mob.get_top()`, `mob.get_bottom()`, `mob.get_left()`, `mob.get_right()`, `mob.get_corner(UL)`, `mob.get_edge_center(RIGHT)`
- Scalar coordinates: `mob.get_x()`, `mob.get_y()`, `mob.get_z()` (setters: `mob.set_x(2.0)`, `mob.set_y(-1.0)`)
- Curve endpoints & arc-length sampling (`VMobject`):
  - `line.get_start()`, `line.get_end()`, `line.get_midpoint()`, `line.get_unit_vector()`
  - `curve.point_from_proportion(0.25)` -> 3D point 25% along the path (`0.0` to `1.0`)

---

## 3. Styling, Draw Order & Scene Bookkeeping

### Stroke, Fill, Background Stroke & Gradients
> [!IMPORTANT]
> Geometric shapes (`Circle`, `Square`, `Rectangle`, `Polygon`) default to **`fill_opacity=0.0`**! Passing `color=BLUE` colors both stroke and fill, **but fill remains invisible until `fill_opacity > 0`**.

```python
box = RoundedRectangle(
    corner_radius=0.2,
    width=4,
    height=2,
    stroke_color=BLUE_B,
    stroke_width=4,          # Default stroke_width is 4
    fill_color=BLUE_E,
    fill_opacity=0.85,
)

# Readable text/shapes over busy grids or vector fields:
label.set_stroke(background=True, color=BLACK, width=8, opacity=0.9)
# Or attach a semi-transparent backing box:
label.add_background_rectangle(color=BLACK, opacity=0.75, buff=0.12)

# Color gradients:
bar.set_color_by_gradient(BLUE, TEAL, GREEN)
```

### Z-Order & The `Scene.restructure_mobjects` Gotcha
1. **Default painter's order**: `self.add(back_mob, middle_mob, front_mob)` draws left-to-right (back-to-front).
2. **Explicit `z_index` (Recommended for complex scenes)**: `dot.set_z_index(10)` keeps `dot` above `z_index=0` grid/polygons regardless of `self.add` or `self.play` order!
3. **Foreground lock**: `self.add_foreground_mobject(hud)` pins `hud` permanently above regular mobjects.
4. **Group Disbanding Gotcha**: If `group = VGroup(a, b)` is in the scene and you call `self.remove(a)` (or re-`add(a)` at top level), Manim's `restructure_mobjects` **disbands `group`** and promotes `b` to top-level `self.mobjects`. To keep `group` intact, mutate the group directly (`group.remove(a)`).

### Class-Wide Defaults (`set_default`)
Set consistent typography or stroke styles across an entire scene or module:
```python
Text.set_default(font="Inter", font_size=32)
MathTex.set_default(color=YELLOW_A)
# Reset later if needed: Text.set_default()
```

---

## 4. State Snapshots (`save_state` & `become`)

```python
mob.save_state()                       # Saves copy of points, position, size, and style
# ... mutate or animate mob ...
self.play(Restore(mob))                # Smoothly animates back to saved state (or mob.restore() instantly)

mob.become(other_mob)                  # Instantly copies points, submobjects, AND style of other_mob
mob.match_points(other_mob)            # Copies geometry/position while keeping mob's current style
```

---

## 5. Detailed Catalogs & Reference Manuals

- **Geometric Shapes, Arrows, Braces, Boolean Ops, `SurroundingRectangle`, `Table`, `Matrix`, `Graph`/`DiGraph`, `SVGMobject`, and `ImageMobject`**: Load [geometry-and-data-mobjects.md](./references/geometry-and-data-mobjects.md).
- **Predefined Colors (`manim_colors`, `DVIPSNAMES`, `SVGNAMES`), `ManimColor`/`HSV` APIs, Direction Vectors, Buffers, and Angles**: Load [colors-and-constants.md](./references/colors-and-constants.md).
