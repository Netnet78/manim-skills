---
name: manim-animations
description: >-
  Orchestrate Manim animations with Scene.play, .animate syntax, Transform vs
  ReplacementTransform, LaggedStart/Succession, rate_functions, ValueTracker,
  Mobject.always, updaters, always_redraw, and custom Animation classes.
version: 0.22.0
---

# Animations, Transforms, Composition, Rate Functions & Updaters

Use this skill when animating mobjects, sequencing or staggering animations, morphing shapes, tuning easing curves (`rate_functions`), driving continuous parameters with `ValueTracker` / updaters, or writing custom `Animation` classes. See [manim-best-practices](../manim-best-practices/SKILL.md) for other topics.

## 1. Playing Animations & `.animate` Syntax

Every animation runs inside `self.play(*animations, run_time=1.0, rate_func=smooth)` (default `run_time=1.0` second). Multiple animations in a single `self.play(...)` execute **simultaneously**:

```python
# Simultaneous animations with per-animation or shared timing:
self.play(
    Create(circle),
    FadeIn(label, shift=UP * 0.3),
    square.animate(rate_func=linear).shift(2 * RIGHT).set_fill(ORANGE, opacity=0.8),
    run_time=1.5,
)
self.wait(0.5)
```

### The `.animate` Quirk (When NOT to Use `.animate`)
`.animate` captures a mobject's **starting state** and **ending state** and linearly interpolates points between them.
- **Gotcha**: `self.play(square.animate.rotate(PI))` interpolates corners straight through the center (shrinking the square) or does nothing if 180° symmetric!
- **Fix**: Use dedicated path/angle animations when trajectory matters:
  - Rotation: `self.play(Rotate(square, angle=PI, about_point=ORIGIN))`
  - Curved translation: `self.play( s.animate(path_arc=PI / 2).move_to(RIGHT * 3) )` or `MoveAlongPath(dot, arc)`

---

## 2. Choosing the Right Transform

| Class | Scene Bookkeeping & Visual Behavior | When to Use |
| :--- | :--- | :--- |
| `Transform(a, b)` | Deforms **`a` in-place** to look like `b`. **`a` stays in `self.mobjects`; `b` is NOT in the scene!** Subsequent animations must still reference `a`! | Chaining multiple transforms on a single variable (`for t in targets: self.play(Transform(a, t))`). |
| `ReplacementTransform(a, b)` | Deforms `a` into `b`, then **removes `a` and adds `b`** to `self.mobjects`. Subsequent animations reference `b`. | Stepping cleanly from `step1_mob` -> `step2_mob` -> `step3_mob`. |
| `TransformFromCopy(a, b)` | Leaves `a` untouched on screen while animating a copy of `a` into `b` (adding `b` to scene). | Deriving a second equation/diagram below the original while keeping the original visible. |
| `FadeTransform(a, b)` | Cross-fades and translates `a` into `b` cleanly (replaces `a` with `b`). | Morphing between mobjects with very different topologies (e.g., `Text` <-> `Circle` or `ImageMobject`). |
| `MoveToTarget(a)` | Animates `a` into `a.target` after calling `a.generate_target()`. | Complex multi-step mutations on `a.target` where `.animate` chaining becomes unreadable. |
| `Restore(a)` | Animates `a` back to the snapshot saved via `a.save_state()`. | Temporary zoom-ins, highlights, or excursions that return to baseline. |
| `TransformMatchingShapes(a, b)` | Matches submobjects with identical normalized glyph shapes (`path_arc=...`, `transform_mismatches=...`). | Rearranging words/anagrams or geometric assemblies. *(For LaTeX equations, prefer `TransformMatchingTex` in [manim-text](../manim-text/SKILL.md).)* |

`MoveToTarget` pattern:
```python
card.generate_target()
card.target.scale(0.6).to_corner(UL).set_color(BLUE)
self.play(MoveToTarget(card))
```

*(Tip: If `Transform(square, circle)` twists awkwardly because vertex winding directions differ, align winding via `square.reverse_points()` or roll `square.points = np.roll(square.points, len(square.points) // 4, axis=0)`.)*

---

## 3. Composing & Choreographing Multiple Animations

