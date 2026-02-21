# talon-ui-elements - AI Guide

**Python canvas UI library for Talon voice control runtime.**

- NOT web/browser - renders on a Skia canvas. No HTML, CSS, DOM, or browser APIs.
- Runs inside Talon's Python runtime (no pip, no virtualenv, no build step). Talon hot-reloads `.py` files on save.
- React-inspired declarative API with CSS-like properties (flexbox layout, styling kwargs).
- Import: `from talon import actions` → call `actions.user.ui_elements(["div", "text", "screen", ...])` to get element constructors.
- All UI code lives in plain `.py` files inside the Talon user directory.

---

## Minimal Example

```python
from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="#333333", padding=16, border_radius=8, border_width=1)[
            text("Hello world", color="#FFFFFF", font_size=24)
        ]
    ]

def show_hello_world():
    actions.user.ui_elements_show(hello_world_ui)

def hide_hello_world():
    actions.user.ui_elements_hide(hello_world_ui)

def toggle_hello_world():
    actions.user.ui_elements_toggle(hello_world_ui)
```

---

## Getting Elements

Destructure element constructors from `actions.user.ui_elements(...)`:

```python
div, text, screen = actions.user.ui_elements(["div", "text", "screen"])
button, input_text, state = actions.user.ui_elements(["button", "input_text", "state"])
ref, effect, icon = actions.user.ui_elements(["ref", "effect", "icon"])
style, component = actions.user.ui_elements(["style", "component"])
checkbox, link = actions.user.ui_elements(["checkbox", "link"])
table, th, tr, td = actions.user.ui_elements(["table", "th", "tr", "td"])
window = actions.user.ui_elements("window")  # single element returns directly
```

**All available elements:**
`div`, `text`, `screen`, `button`, `input_text`, `state`, `ref`, `effect`, `icon`, `style`, `component`, `link`, `checkbox`, `table`, `tr`, `td`, `th`, `window`, `active_window`

**SVG elements** (separate function):
```python
svg, path = actions.user.ui_elements_svg(["svg", "path"])
# All SVG elements: svg, path, rect, circle, line, polyline, polygon
```

> **GOTCHA:** You must CALL elements before using bracket syntax for children: `div()[...]` not `div[...]`. Forgetting the `()` will raise a `TypeError`.

---

## Element Hierarchy

- The root of every UI must be `screen()` (or `active_window()`).
- Children are declared with bracket syntax: `parent()[child1, child2]`
- **Container elements** (can have children): `div`, `window`, `table`, `tr`, `td`, `th`, `screen`, `active_window`, `svg`
- **Leaf elements** (cannot have children): `text`, `icon`, `checkbox`, `input_text`, `link`
- **`button`**: leaf when given a label `button("Click")`, but can wrap children when no label: `button(on_click=fn)[icon("check")]`
- Use splat unpacking for dynamic lists: `div()[*[text(item) for item in items]]`

```python
# Correct hierarchy
screen()[
    div(padding=16)[
        text("Title"),
        div(flex_direction="row", gap=8)[
            button("Save", on_click=save),
            button("Cancel", on_click=cancel),
        ]
    ]
]
```

---

## Properties Reference

All properties are passed as keyword arguments: `div(background_color="333333", padding=16)`.

### Layout

| Property | Type | Default | Values |
|---|---|---|---|
| `flex_direction` | str | `"column"` | `"column"`, `"row"` |
| `justify_content` | str | `"flex_start"` | `"flex_start"`, `"flex_end"`, `"center"`, `"space_between"`, `"space_evenly"` |
| `align_items` | str | `"stretch"` | `"stretch"`, `"center"`, `"flex_start"`, `"flex_end"` |
| `align_self` | str | None | `"stretch"`, `"center"`, `"flex_start"`, `"flex_end"` |
| `flex` | int | None | e.g. `1` - fills available space |
| `flex_wrap` | bool | False | `True` to wrap children |
| `gap` | int/float | None | Space between children in pixels |

### Sizing

| Property | Type | Notes |
|---|---|---|
| `width` | int/float/str | Pixels or `"100%"` |
| `height` | int/float/str | Pixels or `"100%"` |
| `min_width` | int | Minimum width in pixels |
| `max_width` | int | Maximum width in pixels |
| `min_height` | int | Minimum height in pixels |
| `max_height` | int | Maximum height in pixels |

### Spacing

| Property | Type | Notes |
|---|---|---|
| `padding` | int | All sides |
| `padding_top`, `padding_right`, `padding_bottom`, `padding_left` | int | Individual sides |
| `margin` | int | All sides |
| `margin_top`, `margin_right`, `margin_bottom`, `margin_left` | int | Individual sides |

### Positioning

