# Geometry, Annotations, Tables, Matrices, Graphs & Media Reference

## 1. Geometric Shapes (`manim.mobject.geometry`)

### Arcs & Circles
- `Dot(point=ORIGIN, radius=0.08, color=WHITE)`
- `AnnotationDot(radius=0.104, stroke_width=5, stroke_color=WHITE, fill_color=BLUE)`
- `Circle(radius=1.0, color=RED, **kwargs)`
- `Ellipse(width=2.0, height=1.0, **kwargs)`
- `Arc(radius=1.0, start_angle=0, angle=TAU / 4, num_components=9, arc_center=ORIGIN)`
- `ArcBetweenPoints(start, end, angle=TAU / 4, radius=None)`
- `CurvedArrow(start_point, end_point, angle=TAU / 4)` / `CurvedDoubleArrow(...)`
- `Annulus(inner_radius=1.0, outer_radius=2.0, fill_opacity=1.0)`
- `Sector(radius=1.0, angle=TAU / 4, start_angle=0)` *(Note: `inner_radius`/`outer_radius` were removed from `Sector` in v0.19; use `AnnularSector` below for ring sectors)*
- `AnnularSector(inner_radius=1.0, outer_radius=2.0, angle=TAU / 4, start_angle=0)`

### Lines, Rays, Arrows & Angles
- `Line(start=LEFT, end=RIGHT, buff=0, path_arc=None)` (`buff > 0` shrinks endpoints inward!)
- `DashedLine(start=LEFT, end=RIGHT, dash_length=0.05, dashed_ratio=0.5)`
- `DashedVMobject(vmobject, num_dashes=15, dashed_ratio=0.5)` (turns any curve/circle/polygon dashed!)
- `TangentLine(vmob, alpha=0.5, length=1, d_alpha=1e-6)`
- `Elbow(width=0.2, angle=0)`
- `Arrow(start=LEFT, end=RIGHT, buff=MED_SMALL_BUFF, stroke_width=6, max_tip_length_to_length_ratio=0.25)`
  *(Tip: Pass `buff=0` when connecting exact coordinates like `Arrow(ORIGIN, [2, 2, 0], buff=0)`!)*
- `Vector(direction=RIGHT, buff=0)` (convenience `Arrow` starting at `ORIGIN` with `buff=0`)
- `DoubleArrow(start, end, ...)`
- `Angle(line1, line2, radius=None, quadrant=(1, 1), other_angle=False, dot=False)`
- `RightAngle(line1, line2, length=None, quadrant=(1, 1))`

### Polygons & Polygrams
- `Polygon(*vertices)` (e.g., `Polygon([-1, 0, 0], [1, 0, 0], [0, 1.5, 0])`)
- `RegularPolygon(n=6, start_angle=None, **kwargs)`
- `Triangle(**kwargs)` (equilateral triangle inscribed in unit circle)
- `Rectangle(color=WHITE, height=2.0, width=4.0, grid_xstep=None, grid_ystep=None)`
- `Square(side_length=2.0, **kwargs)` (`sq.side_length` is a dynamic property)
- `RoundedRectangle(corner_radius=0.5, height=2.0, width=4.0)`
- `Star(n=5, outer_radius=1, inner_radius=None, density=2)`
- `Cutout(main_shape, *mobjects)` (punches holes `*mobjects` out of `main_shape`!)
- `ConvexHull(*points)` / `ConvexHull3D(*points)` (v0.19+)
- `Polygram(*vertex_groups)` -> `.round_corners(radius=0.2)` rounds vertices of any polygon!

### 2D Boolean Set Operations (`manim.mobject.geometry.boolean_ops`)
```python
a = Circle(radius=1.2).shift(LEFT * 0.6)
b = Circle(radius=1.2).shift(RIGHT * 0.6)

u = Union(a, b, color=ORANGE, fill_opacity=0.6)
i = Intersection(a, b, color=GREEN, fill_opacity=0.6)
d = Difference(a, b, color=PINK, fill_opacity=0.6)      # a minus b
e = Exclusion(a, b, color=YELLOW, fill_opacity=0.6)     # symmetric difference (XOR)
```

---

## 2. Shape Matchers, Braces & Callouts

> [!WARNING]
> Since Manim v0.19, `SurroundingRectangle` accepts `*mobjects` variadically! Positional `color` or `buff` arguments (`SurroundingRectangle(mob, RED, 0.2)`) **raise `TypeError`**. Always use keyword arguments:

```python
# Highlighting one or multiple mobjects:
box = SurroundingRectangle(eq[1], eq[3], color=YELLOW, buff=0.15, corner_radius=0.1)
bg = BackgroundRectangle(mob, color=BLACK, fill_opacity=0.75, buff=0.1)
cross = Cross(mob, stroke_color=RED, stroke_width=6)
underline = Underline(title_mob, buff=SMALL_BUFF, color=BLUE)

# Braces:
brace = Brace(line_or_group, direction=DOWN, buff=0.15)
label_txt = brace.get_text("Width")       # Pango Text/Tex helper
label_tex = brace.get_tex(r"\Delta x")    # MathTex helper

# Rotated brace along an angled line:
normal_dir = line.copy().rotate(PI / 2).get_unit_vector()
angled_brace = Brace(line, direction=normal_dir)

# Brace between explicit points:
brace_pts = BraceBetweenPoints([-2, -1, 0], [2, -1, 0], direction=DOWN)
arc_brace = ArcBrace(arc_mob, direction=RIGHT)
brace_lbl = BraceLabel(mob, r"n \text{ items}", brace_direction=DOWN)
```

