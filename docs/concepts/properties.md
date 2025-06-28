# Properties

Properties control the appearance and behavior of UI elements. They work similarly to CSS properties but are designed for voice-activated interfaces.

## Property Syntax

Properties are passed as keyword arguments in the element's parentheses:

```python
div(
    width=200,
    height=100,
    background_color="blue",
    padding=16
)[
    text("Content", color="white", font_size=18)
]
```

## Layout Properties

### Size and Spacing

| Property | Description | Example |
|----------|-------------|---------|
| `width` | Element width | `width=200`, `width="50%"` |
| `height` | Element height | `height=100`, `height="100%"` |
| `min_width` | Minimum width | `min_width=100` |
| `max_width` | Maximum width | `max_width=500` |
| `min_height` | Minimum height | `min_height=50` |
| `max_height` | Maximum height | `max_height=300` |

### Padding and Margin

| Property | Description | Example |
|----------|-------------|---------|
| `padding` | All sides padding | `padding=16` |
| `padding_top` | Top padding | `padding_top=8` |
| `padding_bottom` | Bottom padding | `padding_bottom=8` |
| `padding_left` | Left padding | `padding_left=12` |
| `padding_right` | Right padding | `padding_right=12` |
| `margin` | All sides margin | `margin=16` |
| `margin_top` | Top margin | `margin_top=8` |
| `margin_bottom` | Bottom margin | `margin_bottom=8` |
| `margin_left` | Left margin | `margin_left=12` |
| `margin_right` | Right margin | `margin_right=12` |

### Flexbox Layout

| Property | Description | Values | Example |
|----------|-------------|--------|---------|
| `flex_direction` | Main axis direction | `"row"`, `"column"` | `flex_direction="row"` |
| `justify_content` | Main axis alignment | `"flex_start"`, `"center"`, `"flex_end"`, `"space_between"`, `"space_around"` | `justify_content="center"` |
| `align_items` | Cross axis alignment | `"flex_start"`, `"center"`, `"flex_end"`, `"stretch"` | `align_items="center"` |
| `flex` | Flex grow factor | `1` | `flex=1` |
| `gap` | Space between children | `gap=8` | `gap=16` |

## Visual Properties

### Colors

