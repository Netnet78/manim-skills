# Plotting, Special Coordinate Planes, `ZoomedScene` & 3D Primitives Reference

## 1. Specialized Coordinate Systems

### `NumberLine` & `UnitInterval`
```python
nl = NumberLine(
    x_range=[-4, 4, 1],
    length=10,
    include_numbers=True,
    include_tip=True,
    label_direction=DOWN,
)
pt = nl.n2p(2.5)          # number_to_point (alias n2p); inverse is nl.p2n(point)
```

### `PolarPlane`
```python
polar = PolarPlane(radius_max=3.0, size=6, azimuth_units="PI radians")
rose = polar.plot_polar_graph(lambda theta: 2 * np.cos(3 * theta), [0, PI], color=ORANGE)
pt = polar.pr2pt(2.0, PI / 4)   # polar_to_point(radius, azimuth); inverse is pt2pr
```

### `ComplexPlane`
```python
cplane = ComplexPlane().add_coordinates()
z_dot = Dot(cplane.n2p(2 + 1j), color=YELLOW)
# Animate holomorphic map z -> z^2:
cplane.prepare_for_nonlinear_transform()
self.play(cplane.animate.apply_complex_function(lambda z: z**2), run_time=3)
```

### Implicit Curves & Secant Slope Groups on `Axes`
```python
# Implicit equation f(x, y) = 0 (e.g., elliptic curve y^2 - x^3 + x = 0):
elliptic = ax.plot_implicit_curve(lambda x, y: y**2 - x**3 + x, color=PINK)

# Animated derivative secant -> tangent visualization:
dx_tracker = ValueTracker(2.0)
secant = always_redraw(
    lambda: ax.get_secant_slope_group(
        x=1.0,
        graph=curve,
        dx=dx_tracker.get_value(),
        dx_label="dx",
        df_label="dy",
        dx_line_color=YELLOW,
        df_line_color=ORANGE,
        secant_line_color=GREEN,
        secant_line_length=6,
    )
)
self.add(secant)
self.play(dx_tracker.animate.set_value(0.01), run_time=3)
```

---

## 2. Animated `BarChart`

```python
chart = BarChart(
    values=[15, 40, 28, 62],
    bar_names=["Q1", "Q2", "Q3", "Q4"],
    y_range=[0, 80, 20],
    y_length=5,
    x_length=7,
    bar_colors=[BLUE_D, TEAL_D, GREEN_D, YELLOW_D],
    y_axis_config={"include_numbers": True},
)
bar_lbls = chart.get_bar_labels(font_size=24)
self.play(Create(chart), FadeIn(bar_lbls))

# Animate bar heights changing to new values:
self.play(chart.animate.change_bar_values([32, 55, 48, 75]), run_time=1.5)
```

---

## 3. Picture-in-Picture Magnifier (`ZoomedScene`)

```python
class MagnifierDemo(ZoomedScene):
    def __init__(self, **kwargs):
        super().__init__(
            zoom_factor=0.25,
            zoomed_display_height=2.5,
            zoomed_display_width=4.0,
            image_frame_stroke_width=6,
            zoomed_camera_config={"default_frame_stroke_width": 2},
            **kwargs,
        )

    def construct(self):
        ax = Axes(x_range=[-3, 3], y_range=[-2, 2])
        curve = ax.plot(lambda x: x * np.sin(1 / x) if x != 0 else 0, x_range=[-2, 2, 0.002], color=BLUE)
        self.add(ax, curve)

        frame = self.zoomed_camera.frame
        display = self.zoomed_display
        frame.move_to(ax @ (0, 0)).set_color(YELLOW)
        display.to_corner(UR)
        display.display_frame.set_color(YELLOW)

        self.play(Create(frame))
        self.activate_zooming()
        self.play(self.get_zoomed_display_pop_out_animation())
        self.play(frame.animate.shift(RIGHT * 0.4), run_time=2)
        self.wait()
```

---

## 4. 3D Primitives, Polyhedra, Lighting & Billboard Labels

### Built-in 3D Mobjects (`manim.mobject.three_d`)
- **Curved / Volumetric**:
  - `Sphere(center=ORIGIN, radius=1, resolution=(24, 24), u_range=[0, TAU], v_range=[0, PI])`
  - `Cube(side_length=2, fill_opacity=0.75, fill_color=BLUE, stroke_width=1)`
  - `Prism(dimensions=[3, 2, 1])`
  - `Cylinder(radius=1, height=2, direction=Z_AXIS, show_ends=True)`
  - `Cone(base_radius=1, height=2, direction=Z_AXIS, show_base=True)`
  - `Torus(major_radius=2, minor_radius=0.5)`
  - `Dot3D(point=ORIGIN, radius=0.08, color=WHITE)`
  - `Line3D(start=ORIGIN, end=[2, 2, 2], thickness=0.02)`
  - `Arrow3D(start=ORIGIN, end=[2, 1, 2], thickness=0.02, height=0.3, base_radius=0.08)`
- **Platonic Polyhedra (`manim.mobject.three_d.polyhedra`)**:
  - `Tetrahedron(edge_length=2)`, `Octahedron(edge_length=2)`, `Icosahedron(edge_length=2)`, `Dodecahedron(edge_length=2)`
  - Custom `Polyhedron(vertex_coords, faces_list)` (access `.graph` and `.faces` directly!)

### 3D Text Modes & Light Source Control
- **`self.add_fixed_in_frame_mobjects(mob)`**: Pins `mob` in 2D screen overlay coordinates (unaffected by 3D camera orbit, pan, or zoom — ideal for titles, equations, legends).
- **`self.add_fixed_orientation_mobjects(mob)`**: Keeps `mob` positioned at its `(x, y, z)` 3D world point (e.g., next to a 3D vector tip), while automatically rotating `mob` so it always faces the camera head-on!
- **Moving the 3D light source (Cairo `ThreeDCamera`)**:
  ```python
  self.renderer.camera.light_source.move_to(3 * IN + 4 * UP + 2 * RIGHT)
  ```