| Property | Type | Notes |
|---|---|---|
| `position` | str | `"static"` (default), `"relative"`, `"absolute"`, `"fixed"` |
| `top`, `left`, `right`, `bottom` | int/float | **Requires** `position` to be set (not `"static"`) |

> **GOTCHA:** Using `top`, `left`, `right`, or `bottom` without setting `position` will raise an error.

### Colors

| Property | Type | Notes |
|---|---|---|
| `background_color` | str | Hex: `"FF0000"`, `"#FF0000"`, `"FF000080"` (with alpha), or named color |
| `color` | str | Text/foreground color (default: `"FFFFFF"`) |
| `border_color` | str | Border color (default: `"555555"`) |

**Named colors:** `black`, `white`, `red`, `green`, `blue`, `yellow`, `cyan`, `gray`, `silver`, `lime`, `purple`, `teal`, `navy`, `orange`, `pink`, `brown`, `gold`

### Font

| Property | Type | Default | Notes |
|---|---|---|---|
| `font_size` | int/float | `16` | |
| `font_weight` | str | `"normal"` | `"normal"`, `"bold"` |
| `font_family` | str | `""` | System font name |
| `text_align` | str | `"left"` | `"left"`, `"center"`, `"right"` |

### Border

| Property | Type | Notes |
|---|---|---|
| `border_width` | int | All sides |
| `border_top`, `border_right`, `border_bottom`, `border_left` | int | Individual sides |
| `border_radius` | int/float/tuple | Rounded corners. Single value or tuple for individual corners |
| `border_color` | str | Default: `"555555"` |

### Opacity

| Property | Type | Notes |
|---|---|---|
| `opacity` | float | `0.0` to `1.0`. Cascades to children and affects background, border, and text colors. |

### Scrolling

| Property | Type | Values |
|---|---|---|
| `overflow` | str | `"hidden"`, `"scroll"` |
| `overflow_x` | str | `"hidden"`, `"scroll"` |
| `overflow_y` | str | `"hidden"`, `"scroll"` |

### Interactivity

| Property | Type | Notes |
|---|---|---|
| `on_click` | callable | Click handler. Receives `ClickEvent` if handler accepts a parameter. |
| `on_change` | callable | For `input_text` and `checkbox`. Receives `ChangeEvent`. |
| `highlight_style` | dict | Hover style: `{"background_color": "444444"}`. Keys: `background_color`, `border_color`, `color`, `fill`, `stroke` |
| `disabled` | bool | Disables interactivity |
| `disabled_style` | dict | Style when disabled |
| `draggable` | bool | Makes element draggable |
| `drag_handle` | bool | Makes this element the drag handle for a draggable ancestor |
| `autofocus` | bool | Auto-focus `input_text` on mount |

### Animation

| Property | Type | Notes |
|---|---|---|
| `transition` | dict | `{"property_name": duration_ms}` or `{"property_name": (duration_ms, "easing")}` |
| `mount_style` | dict | Initial style when element mounts (animates FROM these values) |
| `unmount_style` | dict | Style to animate TO before element unmounts |

### Identity

| Property | Type | Notes |
|---|---|---|
| `id` | str | Unique identifier. Required for `input_text`. Used by refs, imperative actions. |
| `key` | str | Reconciliation key for dynamic lists |
| `class_name` | str | For style block matching |
| `z_index` | int | Stacking order (default: `0`) |

---

## Screen Element

`screen()` is the root container. It spans the full monitor.

```python
# Top-left aligned (default)
screen()

# Centered content
screen(justify_content="center", align_items="center")

# Second monitor
screen(1)

# With an id (for targeted hide)
screen(id="my_screen")[...]

# Hide by screen id
actions.user.ui_elements_hide("my_screen")
```

## Active Window Element

`active_window()` is like `screen()` but constrained to the currently focused OS window instead of the full monitor. Use it for UIs that should be positioned relative to the active app window.

```python
active_window = actions.user.ui_elements("active_window")

return active_window(justify_content="center", align_items="center")[
    div()[text("Attached to active window")]
]
```

---

## State Management

State triggers re-renders when changed. Must be called during render (inside the UI function).

```python
state = actions.user.ui_elements("state")

# Read-only (for display):
value = state.get("key", default_value)

# Read + write (returns current value and setter):
value, set_value = state.use("key", default_value)

# Set directly (also works):
state.set("key", new_value)

# Lambda setter (access previous value):
set_value(lambda prev: prev + 1)
set_items(lambda prev: prev + [new_item])
```

### External State Access (outside UI functions)

```python
# Set state from outside (e.g., from a Talon voice command):
actions.user.ui_elements_set_state("key", value)

# Lambda setter (access previous value):
actions.user.ui_elements_set_state("count", lambda prev: prev + 1)

# Set multiple states at once:
actions.user.ui_elements_set_state({"key1": "val1", "key2": "val2"})

# Get state from outside:
actions.user.ui_elements_get_state("key")
actions.user.ui_elements_get_state("key", "default_value")
```

