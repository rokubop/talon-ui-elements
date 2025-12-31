# SVGs

Create custom SVG graphics using standard SVG elements. Based on a standard `view_box="0 0 24 24"`.

- [SVGs](#svgs)
  - [SVG Elements](#svg-elements)
  - [SVG Properties](#svg-properties)
  - [Usage Examples](#usage-examples)
    - [Basic SVG](#basic-svg)
    - [Rectangle with rounded corners](#rectangle-with-rounded-corners)
    - [Circle](#circle)
    - [Lines](#lines)
    - [Polyline (connected lines, not closed)](#polyline-connected-lines-not-closed)
    - [Polygon (closed shape)](#polygon-closed-shape)
    - [Complex SVG (copy icon)](#complex-svg-copy-icon)
    - [Resizing and styling](#resizing-and-styling)
  - [Convert HTML SVG to ui\_elements code](#convert-html-svg-to-ui_elements-code)
  - [Resources](#resources)

## SVG Elements

| Element | Attributes | Description |
| -- | -- | -- |
| `svg` | `view_box`, `size` | Wrapper container for SVG elements |
| `path` | `d` | Draw complex paths using SVG path commands |
| `rect` | `x`, `y`, `width`, `height`, `rx`, `ry` | Draw rectangles with optional rounded corners |
| `circle` | `cx`, `cy`, `r` | Draw circles |
| `line` | `x1`, `y1`, `x2`, `y2` | Draw straight lines |
| `polyline` | `points` | Draw connected lines (not closed) |
| `polygon` | `points` | Draw connected lines (closed shape) |

## SVG Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| `fill` | Union[str, bool] | None | Fill color. Use `False` for no fill. Use 8-char hex for opacity |
| `stroke` | Union[str, bool] | None | Stroke color. Use `False` for no stroke. Use 8-char hex for opacity |
| `stroke_width` | Union[int, float] | 2 | Width of the stroke |
| `stroke_linecap` | "butt", "round", "square" | "round" | Stroke line cap style |
| `stroke_linejoin` | "miter", "round", "bevel" | "round" | Stroke line join style |
| `size` | Union[int, float] | 24 | Size for the `svg` wrapper (affects both width and height) |
| `view_box` | str | "0 0 24 24" | SVG viewBox attribute |
| `color` | str | "#FFFFFF" | Default color (cascades to children) |

SVG elements also support all standard layout and positioning properties.

## Usage Examples

### Basic SVG

```py
screen, div = actions.user.ui_elements(["screen", "div"])
svg, path, rect, circle = actions.user.ui_elements(["svg", "path", "rect", "circle"])

return screen(align_items="center", justify_content="center")[
    div()[
        # Custom icon using path
        svg()[
            path(d="M12 2 L22 12 L12 22 L2 12 Z", fill="#FF0000")
        ]
    ]
]
```

### Rectangle with rounded corners

```py
svg()[
    rect(x=5, y=5, width=14, height=14, rx=2, ry=2, fill="#00FF00", stroke="#0000FF", stroke_width=2)
]
```

### Circle

```py
svg()[
    circle(cx=12, cy=12, r=8, fill="#FF00FF", stroke="#FFFFFF", stroke_width=2)
]
```

### Lines

```py
svg()[
    line(x1=2, y1=2, x2=22, y2=22, stroke="#FFFFFF", stroke_width=2),
    line(x1=22, y1=2, x2=2, y2=22, stroke="#FFFFFF", stroke_width=2)
]
```

### Polyline (connected lines, not closed)

```py
svg()[
    polyline(points="2 2 12 12 22 2", stroke="#FF0000", stroke_width=2, fill=False)
]
```

### Polygon (closed shape)

```py
svg()[
    polygon(points="12 2 22 22 2 22", fill="#00FF00", stroke="#FFFFFF", stroke_width=2)
]
```

### Complex SVG (copy icon)

```py
svg()[
    rect(x=9, y=9, width=13, height=13, rx=2, ry=2),
    path(d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1")
]
```

### Resizing and styling

```py
# Large SVG with custom colors
svg(size=48, color="#FF0000")[
    path(d="M12 2 L22 12 L12 22 L2 12 Z")
]

# With transparency
svg(size=32)[
    circle(cx=12, cy=12, r=10, fill="#FF000080", stroke="#00FF00FF")
]

# Custom stroke width
svg(stroke_width=4)[
    path(d="M2 12 L22 12 M12 2 L12 22")
]
```

## Convert HTML SVG to ui_elements code

You can convert HTML SVG code to ui_elements code by:
1. Change attributes to snake_case (e.g., `stroke-width` → `stroke_width`)
2. Remove most SVG wrapper attributes (`xmlns`, `width`, `height` - use `size` instead)
3. Convert element tags to function calls

**HTML SVG example (from https://iconsvg.xyz/):**
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
</svg>
```

**ui_elements code:**
```py
svg, rect, path = actions.user.ui_elements(["svg", "rect", "path"])

svg()[
    rect(x=9, y=9, width=13, height=13, rx=2, ry=2),
    path(d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1")
]
```

## Resources

- Icon SVGs: https://iconsvg.xyz/
- More icons: https://lucide.dev/icons
