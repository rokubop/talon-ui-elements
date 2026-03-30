---
name: ui-elements
description: Trigger when building or modifying Talon UI, HUD, overlay, notification, cheatsheet, or using ui_elements.
---

# talon-ui-elements

Python canvas UI library for Talon voice control runtime.

- **NOT web/browser** — renders on a Skia canvas. No HTML, CSS, DOM, or browser APIs.
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
window = actions.user.ui_elements("window")  # single element returns directly
```

**All elements:** `div`, `text`, `screen`, `button`, `input_text`, `textarea`, `select`, `data_table`, `state`, `ref`, `effect`, `icon`, `style`, `component`, `link`, `checkbox`, `table`, `tr`, `td`, `th`, `window`, `active_window`

**SVG elements** (separate function): `actions.user.ui_elements_svg(["svg", "path", "rect", "circle", "line", "polyline", "polygon"])`

---

## Element Hierarchy

- Root must be `screen()` or `active_window()`
- Children via bracket syntax: `parent()[child1, child2]`
- **Containers** (can have children): `div`, `window`, `table`, `tr`, `td`, `th`, `screen`, `active_window`, `svg`
- **Leaves** (no children): `text`, `icon`, `checkbox`, `input_text`, `textarea`, `select`, `data_table`, `link`
- **`button`**: leaf with label `button("Click")`, container without: `button(on_click=fn)[icon("check")]`
- Dynamic lists: `div()[*[text(item) for item in items]]`

---

## Properties Quick Reference

All properties are kwargs: `div(background_color="333333", padding=16)`.

- **Layout:** `flex_direction` ("column"/"row"), `justify_content`, `align_items`, `align_self`, `flex`, `gap`, `flex_wrap`
- **Sizing:** `width`, `height`, `min_width`, `max_width`, `min_height`, `max_height` — pixels or `"100%"`
- **Spacing:** `padding`, `margin` — plus `_top`, `_right`, `_bottom`, `_left` variants
- **Position:** `position` ("static"/"relative"/"absolute"/"fixed"), `top`, `left`, `right`, `bottom`
- **Colors:** `background_color`, `color`, `border_color` — hex strings (`"FF0000"`, `"#FF0000"`, `"FF000080"`) or named colors
- **Font:** `font_size` (default 16), `font_weight` ("normal"/"bold"), `font_family`, `text_align` ("left"/"center"/"right"), `white_space` ("normal"/"nowrap")
- **Border:** `border_width`, `border_radius`, `border_color` — plus individual sides (`border_top`, etc.)
- **Interactivity:** `on_click`, `on_change`, `highlight_style`, `disabled`, `draggable`, `drag_handle`, `autofocus`
- **Animation:** `transition`, `mount_style`, `unmount_style`
- **Identity:** `id`, `key`, `class_name`, `z_index`
- **Scrolling:** `overflow` / `overflow_y` / `overflow_x` = `"scroll"` | `"hidden"`
- **Other:** `opacity` (0.0-1.0, cascades), `drop_shadow`

See: `references/properties.md` for full tables with types and defaults.

---

## State Management

```python
state = actions.user.ui_elements("state")

value = state.get("key", default)                    # Read-only snapshot
value, set_value = state.use("key", default)         # Reactive (triggers re-render)
state.set("key", new_value)                          # Set directly

set_value(lambda prev: prev + 1)                     # Lambda setter
set_items(lambda prev: prev + [new_item])            # Append to list
```

**External access** (from voice commands / outside UI):
```python
actions.user.ui_elements_set_state("key", value)
actions.user.ui_elements_set_state("count", lambda prev: prev + 1)
actions.user.ui_elements_set_state({"key1": "val1", "key2": "val2"})  # batch
actions.user.ui_elements_get_state("key")
actions.user.ui_elements_get_state("key", "default_value")
```

**Initial state** (pre-set before first render):
```python
actions.user.ui_elements_show(my_ui, initial_state={"tab": "home", "items": []})
```

See: `docs/concepts/state.md`

---

## Refs (Imperative Updates)

Direct element access without re-renders. The id must match the `id` prop on the target element.

```python
ref = actions.user.ui_elements("ref")
my_ref = ref("my_text")

# In a callback or effect (NOT during initial render):
my_ref.text = "Updated"
my_ref.background_color = "FF0000"
my_ref.highlight()
my_ref.highlight_briefly()
my_ref.unhighlight()

# Input refs:
input_ref = ref("my_input")
input_ref.value       # Read current value
input_ref.clear()     # Clear the input
input_ref.focus()     # Focus the input
```

See: `docs/concepts/ref.md`

---

## Effects (Lifecycle)

```python
effect = actions.user.ui_elements("effect")

# Mount only:
effect(on_mount, [])

# Mount + unmount:
effect(on_mount, on_unmount, [])

# State change:
effect(on_tab_change, ["active_tab"])  # deps are string state key names

# Mount with cleanup:
def on_mount():
    return lambda: print("Cleanup!")
effect(on_mount, [])
```

See: `docs/concepts/effect.md`

---

## Style Blocks

CSS-like selectors for shared styles:

```python
style = actions.user.ui_elements("style")

style({
    "*": {"color": "CCCCCC"},                        # Universal
    "text": {"font_size": 14},                       # Tag selector
    "#my_id": {"background_color": "333333"},        # ID selector
    ".my_class": {"padding": 12, "border_radius": 6},  # Class selector
})