### Initial State (pre-set before first render)

Pass `initial_state` to `ui_elements_show` to set state values before the UI renders for the first time. This avoids a flash of default values.

```python
actions.user.ui_elements_show(my_ui, initial_state={
    "active_tab": "settings",
    "username": "Alice",
    "items": ["one", "two", "three"],
})
```

---

## Refs (Imperative Updates)

Refs provide direct access to elements without triggering full re-renders. Create with `ref("element_id")` - the id must match the `id` prop on the target element.

```python
ref = actions.user.ui_elements("ref")

my_ref = ref("my_text")

# In the UI tree:
text("Hello", id="my_text")

# Later (e.g., in a click handler):
my_ref.text = "Updated"               # Update text content
my_ref.background_color = "FF0000"     # Update any property
my_ref.highlight()                     # Highlight the element
my_ref.unhighlight()                   # Remove highlight
my_ref.highlight_briefly()             # Flash highlight
my_ref.scroll_to(0, 100)              # Scroll to position
```

### Input Text Refs

```python
input_ref = ref("my_input")

input_ref.value       # Read current value
input_ref.clear()     # Clear the input
input_ref.focus()     # Focus the input
```

> **GOTCHA:** Ref values are not available during the initial render. Only use refs in callbacks (e.g., `on_click` handlers), effects, or after mount.

---

## Effects (Lifecycle)

Effects run side-effect code on mount, unmount, or state changes.

```python
effect = actions.user.ui_elements("effect")

# Run on mount only (empty dependency list):
def on_mount():
    print("Mounted!")
    return lambda: print("Cleanup!")  # Optional: return cleanup function

effect(on_mount, [])

# Mount + explicit unmount callback:
def on_mount():
    print("Mounted!")

def on_unmount():
    print("Unmounted!")

effect(on_mount, on_unmount, [])

# Run when a state key changes:
def on_tab_change():
    print("Tab changed!")

effect(on_tab_change, ["active_tab"])  # "active_tab" is a state key name
```

> **GOTCHA:** Dependencies are **string state key names**, not values. Use `["my_key"]` not `[my_value]`.

> **GOTCHA:** `effect()` must be called during render (inside the UI function body), not outside or in a callback.

---

## Style Blocks

Apply shared styles using CSS-like selectors:

```python
style = actions.user.ui_elements("style")

style({
    "*": {                              # Universal - applies to all elements
        "color": "CCCCCC",
    },
    "text": {                           # Tag selector - all text elements
        "font_size": 14,
    },
    "#my_id": {                         # ID selector
        "background_color": "333333",
    },
    ".my_class": {                      # Class selector
        "padding": 12,
        "border_radius": 6,
        "highlight_style": {
            "background_color": "444444",
        },
    },
})

# Apply class to elements:
button("Click", class_name="my_class")
div(class_name="my_class")[...]
```

---

## Window Element

A draggable window panel with title bar, minimize, and close buttons. Not an OS window - it's a canvas overlay.

```python
window = actions.user.ui_elements("window")

screen()[
    window(title="My Window")[
        text("Window content")
    ]
]
```

**Window properties:**

| Property | Type | Default | Notes |
|---|---|---|---|
| `title` | str | None | Title bar text |
| `show_title_bar` | bool | True | Show/hide title bar |
| `show_minimize` | bool | True | Show minimize button |
| `show_close` | bool | True | Show close button |
| `on_close` | callable | None | Called when close button clicked |
| `on_minimize` | callable | None | Called when minimize button clicked |
| `on_restore` | callable | None | Called when restored from minimized |
| `title_bar_style` | dict | None | Style dict for the title bar |
| `min_width` | int | None | Minimum window width |
| `draggable` | bool | True | Implicit - windows are draggable by default via title bar |

---

## Button Element

```python
button = actions.user.ui_elements("button")

# Text button
button("Click me", on_click=lambda e: print("Clicked!"))

# Styled button
button("Save", on_click=save, background_color="42A5F5", border_radius=4, padding=12)

# Icon button (no label - wraps children)
button(on_click=handler)[icon("check")]

# on_click receives a ClickEvent if the handler accepts a parameter
def handle_click(e):
    print(e.id, e.rect)

button("Click", on_click=handle_click)
```

> **GOTCHA - Loop variable capture:** In loops, use default argument to capture the variable:
> ```python
> for item in items:
>     button("Delete", on_click=lambda e, item=item: delete(item))
> #                                       ^^^^^^^^^ capture here
> ```

---

## Input Text

Text input field. **Requires `id` prop.**

