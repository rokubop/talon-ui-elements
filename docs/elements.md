# Elements

These are your building blocks for building UIs.

Examples:
```py
screen, div, text = actions.user.ui_elements(["screen", "div", "text"])
button, checkbox, link = actions.user.ui_elements(["button", "checkbox", "link"])
table, tr, th, td = actions.user.ui_elements(["table", "tr", "th", "td"])
```

Pass a list of element names to get the elements you need. You can request any combination of elements shown in the table below.

## All Elements

| Element | Type | Description | Example |
| -- | -- | -- | -- |
| `screen` | Root | Full screen container - must be the root element wrapping everything | `screen(justify_content="center", align_items="center")[...]` |
| `active_window` | Root | Container matching active window size - must be the root element wrapping everything | `active_window()[...]` |
| `div` | Layout | Generic container | `div(padding=16)[...]` |
| `window` | Layout | Draggable window with title bar, close button, and drop shadow - must be first element after screen | `screen(justify_content="center", align_items="center")[window(title="My App")[...]]` |
| `cursor` | Layout | Container that follows the mouse cursor position | `cursor()[text("Status")]` |
| `text` | Content | Display text content | `text("Hello world", font_size=16)` |
| `input_text` | Content | Text input field | `input_text(id="my_input", on_change=handler)` |
| `icon` | Content | Built-in icons (see [icons.md](icons.md)) | `icon("microphone", size=24)` |
| `button` | Interactive | Interactive button with click handler | `button(text="Click me", on_click=handler)` |
| `checkbox` | Interactive | Checkbox input with change handler | `checkbox(checked=True, on_change=handler)` |
| `link` | Interactive | Clickable link | `link(text="Visit", url="https://example.com")` |
| `table` | Table | Table container | `table()[tr()[...]]` |
| `tr` | Table | Table row | `tr()[th("Name"), td("Value")]` |
| `th` | Table | Table header cell | `th()[text("Header")]` |
| `td` | Table | Table data cell | `td()[text("Data")]` |
| `svg` | SVG | SVG container (see [svgs.md](svgs.md)) | `svg()[...]` |
| `path` | SVG | SVG path element - must be used inside svg() | `svg()[path(d="M12 2L15.09 8.26...")]` |
| `rect` | SVG | SVG rectangle - must be used inside svg() | `svg()[rect(x=0, y=0, width=10, height=10)]` |
| `circle` | SVG | SVG circle - must be used inside svg() | `svg()[circle(cx=12, cy=12, r=5)]` |
| `line` | SVG | SVG line - must be used inside svg() | `svg()[line(x1=0, y1=0, x2=10, y2=10)]` |
| `polyline` | SVG | SVG polyline (connected lines, not closed) - must be used inside svg() | `svg()[polyline(points="0,0 10,5 20,0")]` |
| `polygon` | SVG | SVG polygon (closed shape) - must be used inside svg() | `svg()[polygon(points="0,0 10,0 5,10")]` |
| `state` | Reactive | Reactive state management (see [state.md](concepts/state.md)) | `state.get("key")`, `state.set("key", value)`, `count, set_count = state.use("count", 0)` |
| `effect` | Reactive | Side effects and lifecycle hooks (see [effect.md](concepts/effect.md)) | `effect(on_mount, [])` for mount, `effect(on_change, ["mode"])` for state changes |
| `ref` | Reactive | Direct element access - useful for getting input_text values (see [ref.md](concepts/ref.md)) | `my_ref = ref()` then `input_text(ref=my_ref)` |
| `component` | Reactive | Reusable component wrapper (see [components.md](concepts/components.md)) | `component(my_component, props={...})` |
| `style` | Utility | Set styles for all elements or per `class_name` instead of inline (see [style.md](concepts/style.md)) | `style({"text": {"color": "red"}, ".header": {"font_size": 24}})` |

## Full Example

```py
from talon import actions

# The renderer function
def counter_ui():
    # Get the elements you need from ui_elements
    screen, div, text, button, state = actions.user.ui_elements([
        "screen", "div", "text", "button", "state"
    ])

    # Create reactive state for the counter, or use state.get
    count, set_count = state.use("count", 0)

    # Define click handler
    def on_increment():
        set_count(count + 1)

    def on_decrement():
        set_count(count - 1)

    # Return a tree of elements starting with a root element (screen)
    return screen(justify_content="center", align_items="center")[
        div(
            padding=32,
            background_color="222222",
            border_radius=8,
            border_width=1,
            border_color="555555"
        )[
            text("Counter", font_size=24, margin_bottom=16),
            text(f"Count: {count}", font_size=32, margin_bottom=16),
            div(flex_direction="row", gap=8)[
                button("Decrement", on_click=on_decrement),
                button("Increment", on_click=on_increment),
            ]
        ]
    ]

def show_counter_ui():
    actions.user.ui_elements_show(counter_ui)

def hide_counter_ui():
    actions.user.ui_elements_hide(counter_ui)

def set_counter(value):
    actions.user.ui_elements_set_state("count", value)
```