button("Click", class_name="my_class")
```

See: `docs/concepts/style.md`

---

## Elements Quick Reference

- `screen()` / `active_window()` — Root containers. `screen(1)` for second monitor. `active_window()` follows focused OS window.
- `div()` — Generic container.
- `text("content")` — Display text.
- `button("label", on_click=fn)` — Interactive button. Container when no label: `button(on_click=fn)[icon("check")]`.
- `input_text(id="x")` — Text input. **Requires `id`**. Supports `placeholder`, `autofocus`, `on_change`.
- `textarea(id="x", rows=5)` — Multi-line input. **Requires `id`**.
- `select(id="x", options=[...])` — Dropdown. **Requires `id`**. Options: strings or `{"label": "...", "value": "..."}` dicts.
- `checkbox(checked=True, on_change=fn)` — Toggle. Uses `on_change` not `on_click`.
- `link("text", url="...")` — Clickable URL. `close_on_click=True` to hide UI after click.
- `icon("name", size=24)` — Built-in SVG icon. Names: `check`, `close`, `star`, `edit`, `trash`, `plus`, `minus`, `play`, `pause`, `settings`, etc.
- `window(title="...")` — Draggable panel with title bar, minimize, close buttons.
- `table()` / `tr()` / `th()` / `td()` — Table structure.
- `component(fn, props)` — Reusable UI with local state (`state.use_local`). Only needed for local state or scoped styles.
- `svg()` / `path()` / `rect()` / `circle()` / `line()` — Custom SVG via `ui_elements_svg(...)`. Use `size` and `view_box`, not `width`/`height`/`viewBox`.

See: `docs/elements.md`

---

## Show / Hide API

```python
actions.user.ui_elements_show(my_ui)                                    # Show
actions.user.ui_elements_show(my_ui, initial_state={...})               # With initial state
actions.user.ui_elements_show(my_ui, duration="2s")                     # Auto-hide
actions.user.ui_elements_show(my_ui, on_mount=fn, on_unmount=fn)        # Lifecycle callbacks
actions.user.ui_elements_hide(my_ui)                                    # Hide by function ref
actions.user.ui_elements_hide("screen_id")                              # Hide by screen id
actions.user.ui_elements_toggle(my_ui)                                  # Toggle
actions.user.ui_elements_hide_all()                                     # Hide all
actions.user.ui_elements_is_active(my_ui)                               # Check if showing
```

See: `docs/actions.md`

---

## Imperative Actions (from outside the UI)

```python
# Fast updates (no re-render, decoration layer):
actions.user.ui_elements_set_text("element_id", "new text")
actions.user.ui_elements_set_text("element_id", lambda current: current + "!")
actions.user.ui_elements_highlight("element_id")
actions.user.ui_elements_highlight("element_id", "FF0000")
actions.user.ui_elements_unhighlight("element_id")
actions.user.ui_elements_highlight_briefly("element_id")

# Full re-render:
actions.user.ui_elements_set_property("element_id", "background_color", "red")
actions.user.ui_elements_set_property("element_id", {"bg": "red", "justify_content": "center"})

# Read input:
actions.user.ui_elements_get_input_value("input_id")
```

---

## Gotchas

1. **`flex_direction` defaults to `"column"`, not `"row"`.** Children stack vertically. Use `flex_direction="row"` for horizontal.

2. **Must CALL elements before brackets:** `div()[...]` not `div[...]`. Forgetting `()` raises `TypeError`.

3. **Root must be `screen()` or `active_window()`.** No bare `div()` as root.

4. **Children via `[]`, not function args.** `div()[text("hi")]` not `div(text("hi"))`.

5. **`input_text`, `textarea`, `select` require `id` prop.** `input_text(id="my_input")` not `input_text()`.

6. **`position` required for `top`/`left`/`right`/`bottom`.** `div(top=10, position="relative")` not `div(top=10)`.

7. **Loop variable capture:** `lambda e, item=item: delete(item)` not `lambda e: delete(item)`.

8. **Ref values not available during initial render.** Use refs in callbacks or effects only.

9. **Effect deps are string state key names:** `effect(fn, ["count"])` not `effect(fn, [count])`.

10. **`effect()` must be called during render** (inside UI function body), not outside or in a callback.

11. **`show()` twice is a no-op.** To restart, hide first then show.

12. **`checkbox` uses `on_change`, not `on_click`.** `on_click` will raise an error.

13. **`svg()` is not HTML `<svg>`.** Use `size` and `view_box` (underscore), not `width`/`height`/`viewBox`/`xmlns`.

14. **For frequent updates, prefer refs or `set_text` over state.** State triggers full re-renders; refs/`set_text` use the decoration layer and are much faster.

---

## Defaults

| Property | Default |
|---|---|
| `flex_direction` | `"column"` |
| `align_items` | `"stretch"` |
| `justify_content` | `"flex_start"` |
| `font_size` | `16` |
| `color` | `"FFFFFF"` |
| `background_color` | `None` (transparent) |
| `border_color` | `"555555"` |
| `position` | `"static"` |
| `font_weight` | `"normal"` |
| `text_align` | `"left"` |
| `z_index` | `0` |

**Cascaded** (inherited by children): `color`, `font_family`, `font_size`, `highlight_style`, `opacity`, `stroke`, `stroke_width`, `z_index`

---

## Further Reading

- `references/properties.md` — Full property tables with types and values
- `references/patterns.md` — Layout patterns, tab navigation, splitting files, complete examples
- `docs/elements.md` — All elements with detailed examples
- `docs/actions.md` — All Talon actions
- `docs/concepts/state.md` — State management deep dive
- `docs/concepts/effect.md` — Lifecycle effects
- `docs/concepts/ref.md` — Imperative ref system
- `docs/concepts/components.md` — Reusable components
- `docs/concepts/style.md` — CSS-like styling
- `docs/concepts/transitions.md` — Animations
- `docs/concepts/window.md` — Window element
- `docs/concepts/svgs.md` — Custom SVG graphics
- `docs/tutorials/` — Step-by-step tutorials (hello_world, cheatsheet, game_keys)