```python
input_text, ref = actions.user.ui_elements(["input_text", "ref"])

my_input = ref("my_input")

# In the UI tree:
input_text(id="my_input", autofocus=True, background_color="222222", border_radius=4, width=200)

# on_change callback receives ChangeEvent:
def handle_change(e):
    print(e.value)           # Current value
    print(e.previous_value)  # Previous value
    print(e.id)              # Element id

input_text(id="search", on_change=handle_change)

# Read value via ref:
current_value = my_input.value

# Clear and refocus:
my_input.clear()
my_input.focus()
```

---

## Checkbox Element

Toggle checkbox implemented as a component with local state.

```python
checkbox = actions.user.ui_elements("checkbox")

def on_check_change(e):
    print(f"Checked: {e.checked}, ID: {e.id}")  # CheckboxEvent

checkbox(id="agree", checked=False, on_change=on_check_change)
checkbox(checked=True, color="00FF00", disabled=True)
```

**Properties:** `checked` (bool), `on_change` (callable), `disabled` (bool), `color`, `size`, `stroke_width`, plus standard styling.

> **Note:** Use `on_change`, not `on_click`. `on_click` will raise an error.

---

## Link Element

Clickable link that opens a URL in the browser.

```python
link = actions.user.ui_elements("link")

link("Visit GitHub", url="https://github.com")
link("Docs", url="https://docs.example.com", close_on_click=True)
```

**Properties:** `url` (str, required), `close_on_click` (bool), `minimize_on_click` (bool), plus standard text styling. Default color is blue with hover effect.

---

## Tables

```python
table, tr, td, th = actions.user.ui_elements(["table", "tr", "td", "th"])

table()[
    tr()[
        th("Name"),
        th("Age"),
    ],
    tr()[
        td("Alice"),
        td("30"),
    ],
    tr()[
        td("Bob"),
        td("25"),
    ],
]
```

---

## Icons

Built-in SVG icons rendered at 24x24 by default.

```python
icon = actions.user.ui_elements("icon")

icon("check")
icon("close", color="red", size=32)
icon("star", stroke_width=3)
```

**Available icon names:**
`arrow_down`, `arrow_left`, `arrow_right`, `arrow_up`,
`check`, `chevron_down`, `chevron_left`, `chevron_right`, `chevron_up`,
`clock`, `close`, `copy`,
`delta`, `diamond`, `download`,
`edit`, `external_link`,
`file`, `file_text`, `folder`,
`home`,
`maximize`, `menu`, `mic`, `minimize`, `minus`, `more_horizontal`, `more_vertical`, `multiply`,
`pause`, `play`, `plus`,
`rotate_left`,
`settings`, `shrink`, `star`, `stop`,
`trash`,
`upload`

**Icon properties:** `color`, `size`, `stroke_width`, `fill`

---

## SVG Elements

For custom SVG graphics. Based on viewBox `0 0 24 24` by default.

```python
svg, path, rect, circle, line, polyline, polygon = actions.user.ui_elements_svg(
    ["svg", "path", "rect", "circle", "line", "polyline", "polygon"]
)

svg()[
    path(d="M12 2 L22 12 L12 22 L2 12 Z", fill="red"),
    rect(x=10, y=10, width=100, height=100, fill="blue"),
    circle(cx=12, cy=12, r=10, stroke="white"),
    line(x1=0, y1=0, x2=24, y2=24, stroke="white"),
]
```

**`svg()` is NOT like HTML `<svg>`.** Don't pass `width`, `height`, or `viewBox` - use `size` (single number, default 24) and `view_box` (underscore, default `"0 0 24 24"`). `xmlns` is not a thing here.

```python
# WRONG - HTML-style attributes
svg(width=48, height=48, viewBox="0 0 24 24", xmlns="...")

# RIGHT - use size and view_box
svg(size=48, view_box="0 0 24 24")
```

---

## Transitions / Animations

### Property Transitions

Smoothly animate property changes:

```python
div(
    width=120,
    height=120,
    background_color="#4488FF",
    transition={
        "width": 400,                          # 400ms duration
        "height": 400,
        "opacity": (300, "linear"),            # with easing
        "background_color": 500,
        "border_radius": (500, "ease_out_bounce"),
    },
)
```

**Easing functions:** `"linear"`, `"ease_in"`, `"ease_out"`, `"ease_in_out"`, `"ease_out_bounce"`

### Highlight Transitions

When a node has both `highlight_style` and `transition`, hover highlights animate smoothly instead of snapping instantly:

```python
button(
    "Click me",
    highlight_style={"background_color": "#444444"},
    transition={"background_color": 150},
)
```

If a node has `transition` with color properties and `on_click` but no explicit `highlight_style`, one is auto-generated from `highlight_color`.

```python
# highlight_style auto-generated from highlight_color
button("Click me", transition={"background_color": 150})
```

### Mount / Unmount Animations

