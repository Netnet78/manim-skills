---
name: manim-math-3d
description: >-
  Plot 2D/3D functions, calculus areas, Riemann sums, bar charts, linear
  transformations, and vector fields; animate camera pan/zoom/PiP with
  MovingCameraScene and ZoomedScene; and build 3D scenes with ThreeDScene.
version: 0.22.0
---

# Plotting, Coordinate Systems, Vector Fields, Cameras & 3D Scenes

Use this skill for mathematical graphing (`Axes`, `NumberPlane`, `PolarPlane`, `ComplexPlane`, `BarChart`), calculus visuals, linear algebra (`LinearTransformationScene`), vector fields (`ArrowVectorField`, `StreamLines`), camera choreography (`MovingCameraScene`, `ZoomedScene`), and 3D scenes (`ThreeDScene`, `ThreeDAxes`, `Surface`). See [manim-best-practices](../manim-best-practices/SKILL.md) for other topics.

## 1. 2D Coordinate Systems & Function Plotting (`Axes`)

> [!IMPORTANT]
> **Scene Coordinates vs Axis Coordinates**: Passing `[2, 3, 0]` to `Dot([2, 3, 0])` places the dot in **screen space**, NOT at `(2, 3)` on `ax`! Always convert via **`ax @ (2, 3)`** (v0.19+ shorthand) or **`ax.c2p(2, 3)`** (`coords_to_point`), and convert screen points back via `ax.p2c(point)` (`point_to_coords`).

```python
ax = Axes(
    x_range=[-1, 5, 1],            # [min, max, step]
    y_range=[-2, 6, 2],
    x_length=8,
    y_length=5,
    tips=False,
    axis_config={"include_numbers": True, "font_size": 24},
)
labels = ax.get_axis_labels(x_label="x", y_label="f(x)")

# Plot curve, tangent/vertical helper lines, Riemann sum, and bounded area:
curve = ax.plot(lambda x: 0.5 * x**2 - x + 1, x_range=[-0.5, 4.5], color=BLUE)
curve_lbl = ax.get_graph_label(curve, r"\frac{1}{2}x^2 - x + 1", x_val=4.0, direction=UL)

pt_dot = Dot(ax @ (3, 2.5), color=YELLOW)              # Equivalent to Dot(ax.c2p(3, 2.5))
on_curve_dot = Dot(ax.i2gp(3.0, curve), color=ORANGE)  # input_to_graph_point(x, graph)
v_line = ax.get_vertical_line(ax.i2gp(3.0, curve), color=GRAY_B)

riemann = ax.get_riemann_rectangles(
    curve, x_range=[0, 3], dx=0.25, color=(TEAL, BLUE), input_sample_type="left", fill_opacity=0.6
)
area = ax.get_area(curve, x_range=[1, 4], color=(BLUE_D, TEAL_D), opacity=0.5)
```

### Discontinuities & Sharp Corners in `ax.plot`
- **Asymptotes / jumps** (`1/x`, `tan(x)`, floor): pass `discontinuities=[0], dt=0.05` so Manim does not draw a vertical spike across the asymptote!
- **Piecewise / kinks** (`|x|`, ReLU): pass `use_smoothing=False` so corners stay sharp instead of overshooting with cubic splines.
- **Logarithmic axes**: pass `x_axis_config={"scaling": LogBase(custom_labels=True)}` (and specify `x_range=[min_exp, max_exp, step]` as powers of 10!).

### Non-Linear Grid Warping (`NumberPlane` / `ComplexPlane`)
Always call **`grid.prepare_for_nonlinear_transform()`** before applying curved functions so straight grid lines are subdivided into enough Bézier segments to bend smoothly:
```python
grid = NumberPlane()
grid.prepare_for_nonlinear_transform()
self.play(
    grid.animate.apply_function(lambda p: p + np.array([np.sin(p[1]), np.sin(p[0]), 0])),
    run_time=3,
)
```

---

## 2. Linear Transformations & Vector Fields