```python
# Staggered cascade across submobjects (lag_ratio=0 -> simultaneous, lag_ratio=1 -> strictly sequential):
self.play(LaggedStart(*(FadeIn(item, shift=UP * 0.2) for item in items), lag_ratio=0.18))

# Concise map form over a VGroup:
self.play(LaggedStartMap(FadeIn, items, shift=UP * 0.2, lag_ratio=0.15))

# Strict back-to-back sequence inside a single play() call:
self.play(Succession(Create(arrow), Indicate(target_box), FadeOut(arrow)))

# Dynamic time-warping / slow-motion ramp:
self.play(
    ChangeSpeed(
        dot.animate(run_time=2).shift(RIGHT * 6),
        speedinfo={0.3: 1.0, 0.45: 0.15, 0.65: 0.15, 1.0: 1.0},
        rate_func=linear,
    )
)
```

---

## 4. Rate Functions (Easing Curves)

> [!WARNING]
> Standard CSS/Penner easings (`ease_in_sine`, `ease_out_cubic`, `ease_in_out_back`, `ease_out_bounce`, etc.) are **NOT** exported into global scope by `from manim import *`. Always prefix them with `rate_functions.`!

- **Directly available in `from manim import *`**:
  - `smooth` *(default S-curve)*, `double_smooth`
  - `linear` *(constant speed — always use for continuous rotations, `MoveAlongPath`, or `ValueTracker` sweeps when constant velocity is expected)*
  - `there_and_back`, `there_and_back_with_pause`
  - `rush_into` *(accelerate)*, `rush_from` *(decelerate)*
  - `running_start`, `lingering`, `wiggle`, `exponential_decay`
  - `squish_rate_func(smooth, 0.2, 0.8)` *(constricts an easing to `[a, b]` sub-interval of `alpha`)*
- **Accessed via `rate_functions.<name>`**:
  - `rate_functions.ease_in_<type>`, `rate_functions.ease_out_<type>`, `rate_functions.ease_in_out_<type>`
  - Where `<type>` is one of: `sine`, `quad`, `cubic`, `quart`, `quint`, `expo`, `circ`, `back`, `elastic`, `bounce`.

---

## 5. Reactive Animations: `ValueTracker`, `always`, Updaters & `always_redraw`

### Pattern A: Declarative `Mobject.always` (v0.20+ — Cleanest for Simple Tracking)
```python
box = Square()
label = Text("Box").next_to(box, UP)
label.always.next_to(box, UP)          # Re-runs label.next_to(box, UP) every frame!

self.add(box, label)
self.play(box.animate.shift(RIGHT * 3))
```

### Pattern B: `ValueTracker` + `add_updater` / `always_redraw`
Use `ValueTracker` to animate an invisible scalar parameter and let dependent mobjects update automatically:

```python
theta = ValueTracker(0.0)
radius = 2.0

circle = Circle(radius=radius, color=BLUE_D)
dot = Dot(color=YELLOW).set_z_index(5)
dot.add_updater(
    lambda m: m.move_to([
        radius * np.cos(theta.get_value()),
        radius * np.sin(theta.get_value()),
        0,
    ])
)

# Use always_redraw when geometry topology is rebuilt each frame (lines, braces, polygons, Riemann rects):
radius_line = always_redraw(
    lambda: Line(ORIGIN, dot.get_center(), color=TEAL)
)
readout = DecimalNumber(0, num_decimal_places=2, unit=r"\text{ rad}").to_corner(UR)
readout.add_updater(lambda d: d.set_value(theta.get_value()))

self.add(circle, radius_line, dot, readout)
self.play(theta.animate.set_value(TAU), run_time=4, rate_func=linear)
dot.clear_updaters()                   # Clean up when tracking is no longer needed
```

### Pattern C: Time-Based Updaters (`dt`)
Updater functions accepting a second parameter `dt` receive the frame time delta (`1 / fps`):
```python
gear.add_updater(lambda m, dt: m.rotate(90 * DEGREES * dt))
self.add(gear)
self.wait(3)   # Scene detects time-based updater and renders all 3s of motion (not a frozen frame!)
```
> [!IMPORTANT]
> 1. If you attach a `dt` updater to a **`ValueTracker`**, you **must** `self.add(tracker)` to the scene so the scene ticks its updater! (When animating `tracker.animate.set_value(...)`, `self.play` handles it automatically without `self.add(tracker)`.)
> 2. During `self.play(SomeAnimation(mob))`, Manim **suspends updaters on `mob` itself** unless `suspend_mobject_updating=False` is passed to the animation.

---

## 6. Complete Animation Catalog & Custom `Animation` Subclasses

For the full reference of all built-in creation, fading, growing, indication, movement, number, and updater-utility animations—plus how to author custom `Animation` subclasses and `@override_animation` decorators—load [animation-catalog.md](./references/animation-catalog.md).