Colors can be specified as hex values (with or without #) or named colors:

```python
# Hex colors
background_color="FF0000"      # Red
background_color="#00FF00"     # Green
background_color="#0000FFAA"   # Blue with transparency of AA

# Named colors
color="red"
color="blue"
color="white"
```

Valid transparency values are from `00` (fully transparent) to `FF` (fully opaque) and can be optionally appended to the last two characters of the hex code.

| Property | Description | Example |
|----------|-------------|---------|
| `background_color` | Background color | `background_color="333333"` |
| `color` | Text color | `color="FFFFFF"` |
| `border_color` | Border color | `border_color="CCCCCC"` |

### Borders and Corners

| Property | Description | Example |
|----------|-------------|---------|
| `border` | All borders | `border="1px solid #ccc"` |
| `border_width` | Border thickness | `border_width=2` |
| `border_radius` | Corner rounding | `border_radius=8` |
| `border_top` | Top border only | `border_top="1px solid red"` |
| `border_bottom` | Bottom border only | `border_bottom="1px solid blue"` |
| `border_left` | Left border only | `border_left="2px solid green"` |
| `border_right` | Right border only | `border_right="2px solid yellow"` |

### Opacity and Shadows

| Property | Description | Example |
|----------|-------------|---------|
| `opacity` | Element transparency | `opacity=0.5` (50% transparent) |
| `drop_shadow` | Drop shadow - tuple value with (dx, dy, sigmaX, sigmaY, and color) | `drop_shadow=(0, 20, 25, 25, "000000CC")` |

## Typography Properties

| Property | Description | Values | Example |
|----------|-------------|--------|---------|
| `font_size` | Text size | Number in pixels | `font_size=16` |
| `font_family` | Font family | Font name | `font_family="Arial"` |
| `font_weight` | Text weight | `"normal"`, `"bold"`, `"100"`-`"900"` | `font_weight="bold"` |
| `text_align` | Text alignment | `"left"`, `"center"`, `"right"` | `text_align="center"` |

### Text Decoration

| Property | Description | Example |
|----------|-------------|---------|
| `stroke_color` | Text outline or svg outline color | `stroke_color="000000"` |
| `stroke_width` | Text outline or svg outline width | `stroke_width=2` |

## Positioning Properties

| Property | Description | Values | Example |
|----------|-------------|--------|---------|
| `position` | Positioning type | `"relative"`, `"static"`, `"absolute"`, `"fixed"` | `position="absolute"` |
| `top` | Distance from top | Number or percentage | `top=10`, `top="50%"` |
| `bottom` | Distance from bottom | Number or percentage | `bottom=10` |
| `left` | Distance from left | Number or percentage | `left=20` |
| `right` | Distance from right | Number or percentage | `right=20` |
| `z_index` | Stacking order | Number | `z_index=10` |

## Interactive Properties

### Cursor and Focus

| Property | Description | Values | Example |
|----------|-------------|--------|---------|
| `focus_outline_color` | Focus ring color | Color value | `focus_outline_color="blue"` |
| `focus_outline_width` | Focus ring width | Number | `focus_outline_width=2` |

### Dragging and Scrolling

| Property | Description | Values | Example |
|----------|-------------|--------|---------|
| `draggable` | Enable dragging | `True`, `False` | `draggable=True` |
| `drag_handle` | Drag handle area | `True`, `False` | `drag_handle=True` |
| `overflow_y` | Vertical overflow | `"scroll"`, `"visible"`, `"auto"` | `overflow_y="scroll"` |

## Event Properties

| Property | Description | Example |
|----------|-------------|---------|
| `on_click` | Click handler | `on_click=my_function` |
| `on_change` | Change handler | `on_change=handle_change` |

## Element-Specific Properties

### Input Elements

| Property | Description | Example |
|----------|-------------|---------|
| `on_change` | On_change text | `on_change=lambda e: print(e.value)` |
| `value` | Input value | `value="Default text"` |
| `autofocus` | Auto-focus on mount | `autofocus=True` |

### Button Elements

| Property | Description | Example |
|----------|-------------|---------|
| `on_click` | Click handler | `on_click=my_function` |

### Icon Elements

| Property | Description | Example |
|----------|-------------|---------|
| `size` | Icon size | `size=24` |
| `color` | Icon color | `color="red"` |
| `fill` | Fill color | `fill="red"` |
| `stroke` | Stroke color | `stroke="blue"` |
| `stroke_width` | Stroke width | `stroke_width=2` |

## CSS Class and ID

| Property | Description | Example |
|----------|-------------|---------|
| `id` | Unique identifier | `id="my_element"` |
| `class_name` | CSS class - can be styled using `style` | `class_name="header"` |

## Property Inheritance

Some properties cascade down to child elements:

- `color` - Text color
- `font_size` - Text size
- `font_family` - Font family
- `opacity` - Transparency
- `highlight_color` - Highlight color for voice commands

```python
div(color="blue", font_size=16)[
    text("This inherits blue color and 16px size"),
    text("This too", color="red")  # This overrides to red
]
```

## Common Patterns

### Centering Content

```python
# Center horizontally and vertically
div(
    justify_content="center",
    align_items="center",
)[
    text("Centered content")
]
```

### Creating Cards

```python
div(
    background_color="white",
    border_radius=8,
    padding=16,
    drop_shadow=(0, 4, 6, 6, "00000020"),
    margin=8
)[
    text("Card content")
]
```

### Button Styling

```python
button(
    "Click me",
    background_color="blue",
    color="white",
    border_radius=4,
    padding=12,
    on_click=my_function
)
```

## Property Values

### Units

- **Numbers**: Treated as pixels (e.g., `width=200` = 200px)
- **Percentages**: String with % (e.g., `width="50%"`)

### Colors

- **Hex**: `"FF0000"` or `"#FF0000"` for red
- **RGBA**: `"FF0000AA"` for red with transparency
- **Named**: `"red"`, `"blue"`, `"white"`, etc.

### Booleans

- `True` / `False` for toggle properties
- `draggable=True`, `autofocus=False`

## Next Steps

- Learn about [State and Reactivity](state.md) for dynamic properties
- Explore [Elements](elements.md) for available components
- Check [Components](components.md) for reusable styling patterns