Animate elements in and out:

```python
div(
    opacity=1.0,
    top=0,
    position="relative",
    mount_style={"opacity": 0, "top": 20},       # Start here, animate TO current values
    unmount_style={"opacity": 0, "top": 20},      # Animate TO these values before removal
    transition={"opacity": 300, "top": 300},       # Animation timing
)[
    text("I fade in and slide up!")
]
```

---

## Show / Hide API

```python
# Show a UI (pass the function, don't call it)
actions.user.ui_elements_show(my_ui)

# With options
actions.user.ui_elements_show(my_ui,
    initial_state={"tab": "home"},       # Pre-set state before first render
    on_mount=lambda: print("visible"),   # After UI appears
    on_unmount=lambda: print("hidden"),  # Before UI disappears
    duration="2s",                       # Auto-hide after duration (e.g., "2s", "500ms")
)

# Hide
actions.user.ui_elements_hide(my_ui)          # By function reference
actions.user.ui_elements_hide("screen_id")    # By screen id

# Toggle
actions.user.ui_elements_toggle(my_ui)

# Hide all UIs
actions.user.ui_elements_hide_all()

# Check if active
actions.user.ui_elements_is_active(my_ui)  # Returns bool
```

> **GOTCHA:** Calling `ui_elements_show` twice with the same function is a no-op (the UI is already showing). To restart, hide first then show.

---

## Imperative Actions (from outside the UI)

These actions let you update a running UI from external code (e.g., Talon voice commands):

```python
# State
actions.user.ui_elements_set_state("key", value)
actions.user.ui_elements_get_state("key")

# Text (fast - no re-render, uses decoration layer)
actions.user.ui_elements_set_text("element_id", "new text")
actions.user.ui_elements_set_text("element_id", lambda current: current + "!")

# Properties (triggers re-render)
actions.user.ui_elements_set_property("element_id", "background_color", "red")
actions.user.ui_elements_set_property("element_id", {
    "background_color": "red",
    "justify_content": "center",
})

# Highlight (fast - decoration layer)
actions.user.ui_elements_highlight("element_id")
actions.user.ui_elements_highlight("element_id", "FF0000")  # custom color
actions.user.ui_elements_unhighlight("element_id")
actions.user.ui_elements_highlight_briefly("element_id")

# Input
actions.user.ui_elements_get_input_value("input_id")
```

---

## Components (Reusable UI with Local State)

`component` wraps a render function to create isolated, reusable UI pieces with their own local state and scoped styles.

```python
component, div, button, text, state = actions.user.ui_elements(
    ["component", "div", "button", "text", "state"]
)

def counter(props):
    count, set_count = state.use_local("count", props.get("initial", 0))
    return div(flex_direction="row", gap=8, align_items="center")[
        text(str(count)),
        button("+", on_click=lambda e: set_count(count + 1)),
    ]

def my_ui():
    return screen()[
        component(counter, {"initial": 5}),   # Independent state
        component(counter, {"initial": 10}),  # Separate instance
    ]
```

- `state.use_local("key", default)` - like `state.use`, but scoped to this component instance
- Styles defined with `style({...})` inside a component are scoped and don't leak out
- **When to use:** Only when you need `state.use_local` or scoped styles. Most UI code should just use regular Python functions.
- The render function receives a `props` dict if it accepts a parameter, or no args if it doesn't.

---

## Event Objects

### ClickEvent

```python
@dataclass
class ClickEvent:
    id: str           # Element ID (if set)
    cause: str = "click"
```

`on_click` handlers receive a `ClickEvent` **only if the handler accepts a parameter**. A zero-argument lambda works too:

```python
button("A", on_click=lambda e: print(e.id))   # receives ClickEvent
button("B", on_click=lambda: print("clicked")) # no event, also valid
```

### ChangeEvent (input_text)

```python
@dataclass
class ChangeEvent:
    value: str              # Current value
    id: str = None          # Element ID
    previous_value: str = None
```

### CheckboxEvent

```python
@dataclass
class CheckboxEvent:
    checked: bool    # New checked state
    id: str = None
```

### WindowCloseEvent

```python
class WindowCloseEvent:
    hide: bool
    def prevent_default(self):
        """Call to prevent the window from actually closing"""
```

```python
def on_close(e):
    e.prevent_default()  # Keep window open
    print("Close prevented")

window(title="My Window", on_close=on_close)[...]
```

---

## Drop Shadow

```python
div(
    drop_shadow=(x_offset, y_offset, blur_x, blur_y, color),
    # Example:
    drop_shadow=(0, 4, 8, 8, "00000088"),
)
```

---

## Registering Effects from Outside

`ui_elements_register_effect` works like `effect()` but can be called outside the render function. It attaches to the current or next rendered tree.

