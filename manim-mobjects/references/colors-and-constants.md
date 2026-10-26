# Manim Colors, Palettes & Spatial Constants Reference

## 1. Spatial, Buffer & Angle Constants (`manim.constants`)

### Coordinate & Direction Vectors (`np.ndarray` of shape `(3,)`)
| Constant | Value | Meaning |
| :--- | :--- | :--- |
| `ORIGIN` | `[0., 0., 0.]` | Center of scene |
| `UP` / `DOWN` | `[0., 1., 0.]` / `[0., -1., 0.]` | ±Y unit step |
| `RIGHT` / `LEFT` | `[1., 0., 0.]` / `[-1., 0., 0.]` | ±X unit step |
| `OUT` / `IN` | `[0., 0., 1.]` / `[0., 0., -1.]` | ±Z unit step (`OUT` points toward camera in 2D) |
| `UL`, `UR`, `DL`, `DR` | `UP+LEFT`, `UP+RIGHT`, `DOWN+LEFT`, `DOWN+RIGHT` | Diagonal 2D corners |
| `X_AXIS`, `Y_AXIS`, `Z_AXIS` | `[1,0,0]`, `[0,1,0]`, `[0,0,1]` | Rotation/projection axes |

### Standard Spacing Buffers (`buff=...`)
- `SMALL_BUFF = 0.1`
- `MED_SMALL_BUFF = 0.25` *(default `buff` for `.next_to()` and `.arrange()`)*
- `MED_LARGE_BUFF = 0.5` *(default `buff` for `.to_edge()` and `.to_corner()`)*
- `LARGE_BUFF = 1.0`

### Angles
- `PI` ($\pi$), `TAU` ($2\pi$, full turn)
- `DEGREES = TAU / 360` -> write `45 * DEGREES` instead of manual radian conversion!

### Stroke Line Caps & Joints
- `CapStyleType`: `CapStyleType.AUTO`, `CapStyleType.ROUND`, `CapStyleType.BUTT`, `CapStyleType.SQUARE`
- `LineJointType`: `LineJointType.AUTO`, `LineJointType.ROUND`, `LineJointType.BEVEL`, `LineJointType.MITER`

---

## 2. Default Global Color Palette (`manim_colors`)

Every main hue comes in 5 lightness ramps from **`_A` (lightest)** to **`_E` (darkest)**, where the bare name equals **`_C`**:

| Family | Bare (`_C`) | Ramp Variants |
| :--- | :--- | :--- |
| **Blue** | `BLUE` (`#58C4DD`) | `BLUE_A`, `BLUE_B`, `BLUE_C`, `BLUE_D`, `BLUE_E`, `DARK_BLUE` |
| **Teal** | `TEAL` (`#5CD0B3`) | `TEAL_A`, `TEAL_B`, `TEAL_C`, `TEAL_D`, `TEAL_E` |
| **Green** | `GREEN` (`#83C167`) | `GREEN_A`, `GREEN_B`, `GREEN_C`, `GREEN_D`, `GREEN_E` |
| **Yellow** | `YELLOW` (`#FFFF00` / `#F7D96F` ramp) | `YELLOW_A`, `YELLOW_B`, `YELLOW_C`, `YELLOW_D`, `YELLOW_E` |
| **Gold** | `GOLD` (`#F0AC5F`) | `GOLD_A`, `GOLD_B`, `GOLD_C`, `GOLD_D`, `GOLD_E` |
| **Red** | `RED` (`#FC6255`) | `RED_A`, `RED_B`, `RED_C`, `RED_D`, `RED_E` |
| **Maroon** | `MAROON` (`#C55F73`) | `MAROON_A`, `MAROON_B`, `MAROON_C`, `MAROON_D`, `MAROON_E` |
| **Purple** | `PURPLE` (`#9A72AC`) | `PURPLE_A`, `PURPLE_B`, `PURPLE_C`, `PURPLE_D`, `PURPLE_E` |
| **Gray / Grey** | `GRAY` / `GREY` (`#888888`) | `GRAY_A` (`LIGHTER_GRAY`), `GRAY_B` (`LIGHT_GRAY`), `GRAY_C`, `GRAY_D` (`DARK_GRAY`), `GRAY_E` (`DARKER_GRAY`) |
| **Accents** | `WHITE`, `BLACK`, `ORANGE` (`#FF862F`), `PINK` (`#D147BD`), `LIGHT_PINK`, `DARK_BROWN`, `LIGHT_BROWN`, `GRAY_BROWN` |
| **Pure RGB/CMY** | `PURE_RED`, `PURE_GREEN`, `PURE_BLUE`, `PURE_CYAN`, `PURE_MAGENTA`, `PURE_YELLOW` *(CMY added in v0.20)* |
| **Logo** | `LOGO_WHITE`, `LOGO_GREEN`, `LOGO_BLUE`, `LOGO_RED`, `LOGO_BLACK` |

---

## 3. Extended Palettes & `ManimColor` / `HSV` Manipulation

### Extended Named Color Namespaces (Not in `*` Import)
```python
from manim.utils.color import DVIPSNAMES, SVGNAMES, XKCD, X11

Circle(color=SVGNAMES.CORNFLOWERBLUE)
Square(color=DVIPSNAMES.FORESTGREEN)
Dot(color=XKCD.MANGO)
```

### Constructing & Transforming `ManimColor`
```python
# Hex strings can be passed directly anywhere a ParsableManimColor is expected:
c1 = Circle(color="#38bdf8")

# Explicit ManimColor / HSV construction & manipulation (v0.19+):
col = ManimColor.from_hex(hex_str="#38bdf8")   # Note: parameter is `hex_str=`, not `hex=`
rgb = ManimColor.from_rgb((0.2, 0.7, 0.9))     # Floats in [0, 1] or ints in [0, 255]
hsv = HSV((0.55, 0.8, 0.95))                   # Hue, Saturation, Value in [0, 1]

lighter_col = BLUE.lighter(0.25)               # v0.19+
darker_col = BLUE.darker(0.25)                 # v0.19+
text_col = bg_color.contrasting()              # Picks BLACK or WHITE for legibility (v0.19+)
mid_col = interpolate_color(BLUE, RED, alpha=0.5)
gradient_list = color_gradient([BLUE, PURPLE, PINK], length_of_output=10)
```