---

## 3. Tables (`Table`, `MathTable`, `MobjectTable`, `IntegerTable`, `DecimalTable`)

```python
t = Table(
    [["O(1)", "O(n)"], ["O(log n)", "O(n log n)"]],
    row_labels=[Text("Hash Map"), Text("Balanced BST")],
    col_labels=[Text("Average"), Text("Worst Case")],
    top_left_entry=Text("Structure", color=GRAY_B),
    include_outer_lines=True,
    include_inner_lines=True,          # Can be False (v0.21+) to omit inner grid lines
    v_buff=0.6,
    h_buff=1.1,
    line_config={"stroke_width": 2, "color": GRAY_C},
    arrange_in_grid_config={"cell_alignment": ORIGIN},
).scale(0.65)

# Note: Table cell positions (row, col) are 1-INDEXED (including label row/col if present)!
t.add_highlighted_cell((2, 2), color=GREEN_E)
cell_outline = t.get_cell((3, 3), color=YELLOW)

# Progressive table creation animation:
self.play(t.create())
```

Specialized subclasses change `element_to_mobject` automatically:
- `Table` -> `Paragraph` (Pango text)
- `MathTable` -> `MathTex` (LaTeX math mode)
- `IntegerTable` / `DecimalTable` -> `Integer` / `DecimalNumber`
- `MobjectTable` -> expects pre-built `VMobject` instances in every cell

Useful accessors: `t.get_rows()`, `t.get_columns()`, `t.get_entries(pos=None)`, `t.get_entries_without_labels()`, `t.get_horizontal_lines()`, `t.get_vertical_lines()`, `t.set_row_colors(...)`, `t.set_column_colors(...)`.

---

## 4. Matrices (`Matrix`, `DecimalMatrix`, `IntegerMatrix`, `MobjectMatrix`)

```python
m = Matrix(
    [[1, r"\lambda"], [0, 1]],
    v_buff=0.8,
    h_buff=1.2,
    left_bracket="(",
    right_bracket=")",          # Also "[", r"\{", "|", r"\langle"
)
m.set_column_colors(GREEN, RED)

# Highlighting a column or entry:
col_box = SurroundingRectangle(m.get_columns()[1], color=YELLOW, buff=0.15)
entry_01 = m.get_entries()[1]   # Flat VGroup of entries (row-major)
rows = m.get_rows()             # VGroup of row VGroups
brackets = m.get_brackets()
```
*(Note: Default `Matrix` uses `MathTex` and requires LaTeX. Without LaTeX, pass `element_to_mobject=Text` or use `MobjectMatrix`!)*

---

## 5. Network / Graph Theory (`Graph` & `DiGraph`)

`Graph` (undirected) and `DiGraph` (directed arrows) include built-in updaters so edges automatically follow moving vertices!

```python
vertices = ["s", "a", "b", "t"]
edges = [("s", "a"), ("s", "b"), ("a", "b"), ("a", "t"), ("b", "t")]

g = DiGraph(
    vertices,
    edges,
    labels=True,                      # True (MathTex), False, or dict {v: Text(...)}
    layout="kamada_kawai",            # "spring", "circular", "kamada_kawai", "planar", "tree", "partite", "shell", "spiral", or manual dict {v: [x, y, 0]}
    layout_scale=2.5,
    vertex_config={"s": {"fill_color": GREEN}, "t": {"fill_color": RED}},
    edge_config={("a", "t"): {"stroke_color": YELLOW}},
)

self.play(Create(g))
# Index vertices with g[v] and edges with tuple g[(u, v)] (v0.21+):
self.play(
    g["a"].animate.shift(UP * 0.5),
    Indicate(g[("a", "t")], color=YELLOW),
)
```
- **Tree layout**: `Graph(V, E, layout="tree", root_vertex=0, layout_config={"vertex_spacing": (1.5, 1.2)})`
- **Neural network / bipartite layout**: `Graph(V, E, layout="partite", partitions=[layer0, layer1, layer2])`
- Dynamic mutations: `g.add_vertices(...)`, `g.remove_vertices(...)`, `g.add_edges(...)`, `g.remove_edges(...)`, `g.change_layout("circular")` (animatable via `self.play(g.animate.change_layout("circular"))`!).

---

## 6. External Assets: `SVGMobject` & `ImageMobject`

```python
# Vector SVG (sub-paths accessible via indexing svg[0], svg[1], ...):
icon = SVGMobject("assets/icon.svg", height=2.0)

# Raster PNG/JPEG or uint8 NumPy array:
photo = ImageMobject("assets/diagram.png").scale_to_fit_height(4.0)
photo.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bicubic"])  # nearest, bilinear, bicubic
frame = SurroundingRectangle(photo, color=WHITE, buff=0)
photo_card = Group(photo, frame)   # Use Group, NOT VGroup!
self.play(FadeIn(photo_card))
```