```python
actions.user.ui_elements_register_effect(on_mount, [])
actions.user.ui_elements_register_effect(on_mount, on_unmount, [])
actions.user.ui_elements_register_effect(on_change, ["state_key"])
```

---

## Building Complex UIs

### Conditional Rendering

Return `None` to skip rendering an element:

```python
div()[
    text("Always shown"),
    text("Only if active") if is_active else None,
    div(background_color="red")[text("Error")] if has_error else None,
]
```

### Tab Navigation

Use state to switch between pages. Store page functions in a dict:

```python
def page_home():
    return div()[text("Home page")]

def page_settings():
    return div()[text("Settings page")]

TAB_PAGES = {
    "home": page_home,
    "settings": page_settings,
}

def my_app():
    div, text, button, screen, state, component = actions.user.ui_elements(
        ["div", "text", "button", "screen", "state", "component"]
    )

    tab, set_tab = state.use("tab", "home")

    return screen()[
        div()[
            # Tab bar
            div(flex_direction="row", gap=8)[
                *[button(
                    label,
                    on_click=lambda e, t=t: set_tab(t),
                    background_color="444444" if tab == t else "222222",
                ) for t, label in [("home", "Home"), ("settings", "Settings")]],
            ],
            # Active page
            component(TAB_PAGES[tab]),
        ]
    ]
```

### Splitting UI Across Files

Extract page functions and reusable helpers into separate files. Import them into the main UI:

```python
# ui/colors.py
BG_DARK = "1E1E1E"
BG_PANEL = "2A2A2A"
TEXT_DIM = "888888"

# ui/sidebar.py
from talon import actions
from .colors import BG_PANEL

def sidebar(items, selected, on_select):
    div, text, button = actions.user.ui_elements(["div", "text", "button"])
    return div(background_color=BG_PANEL, min_width=160, padding=8, gap=4)[
        *[button(
            item,
            on_click=lambda e, item=item: on_select(item),
            background_color="444444" if item == selected else None,
        ) for item in items]
    ]

# ui/app.py
from talon import actions
from .sidebar import sidebar

def my_app():
    div, text, screen, state = actions.user.ui_elements(["div", "text", "screen", "state"])
    selected, set_selected = state.use("selected", "item1")

    return screen()[
        div(flex_direction="row")[
            sidebar(["item1", "item2", "item3"], selected, set_selected),
            div(flex=1, padding=16)[
                text(f"Selected: {selected}"),
            ],
        ]
    ]
```

> **Note:** Helper functions that return elements (like `sidebar` above) are just regular Python functions - you don't need `component()` for them. Only use `component()` when you need `state.use_local` or scoped styles.

### Updating UI from Voice Commands / External Code

The typical pattern for complex UIs: Talon actions push data into the UI via `ui_elements_set_state`, and the UI reads it with `state.get`:

```python
# my_package.py (Talon actions)
from talon import Module, actions

mod = Module()

@mod.action_class
class Actions:
    def my_update_data(new_data: list):
        """Push data into the UI"""
        actions.user.ui_elements_set_state("my_data", new_data)

    def my_toggle_ui():
        """Show/hide the UI"""
        actions.user.ui_elements_toggle(my_dashboard)

# ui.py
from talon import actions

def my_dashboard():
    div, text, screen, state, effect = actions.user.ui_elements(
        ["div", "text", "screen", "state", "effect"]
    )

    items = state.get("my_data", [])

    # Populate initial data on mount
    def on_mount():
        actions.user.my_fetch_initial_data()

    effect(on_mount, [])

    return screen()[
        div()[
            *[text(item) for item in items]
        ]
    ]
```

### Common Layout Patterns

**Sidebar + Main Content:**
```python
div(flex_direction="row", height=600)[
    div(min_width=200, border_right=1, padding=16)[...],  # Sidebar
    div(flex=1, padding=16)[...],                          # Main content
]
```

**Header + Scrollable Body + Footer:**
```python
div(height=500)[
    div(padding=8)[text("Header")],                              # Fixed header
    div(flex=1, overflow_y="scroll", padding=8)[...],            # Scrollable body
    div(padding=8, border_top=1)[text("Footer")],               # Fixed footer
]
```

**Overlay / Floating Element:**
```python
div(position="relative")[
    div()[...],  # Normal content
    div(position="absolute", bottom=8, right=8)[
        text("Overlay badge")
    ],
]
```

---

## Complete Examples

### 1. Hello World

```python
from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="#333333", padding=16, border_radius=8, border_width=1)[
            text("Hello world", color="#FFFFFF", font_size=24)
        ]
    ]

def show_hello_world():
    actions.user.ui_elements_show(hello_world_ui)

def hide_hello_world():
    actions.user.ui_elements_hide(hello_world_ui)

def toggle_hello_world():
    actions.user.ui_elements_toggle(hello_world_ui)
```

