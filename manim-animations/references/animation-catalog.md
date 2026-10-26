# Built-in Animation Catalog & Custom Animation Reference

## 1. Creation & Removal (`manim.animation.creation`)
- `Create(vmobject, lag_ratio=1.0, introducer=True)` — Draws stroke paths progressively, then fills. *(Replaces legacy `ShowCreation`.)*
- `Uncreate(vmobject, reverse_rate_function=True, remover=True)` — Reverses `Create` and removes from scene.
- `DrawBorderThenFill(vmobject, run_time=2, stroke_width=2)` — Outlines border first, then fades in fill.
- `Write(vmobject)` / `Unwrite(vmobject)` — Tuned stroke+fill reveal ideal for `Text`, `Tex`, `MathTex`, `Typst`.
- `SpiralIn(shapes, scale_factor=2, fade_in_fraction=0.3)` — Spirals submobjects inward into place.
- `ShowPartial(vmobject)` / `ShowIncreasingSubsets(group)` / `ShowSubmobjectsOneByOne(group)`
- **Typing / Terminal Effects**:
  - `AddTextLetterByLetter(text, time_per_char=0.1)` / `RemoveTextLetterByLetter(...)`
  - `AddTextWordByWord(text_mobject, run_time=..., time_per_char=0.06)`
  - `TypeWithCursor(text, cursor, buff=0.1, time_per_char=0.1, leave_cursor_on=True)` *(v0.19+)*
  - `UntypeWithCursor(text, cursor, ...)` *(v0.19+)*
- `Add(mobject)` *(v0.19+)* — Instantaneous zero-duration introducer (`run_time=0`) usable inside `Succession`!

## 2. Fading (`manim.animation.fading`)
- `FadeIn(mobject, shift=ORIGIN, target_position=None, scale=1)`
  - Examples: `FadeIn(title, shift=DOWN * 0.4)`, `FadeIn(badge, scale=0.8)`, `FadeIn(note, target_position=source_dot)`
- `FadeOut(mobject, shift=ORIGIN, target_position=None, scale=1)`

## 3. Growing (`manim.animation.growing`)
- `GrowFromCenter(mobject, point_color=None)`
- `GrowFromEdge(mobject, edge=DOWN)` (great for bar-chart bars: `GrowFromEdge(bar, DOWN)`)
- `GrowFromPoint(mobject, point, point_color=None)`
- `GrowArrow(arrow)` — Grows an `Arrow` or `Vector` cleanly from its tail `get_start()` to its tip!
- `SpinInFromNothing(mobject, angle=PI / 2, point_color=None)`

## 4. Indication & Attention (`manim.animation.indication`)
Use these to guide viewer focus without permanently altering the mobject:
- `Indicate(mobject, scale_factor=1.2, color=YELLOW)` — Scales up & flashes color briefly, then returns.
- `Circumscribe(mobject, shape=Rectangle, fade_in=False, fade_out=False, time_width=0.3, color=YELLOW, buff=SMALL_BUFF)` — Draws a temporary glowing outline (`Rectangle` or `Circle`) around `mobject`.
- `Flash(point_or_mob, line_length=0.2, num_lines=12, color=YELLOW, flash_radius=0.1)` — Radial burst of lines.
- `ShowPassingFlash(vmobject, time_width=0.1)` — Sends a bright traveling pulse along `vmobject` (copy + color first: `ShowPassingFlash(box.copy().set_color(YELLOW), time_width=0.4)`).
- `FocusOn(point_or_mob, opacity=0.2, color=GRAY)` — Shrinking spotlight circle converging onto target.
- `ApplyWave(mobject, direction=UP, amplitude=0.2)` — Sends a sine-wave ripple across `mobject`.
- `Wiggle(mobject, scale_value=1.1, rotation_angle=0.01 * TAU, n_wiggles=6)` — Shakes mobject for emphasis.
- `Blink(mobject, time_on=0.5, time_off=0.5, blinks=1)` — Cursor-style blinking.
- `Broadcast(mobject, focal_point=ORIGIN, n_mobs=5)` (`manim.animation.specialized`) — Expanding concentric wave rings.

## 5. Movement, Rotation, Numbers & Boundary Tracing
- **Movement (`manim.animation.movement`)**:
  - `MoveAlongPath(mobject, path, suspend_mobject_updating=False)`
  - `Homotopy(homotopy_fn, mobject)` where `homotopy_fn(x, y, z, t) -> (x', y', z')` for `t ∈ [0, 1]`
  - `ComplexHomotopy(complex_homotopy_fn, mobject)` where `fn(z: complex, t: float) -> complex`
  - `PhaseFlow(function, mobject, virtual_time=1)` — Flows points along a vector field `function(point) -> vector`