### `LinearTransformationScene`
```python
class ShearDemo(LinearTransformationScene):
    def __init__(self, **kwargs):
        super().__init__(
            show_coordinates=True,
            leave_ghost_vectors=True,
            include_background_plane=True,
            **kwargs,
        )

    def construct(self):
        v = self.add_vector([1, 2], color=YELLOW)
        self.add_unit_square(animate=True)
        self.apply_matrix([[1, 1], [0, 1]])
        self.wait()
```

### `ArrowVectorField` & Animated `StreamLines`
```python
field_fn = lambda pos: np.sin(pos[1]) * RIGHT + np.cos(pos[0]) * UP
vf = ArrowVectorField(field_fn, x_range=[-6, 6, 1], y_range=[-3.5, 3.5, 1])

streams = StreamLines(field_fn, stroke_width=2, max_anchors_per_line=30, virtual_time=2)
self.add(vf, streams)
streams.start_animation(warm_up=True, flow_speed=1.2)
self.wait(3)
self.play(streams.end_animation())
```

---

## 3. 2D Camera Pan, Zoom & Tracking (`MovingCameraScene`)

Inherit from **`MovingCameraScene`** (not `Scene`) to animate `self.camera.frame` just like any `Mobject`:

```python
class CameraTour(MovingCameraScene):
    def construct(self):
        self.camera.frame.save_state()     # Snapshot full-screen 14.22 x 8.0 view

        ax = Axes(x_range=[0, 10], y_range=[-2, 2])
        wave = ax.plot(np.sin, x_range=[0, 3 * PI], color=BLUE)
        dot = Dot(ax.i2gp(0, wave), color=YELLOW)
        self.add(ax, wave, dot)

        # Zoom in 2x (scale 0.5) and center on dot:
        self.play(self.camera.frame.animate.scale(0.5).move_to(dot))

        # Follow dot smoothly along curve:
        self.camera.frame.add_updater(lambda f: f.move_to(dot.get_center()))
        self.play(MoveAlongPath(dot, wave, run_time=3, rate_func=linear))
        self.camera.frame.clear_updaters()

        # Pull back to original view:
        self.play(Restore(self.camera.frame))
```

---

## 4. 3D Scenes, Surfaces & HUD Text (`ThreeDScene`)

Inherit from **`ThreeDScene`**. Camera orientation uses spherical angles:
- `phi`: polar tilt from `+Z` axis (`0` = top-down 2D view, `75 * DEGREES` = classic 3D view, `90 * DEGREES` = horizontal side view).
- `theta`: azimuth angle around `Z` axis (`-45 * DEGREES` views from front-right quadrant).
- `gamma`: roll angle; `zoom`: camera magnification factor.

```python
class SaddleSurface(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-4, 4])
        surface = Surface(
            lambda u, v: axes.c2p(u, v, 0.4 * (u**2 - v**2)),
            u_range=[-2.5, 2.5],
            v_range=[-2.5, 2.5],
            resolution=(28, 28),
        )
        surface.set_style(fill_opacity=0.75, stroke_color=BLUE_E, stroke_width=0.5)
        surface.set_fill_by_value(axes=axes, colorscale=[(BLUE, -2), (TEAL, 0), (YELLOW, 2)], axis=2)

        # Pin 2D HUD text to screen frame BEFORE playing Write() so it stays flat on screen!
        hud = MathTex(r"z = 0.4(x^2 - y^2)").to_corner(UL)
        self.add_fixed_in_frame_mobjects(hud)

        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        self.play(Create(axes), Create(surface), Write(hud))

        # Animate camera orbit:
        self.begin_ambient_camera_rotation(rate=0.25, about="theta")
        self.wait(3)
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=60 * DEGREES, theta=30 * DEGREES, zoom=1.2, run_time=1.5)
```

---

## 5. Complete Reference (`PolarPlane`, `ComplexPlane`, `BarChart`, `ZoomedScene`, 3D Solids)

Load [plotting-and-3d-reference.md](./references/plotting-and-3d-reference.md) for `PolarPlane`, `ComplexPlane`, `NumberLine`, `BarChart` animated updates, secant slope groups (`get_secant_slope_group`), picture-in-picture `ZoomedScene`, 3D primitives (`Sphere`, `Cube`, `Cylinder`, `Cone`, `Torus`, `Arrow3D`, Platonic polyhedra), and 3D billboard labels (`add_fixed_orientation_mobjects`).