### 2. Todo List (state, refs, input, buttons, dynamic lists)

```python
from talon import actions

def todo_list_ui():
    elements = ["div", "text", "button", "screen", "state", "input_text", "ref"]
    div, text, button, screen, state, input_text, ref = actions.user.ui_elements(elements)

    items, set_items = state.use('items', [])
    add_input = ref('add_input')

    def add_item():
        new_item = add_input.value
        if new_item:
            set_items(items + [new_item])
            add_input.clear()
            add_input.focus()

    def delete_item(item_name):
        set_items([item for item in items if item != item_name])

    def item(item_name):
        return div(background_color="333333", justify_content="space_between", flex_direction="row", align_items="center", gap=8)[
            text(item_name, color="FFFFFF", font_size=16),
            button("X", background_color="FF0000", font_size=10, on_click=lambda: delete_item(item_name), border_radius=2)
        ]

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="333333", padding=16, border_radius=8, gap=16)[
            text("Todo list", font_size=24, padding=8),
            div(gap=8, max_height=300, margin_top=8)[
                *[item(item_name) for item_name in items]
            ],
            div(border_top=1, margin_top=8, padding_top=16, gap=16)[
                text("New Item", font_size=12, id="label"),
                div(flex_direction="row", gap=8)[
                    input_text(id="add_input", autofocus=True, background_color="222222", border_radius=4, width=200),
                    button("Add", on_click=add_item, background_color="42A5F5", border_radius=4, padding=12)
                ]
            ]
        ]
    ]

def show_todo_list():
    actions.user.ui_elements_show(todo_list_ui)

def hide_todo_list():
    actions.user.ui_elements_hide(todo_list_ui)

def toggle_todo_list():
    actions.user.ui_elements_toggle(todo_list_ui)
```

### 3. Notification (mount/unmount animations, auto-hide)

```python
from talon import actions, cron

def notification_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(
            padding=15,
            background_color="#0088ffdd",
            border_radius=10,
            opacity=1.0,
            top=0,
            position="relative",
            mount_style={"opacity": 0, "top": 20},
            unmount_style={"opacity": 0, "top": 20},
            transition={"opacity": 300, "top": 300},
        )[
            text("Notification: saved!", font_size=20, color="white", font_weight="bold"),
        ],
    ]

def show_notification():
    actions.user.ui_elements_show(notification_ui, duration="2s")

def hide_notification():
    actions.user.ui_elements_hide(notification_ui)
```

### 4. Transitions (property animations, style blocks, state-driven UI)

```python
from talon import actions

def transitions_ui():
    elements = ["div", "text", "button", "screen", "state", "style"]
    div, text, button, screen, state, style = actions.user.ui_elements(elements)

    expanded, set_expanded = state.use("expanded", False)
    faded, set_faded = state.use("faded", False)
    color_shifted, set_color_shifted = state.use("color_shifted", False)
    bounced, set_bounced = state.use("bounced", False)

    style({
        ".sidebar_btn": {
            "padding": 12,
            "padding_left": 20,
            "padding_right": 20,
            "border_radius": 6,
            "border_width": 1,
            "border_color": "#444444",
            "color": "#FFFFFF",
            "font_size": 14,
            "highlight_style": {
                "background_color": "#444444",
            },
        },
        ".sidebar_btn_active": {
            "padding": 12,
            "padding_left": 20,
            "padding_right": 20,
            "border_radius": 6,
            "border_width": 1,
            "border_color": "#FFCC00",
            "background_color": "#3D3200",
            "color": "#FFCC00",
            "font_size": 14,
            "highlight_style": {
                "background_color": "#4D4200",
            },
        },
    })

    def toggle_all():
        val = not (expanded or faded or color_shifted or bounced)
        set_expanded(val)
        set_faded(val)
        set_color_shifted(val)
        set_bounced(val)

    def reset():
        set_expanded(False)
        set_faded(False)
        set_color_shifted(False)
        set_bounced(False)

    all_active = expanded and faded and color_shifted and bounced

    return screen(justify_content="center", align_items="center")[
        div(
            draggable=True,
            background_color="#1E1E1E",
            border_radius=12,
            border_width=1,
            border_color="#333333",
            width=700,
            flex_direction="row",
        )[
            # Sidebar
            div(
                padding=16,
                gap=8,
                border_right=1,
                border_color="#333333",
                min_width=160,
            )[
                text("Transitions", font_size=18, font_weight="bold", color="#FFCC00", margin_bottom=8),
                button(
                    "Expand" if not expanded else "Collapse",
                    class_name="sidebar_btn_active" if expanded else "sidebar_btn",
                    on_click=lambda e: set_expanded(not expanded),
                ),
                button(
                    "Fade" if not faded else "Unfade",
                    class_name="sidebar_btn_active" if faded else "sidebar_btn",
                    on_click=lambda e: set_faded(not faded),
                ),
                button(
                    "Color" if not color_shifted else "Uncolor",
                    class_name="sidebar_btn_active" if color_shifted else "sidebar_btn",
                    on_click=lambda e: set_color_shifted(not color_shifted),
                ),
                button(
                    "Bounce" if not bounced else "Unbounce",
                    class_name="sidebar_btn_active" if bounced else "sidebar_btn",
                    on_click=lambda e: set_bounced(not bounced),
                ),
                div(height=8),
                button(
                    "All",
                    class_name="sidebar_btn_active" if all_active else "sidebar_btn",
                    on_click=lambda e: toggle_all(),
                ),
                button(
                    "Reset",
                    class_name="sidebar_btn",
                    on_click=lambda e: reset(),
                ),
            ],
            # Main content area
            div(
                flex=1,
                justify_content="center",
                align_items="center",
                padding=40,
                min_height=350,
            )[
                div(
                    width=250 if expanded else 120,
                    height=200 if expanded else 120,
                    background_color="#FFCC00" if color_shifted else "#4488FF",
                    opacity=1.0 if not faded else 0.15,
                    border_radius=24 if bounced else 8,
                    justify_content="center",
                    align_items="center",
                    transition={
                        "width": 400,
                        "height": 400,
                        "opacity": (300, "linear"),
                        "background_color": 500,
                        "border_radius": (500, "ease_out_bounce"),
                    },
                )[
                    text(
                        "Animated",
                        font_size=20 if expanded else 14,
                        font_weight="bold",
                        color="#000000" if color_shifted else "#FFFFFF",
                        transition={
                            "font_size": 300,
                            "color": 500,
                        },
                    ),
                ],
            ],
        ]
    ]

def show_transitions():
    actions.user.ui_elements_show(transitions_ui)

def hide_transitions():
    actions.user.ui_elements_hide(transitions_ui)

def toggle_transitions():
    actions.user.ui_elements_toggle(transitions_ui)
```

