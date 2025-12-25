# Elements

UI Elements provides a collection of HTML-inspired components for building voice-activated interfaces in Talon.

## Getting Elements

Use `actions.user.ui_elements()` to get the elements you need:

```python
from talon import actions

# Get specific elements
div = actions.user.ui_elements("div")
div, text, button = actions.user.ui_elements(["div", "text", "button"])
table, th, tr, td = actions.user.ui_elements(["table", "th", "tr", "td"])
screen, window, icon, cursor = actions.user.ui_elements(["screen", "window", "icon", "cursor"])
# etc...
```

## Core Elements

### Layout Elements

| Element | Description | Example |
|---------|-------------|---------|
| `screen` | Typically the first element required for every UI, full screen size | `screen()[...]` |
| `active_window` | Root container that matches the size of currently active window you have open | `active_window()[...]` |
| `div` | Generic container | `div(padding=16)[...]` |
| `cursor` | Container that follows the mouse cursor position | `cursor()[text("Status")]` |
| `window` | Draggable window with title bar, close button, and drop shadow | `window(title="My App")[...]` |

### Content Elements

| Element | Description | Example |
|---------|-------------|---------|
| `text` | Display text content | `text("Hello world", font_size=16)` |
| `input_text` | Text input field | `input_text(id="my_input")` |
| `icon` | Built-in icons | `icon("arrow_right", size=24)` |

### Interactive Elements

| Element | Description | Example |
|---------|-------------|---------|
| `button` | Interactive button | `button("Click me", on_click=my_function)` |
| `checkbox` | Checkbox input | `checkbox(checked=True, on_change=handler)` |
| `link` | Clickable link | `link("Visit site", href="https://example.com")` |

### Table Elements

| Element | Description | Example |
|---------|-------------|---------|
| `table` | Table container | `table()[...]` |
| `th` | Table header cell | `th("Name")` or `th()[text("Name")]` |
| `tr` | Table row | `tr()[th("Name"), td("John")]` or `tr()[th()[text("Name")], td()[text("John")]]` |
| `td` | Table data cell | `td("John")` or `td()[text("John")]` or `td()[text("John", font_weight="bold")]` |

### SVG Elements

SVG elements default to a view box of `0 0 24 24` and can be customized with properties like `fill`, `stroke`, and `stroke_width`.

You can use a reference like https://lucide.dev/icons/ or https://iconsvg.xyz/, copy the SVG code, and convert to ui_elements format, which is
- replace `-` with `_`
- default to just `svg()` instead of passing it properties

```python
svg, path, rect = actions.user.ui_elements(["svg", "path", "rect"])
```

| Element | Description | Example |
|---------|-------------|---------|
| `svg` | SVG container | `svg()[...]` |
| `path` | SVG path | `path(d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77...")` |
| `rect` | SVG rectangle | `rect(x=0, y=0, width=10, height=10)` |
| `circle` | SVG circle | `circle(cx=12, cy=12, r=5)` |
| `line` | SVG line | `line(x1=0, y1=0, x2=10, y2=10)` |
| `polyline` | SVG polyline | `polyline(points="0,0 10,5 20,0")` |
| `polygon` | SVG polygon | `polygon(points="0,0 10,0 5,10")` |

## Special Elements

### Cursor Element

The `cursor` element is a container that follows the mouse cursor position in real-time. It's useful for displaying content like custom overlays, tooltips, or visual indicators that track with the cursor. Note that this doesn't replace the system cursor icon itself, but rather displays content that follows it.

Defaults:
`left: 0`
`top: 0`
`refresh_rate: 16` (60fps)

```python
cursor, div, text, icon = actions.user.ui_elements(["cursor", "div", "text", "icon"])

# Basic cursor with icon
screen()[
    cursor()[
        text("status", font_size=14),
    ]
]

# Cursor with offset positioning
screen()[
    cursor(left=10, top=10)[
        div(
            padding=8,
            background_color="000000cc",
            border_radius=4
        )[
            text("Cursor Info", color="ffffff")
        ]
    ]
]

# Custom refresh rate (in milliseconds)
cursor(refresh_rate=33)[...]  # 30fps
cursor(refresh_rate=16)[...]  # 60fps (default)
cursor(refresh_rate=8)[...]   # 120fps
```

## Reactive Elements

### State Management

| Element | Description | Example |
|---------|-------------|---------|
| `state` | Reactive state management | `count, set_count = state.use("count", 0)` |
| `effect` | Side effects and lifecycle | `effect(lambda: print("mounted"), [])` |
| `ref` | Direct element access | `input_ref = ref("my_input")` |

### Component System

| Element | Description | Example |
|---------|-------------|---------|
| `component` | Reusable components | `component(my_component_function)` |
| `style` | CSS-like styling | `style({"text": {"color": "red"}})` |

## Element Structure

All elements follow the same pattern:

```python
element(properties)[children]
```

- **Properties** go in parentheses `()`
- **Children** go in square brackets `[]`

### Examples

```python
# Text with properties, no children
text("Hello", color="red", font_size=16)

# Div with properties and children
div(padding=16, background_color="blue")[
    text("Child 1"),
    text("Child 2")
]

# Nested structure
screen()[
    div(class_name="header")[
        text("Title", font_size=24)
    ],
    div(class_name="content")[
        text("Body content"),
        button("Click me", on_click=my_function)
    ]
]
```

## Event Handling

Interactive elements accept event handlers:

```python
def handle_click():
    print("Button clicked!")

def handle_input(value):
    print(f"Input changed: {value}")

# Button with click handler
button("Submit", on_click=handle_click)

# Input with change handler
input_text(on_change=handle_input)

# Button with inline handler
button("Delete", on_click=lambda: print("Deleted!"))
```

## Common Patterns

### Conditional Rendering

```python
show_advanced = state.get("show_advanced", False)

div()[
    text("Basic content"),
    *(
        [text("Advanced content")]
        if show_advanced
        else []
    )
]
```

### Dynamic Lists

```python
items = ["apple", "banana", "cherry"]

div()[
    text("Fruits:"),
    *[text(f"• {item}") for item in items]
]
```

## Element IDs

Give elements unique IDs for targeting:

```python
div(id="my_container")[
    text("Original text", id="my_text")
]

# Later, update the text
actions.user.ui_elements_set_text("my_text", "New text")

# Or highlight the container
actions.user.ui_elements_highlight("my_container")
```

## Next Steps

- Learn about [Properties](properties.md) for styling elements
- Understand [State and Reactivity](state.md) for dynamic UIs
- Explore [Components](components.md) for reusable patterns
- Check [Talon Actions](actions.md) for voice integration