- **Rotation (`manim.animation.rotation`)**:
  - `Rotate(mobject, angle=PI, axis=OUT, about_point=None, about_edge=None)`
  - `Rotating(mobject, axis=OUT, radians=TAU, about_point=None, run_time=5, rate_func=linear)`
- **Pointwise / Matrix Transforms (`manim.animation.transform`)**:
  - `ApplyMatrix(matrix, mobject, about_point=ORIGIN)`
  - `ApplyFunction(fn, mobject)` / `ApplyComplexFunction(fn, mobject)`
  - `CyclicReplace(*mobjects)` / `Swap(*mobjects)` (accepts unpacked args or a single `Group`/`VGroup` since v0.21)
  - `ClockwiseTransform(a, b)` / `CounterclockwiseTransform(a, b)` (curved path transforms)
  - `ScaleInPlace(mobject, scale_factor)` / `ShrinkToCenter(mobject)`
- **Numbers (`manim.animation.numbers`)**:
  - `ChangeDecimalToValue(decimal_mob, target_number)`
  - `ChangingDecimal(decimal_mob, number_update_func)` where `number_update_func(alpha) -> float`
- **Boundary & Path Tracing (`manim.animation.changing`)**:
  - `TracedPath(traced_point_func, stroke_width=2, stroke_color=WHITE, dissipating_time=None)`:
    ```python
    dot = Dot(RIGHT * 2)
    # dissipating_time=0.8 creates a comet-tail trail!
    trail = TracedPath(dot.get_center, stroke_color=YELLOW, stroke_width=4, dissipating_time=0.8)
    self.add(trail, dot)
    self.play(Rotate(dot, angle=TAU, about_point=ORIGIN, run_time=3, rate_func=linear))
    ```
  - `AnimatedBoundary(vmobject, colors=[BLUE_B, BLUE_E, TEAL], cycle_rate=0.5)` — Continuously cycling neon border!

## 6. Updater Utilities (`manim.animation.updaters`)
- `UpdateFromFunc(mobject, update_function)` — Runs `update_function(mobject)` during a `self.play()` call without permanently attaching an updater.
- `UpdateFromAlphaFunc(mobject, update_function)` — Runs `update_function(mobject, alpha)` with `alpha ∈ [0, 1]` (already passed through `rate_func`) during `self.play()`.
- `always_rotate(mobject, rate=20 * DEGREES, **rotate_kwargs)`
- `always_shift(mobject, direction=RIGHT, rate=0.5)`
- `f_always(mob.set_x, tracker.get_value)` — Calls `mob.set_x(tracker.get_value())` every frame without lambda allocation overhead.
- `turn_animation_into_updater(Write(title, run_time=1.5), cycle=False, delay=0.2)` — Drives any `Animation` asynchronously via updaters while other `self.play()` calls run!
- `cycle_animation(Indicate(badge))` — Loops an animation continuously in the background.

---

## 7. Writing Custom `Animation` Classes & `@override_animation`

### Custom `Animation` Subclass
Override `interpolate_mobject(self, alpha: float)` and **explicitly apply `self.rate_func(alpha)`**:

```python
class Count(Animation):
    def __init__(self, number: DecimalNumber, start: float, end: float, **kwargs) -> None:
        super().__init__(number, **kwargs)
        self.start = start
        self.end = end

    def interpolate_mobject(self, alpha: float) -> None:
        progress = self.rate_func(alpha)
        value = self.start + progress * (self.end - self.start)
        self.mobject.set_value(value)
```
*(If you instead need an unmodified copy of `self.mobject` as reference at each frame—e.g. geometric deformation—override `interpolate_submobject(self, submob, starting_submob, alpha)` where `alpha` has already been mapped by `self.rate_func`, or read `self.starting_mobject` created during `begin()`.)*

### Customizing Built-in Animations for Custom Mobjects (`@override_animation`)
```python
class NodeCard(VGroup):
    def __init__(self, label: str, **kwargs):
        super().__init__(**kwargs)
        self.box = RoundedRectangle(corner_radius=0.15, width=2.2, height=1.0, fill_opacity=0.2, color=BLUE)
        self.txt = Text(label, font_size=28).move_to(self.box)
        self.add(self.box, self.txt)

    @override_animation(Create)
    def _create_override(self, **kwargs):
        return AnimationGroup(
            DrawBorderThenFill(self.box),
            FadeIn(self.txt, shift=UP * 0.15),
            lag_ratio=0.4,
            **kwargs,
        )
```
Calling `self.play(Create(NodeCard("API")))` now automatically plays `_create_override`!