---

## Defaults Quick Reference

| Property | Default |
|---|---|
| `flex_direction` | `"column"` |
| `align_items` | `"stretch"` |
| `justify_content` | `"flex_start"` |
| `font_size` | `16` |
| `color` | `"FFFFFF"` (white) |
| `border_color` | `"555555"` |
| `position` | `"static"` |
| `font_weight` | `"normal"` |
| `text_align` | `"left"` |
| `z_index` | `0` |

**Cascaded properties** (inherited by children): `color`, `font_family`, `font_size`, `highlight_style`, `opacity`, `stroke`, `stroke_width`, `z_index`

---

## Common Mistakes

1. **Must call elements before brackets:**
   ```python
   # WRONG
   div[text("hello")]
   # RIGHT
   div()[text("hello")]
   ```

2. **Don't use `top`/`left`/`right`/`bottom` without `position`:**
   ```python
   # WRONG - raises error
   div(top=10)[...]
   # RIGHT
   div(top=10, position="relative")[...]
   ```

3. **`input_text` requires `id`:**
   ```python
   # WRONG - raises error
   input_text()
   # RIGHT
   input_text(id="my_input")
   ```

4. **Calling `ui_elements_show` twice is a no-op.** The UI is already active. To restart it, hide first then show.

5. **Loop variable capture in lambdas:**
   ```python
   # WRONG - all buttons will reference the last item
   for item in items:
       button("Delete", on_click=lambda e: delete(item))
   # RIGHT - capture with default argument
   for item in items:
       button("Delete", on_click=lambda e, item=item: delete(item))
   ```

6. **Effects must be called during render:**
   ```python
   # WRONG - outside the UI function
   effect(my_callback, [])
   def my_ui():
       return screen()[...]

   # RIGHT - inside the UI function
   def my_ui():
       effect(my_callback, [])
       return screen()[...]
   ```

7. **Effect dependencies are state key strings, not values:**
   ```python
   # WRONG
   count, set_count = state.use("count", 0)
   effect(on_change, [count])
   # RIGHT
   effect(on_change, ["count"])
   ```

8. **Ref values not available during initial render.** Use refs in callbacks or effects, not inline during the first render pass.

9. **For frequent updates (game HUDs, live data), prefer refs or `set_text` over state.** State triggers full re-renders; refs/`set_text` update the decoration layer directly and are much faster.

10. **`flex_direction` defaults to `"column"`, not `"row"`.** Unlike CSS, children stack vertically by default. Use `flex_direction="row"` explicitly for horizontal layouts.

11. **`svg()` is not HTML `<svg>`.** Don't use `width`/`height`/`viewBox`/`xmlns`. Use `size` (single number) and `view_box` (underscore).
