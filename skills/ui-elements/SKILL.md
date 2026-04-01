---
name: ui-elements
description: Trigger when building or modifying Talon UI, HUD, overlay, notification, cheatsheet, or using ui_elements.
---

# talon-ui-elements

Python canvas UI library for Talon voice control runtime.

- NOT web/browser - renders on a Skia canvas. No HTML, CSS, DOM, or browser APIs.
- Everything is flexbox. No `display: block/inline/grid`. Every container is a flex container.
- `flex_direction` defaults to `"column"` - children stack vertically. Use `flex_direction="row"` for horizontal.
- `align_items` defaults to `"stretch"` on containers (divs), `"flex_start"` on screen.
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
        div(background_color="#333333", padding=16, border_radius=8, border_width=1)[
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

All elements: `div`, `text`, `screen`, `button`, `input_text`, `textarea`, `select`, `data_table`, `form`, `state`, `ref`, `effect`, `icon`, `style`, `component`, `link`, `checkbox`, `table`, `tr`, `td`, `th`, `window`, `active_window`

SVG elements (separate function): `actions.user.ui_elements_svg(["svg", "path", "rect", "circle", "line", "polyline", "polygon"])`

---

## Element Hierarchy

- Root must be `screen()` or `active_window()`
- Children via bracket syntax: `parent()[child1, child2]`
- Containers (can have children): `div`, `form`, `window`, `table`, `tr`, `td`, `th`, `screen`, `active_window`, `svg`
- Leaves (no children): `text`, `icon`, `checkbox`, `input_text`, `textarea`, `select`, `data_table`, `link`
- `button`: leaf with label `button("Click")`, container without: `button(on_click=fn)[icon("check")]`
- Dynamic lists: `div()[*[text(item) for item in items]]`

See [patterns.md](references/patterns.md) for common layout patterns, tab navigation, and complete examples.

---

## Properties Quick Reference

All properties are kwargs: `div(background_color="333333", padding=16)`.

- Layout: `flex_direction` ("column"/"row"), `justify_content`, `align_items`, `align_self`, `flex`, `gap`, `flex_wrap`
- Sizing: `width`, `height`, `min_width`, `max_width`, `min_height`, `max_height` - pixels or `"100%"`
- Spacing: `padding`, `margin` - plus `_top`, `_right`, `_bottom`, `_left` variants
- Position: `position` ("static"/"relative"/"absolute"/"fixed"), `top`, `left`, `right`, `bottom`
- Colors: `background_color`, `color`, `border_color` - hex strings (`"FF0000"`, `"#FF0000"`, `"FF000080"`) or named colors
- Font: `font_size` (default 16), `font_weight` ("normal"/"bold"), `font_family`, `text_align` ("left"/"center"/"right"), `white_space` ("normal"/"nowrap")
- Border: `border_width`, `border_radius`, `border_color` - plus individual sides (`border_top`, etc.)
- Interactivity: `on_click`, `on_change`, `highlight_style`, `disabled`, `draggable`, `drag_handle`, `autofocus`
- Animation: `transition`, `mount_style`, `unmount_style`
- Identity: `id`, `key`, `class_name`, `z_index`
- Scrolling: `overflow` / `overflow_y` / `overflow_x` = `"scroll"` | `"hidden"`
- Other: `opacity` (0.0-1.0, cascades), `drop_shadow`

See [properties.md](references/properties.md) for full tables with types and defaults.

---

## State Management

All state is global - any UI or voice command can read/write any key. State is shared across UIs, so one UI can react to state set by another UI or by a voice command.

```python
state = actions.user.ui_elements("state")

value = state.get("key", default)                    # Read-only snapshot
value, set_value = state.use("key", default)         # Reactive (triggers re-render)
state.set("key", new_value)                          # Set directly

set_value(lambda prev: prev + 1)                     # Lambda setter
set_items(lambda prev: prev + [new_item])            # Append to list
```

External access (from voice commands / outside UI):
```python
actions.user.ui_elements_set_state("key", value)
actions.user.ui_elements_set_state("count", lambda prev: prev + 1)
actions.user.ui_elements_set_state({"key1": "val1", "key2": "val2"})  # batch
actions.user.ui_elements_get_state("key")
actions.user.ui_elements_get_state("key", "default_value")
```

Initial state (pre-set before first render):
```python
actions.user.ui_elements_show(my_ui, initial_state={"tab": "home", "items": []})
```

See: `docs/concepts/state.md`

---

## Refs

Direct element access for input fields. Requires matching `id` prop. Only use in callbacks or effects, not during initial render.

```python
ref = actions.user.ui_elements("ref")
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

- `screen()` / `active_window()` - Root containers. `screen(1)` for second monitor. `active_window()` follows focused OS window.
- `div()` - Generic container.
- `text("content")` - Display text.
- `form(on_submit=fn)` - Form container. Enter in child `input_text` or clicking a child `button(type="submit")` triggers `on_submit`. Callback receives `SubmitEvent(data={"input_id": "value", ...})` with all child input values. Ctrl+Enter submits from `textarea`.
- `button("label", on_click=fn)` - Interactive button. Container when no label: `button(on_click=fn)[icon("check")]`. Use `type="submit"` inside a `form` to trigger the form's `on_submit`.
- `input_text(id="x")` - Text input. Requires `id`. Supports `placeholder`, `autofocus`, `on_change`.
- `textarea(id="x", rows=5)` - Multi-line input. Requires `id`.
- `select(id="x", options=[...])` - Dropdown. Requires `id`. Options: strings or `{"label": "...", "value": "..."}` dicts.
- `checkbox(checked=True, on_change=fn)` - Toggle. Uses `on_change` not `on_click`.
- `link("text", url="...")` - Clickable URL. `close_on_click=True` to hide UI after click.
- `icon("name", size=24)` - Built-in SVG icon (Lucide-style, 24x24 viewbox). ~48 available names: `arrow_down`, `arrow_left`, `arrow_right`, `arrow_up`, `check`, `chevron_down`, `chevron_left`, `chevron_right`, `chevron_up`, `close`, `clock`, `copy`, `delta`, `diamond`, `download`, `edit`, `external_link`, `file`, `file_text`, `folder`, `home`, `maximize`, `menu`, `mic`, `minimize`, `minus`, `more_horizontal`, `more_vertical`, `multiply`, `pause`, `play`, `plus`, `rotate_left`, `settings`, `shrink`, `star`, `stop`, `trash`, `upload`.
- `window(title="...")` - Draggable panel with title bar, minimize, close buttons.
- `table()` / `tr()` / `th()` / `td()` - Table structure.
- `component(fn, props)` - Reusable UI with local state (`state.use_local`). Only needed for local state or scoped styles.
- `svg()` / `path()` / `rect()` / `circle()` / `line()` - Custom SVG via `ui_elements_svg(...)`. Use `size` and `view_box`, not `width`/`height`/`viewBox`. Icons use a 24x24 viewbox. To create a custom icon:
```python
svg, path, circle = actions.user.ui_elements_svg(["svg", "path", "circle"])
# defaults: size=24, view_box="0 0 24 24", stroke_width=2, stroke_linecap/linejoin="round"
svg()[
    circle(cx=12, cy=12, r=10),
    path(d="M12 6v6l4 2"),
]
```

See: `docs/elements.md`

---

## Show / Hide API

```python
actions.user.ui_elements_show(my_ui)                                    # Show
actions.user.ui_elements_show(my_ui, initial_state={...})               # With initial state
actions.user.ui_elements_show(my_ui, duration="2s")                     # Auto-hide
actions.user.ui_elements_show(my_ui, on_mount=fn, on_unmount=fn)        # Lifecycle callbacks
actions.user.ui_elements_show(my_ui, show_hints=False)                  # Disable voice hints
actions.user.ui_elements_hide(my_ui)                                    # Hide by function ref
actions.user.ui_elements_hide("screen_id")                              # Hide by screen id
actions.user.ui_elements_toggle(my_ui)                                  # Toggle
actions.user.ui_elements_hide_all()                                     # Hide all
actions.user.ui_elements_is_active(my_ui)                               # Check if showing
```

Every interactive element (buttons, inputs, links, checkboxes) automatically gets a voice-activated 2-letter hint label. Users say the letters to click the element. This is on by default - pass `show_hints=False` to disable for UIs that don't need voice interaction (e.g. display-only HUDs).

See: `docs/actions.md`

---

## Imperative Actions (from outside the UI)

```python
# Decoration layer (no re-render):
actions.user.ui_elements_set_text("element_id", "new text")
actions.user.ui_elements_set_text("element_id", lambda current: current + "!")
actions.user.ui_elements_highlight("element_id")
actions.user.ui_elements_unhighlight("element_id")
actions.user.ui_elements_highlight_briefly("element_id")

# Read input:
actions.user.ui_elements_get_input_value("input_id")
```

---

## Reactive State vs Decoration Layer

Choose your update strategy based on whether layout changes:

- Reactive (`state.use`) - for forms, wizards, dashboards. Layout adds/removes/resizes elements. Re-renders on change. Use when interactions are human-speed (clicks, typing).
- Decoration layer (`highlight`, `set_text`) - for game overlays, real-time HUDs. Layout renders once; only appearance changes (color, text content). No re-render, no layout recalc. Use when updates are rapid or performance-critical.

The decoration layer paints on top of existing elements without touching layout. `highlight` changes an element's visual state (background, border, color). `set_text` swaps displayed text. Neither can add, remove, or reposition elements - use state for that.

```python
# Game overlay: render once, update via decoration layer
# highlight_style defines the look; default is a gray overlay if omitted
div(id="jump", highlight_style={"background_color": "87ceeb88"}, **key_style)[text("jump")]

# On rapid input events (no re-render):
actions.user.ui_elements_highlight_briefly("jump")       # tap
actions.user.ui_elements_highlight("jump")               # hold
actions.user.ui_elements_unhighlight("jump")             # release
actions.user.ui_elements_set_text("apm", str(apm_count)) # live counter
```

See [paradigms.md](references/paradigms.md) for complete examples of both approaches.

---

## Gotchas

1. `flex_direction` defaults to `"column"`, not `"row"`. Children stack vertically. Use `flex_direction="row"` for horizontal.
2. Must CALL elements before brackets: `div()[...]` not `div[...]`. Forgetting `()` raises `TypeError`.
3. Root must be `screen()` or `active_window()`. No bare `div()` as root.
4. Children via `[]`, not function args. `div()[text("hi")]` not `div(text("hi"))`.
5. `input_text`, `textarea`, `select` require `id` prop. `input_text(id="my_input")` not `input_text()`.
6. `position` required for `top`/`left`/`right`/`bottom`. `div(top=10, position="relative")` not `div(top=10)`.
7. Loop variable capture: `lambda e, item=item: delete(item)` not `lambda e: delete(item)`.
8. Ref values not available during initial render. Use refs in callbacks or effects only.
9. Effect deps are string state key names: `effect(fn, ["count"])` not `effect(fn, [count])`.
10. `effect()` must be called during render (inside UI function body), not outside or in a callback.
11. `show()` twice is a no-op. To restart, hide first then show.
12. `checkbox` uses `on_change`, not `on_click`. `on_click` will raise an error.
13. `svg()` is not HTML `<svg>`. Use `size` and `view_box` (underscore), not `width`/`height`/`viewBox`/`xmlns`.

---

## Defaults

| Property | Default |
|---|---|
| `flex_direction` | `"column"` |
| `align_items` | `"stretch"` (containers), `"flex_start"` (screen) |
| `justify_content` | `"flex_start"` |
| `font_size` | `16` |
| `color` | `"FFFFFF"` |
| `background_color` | `None` (transparent) |
| `border_color` | `"555555"` |
| `position` | `"static"` |
| `font_weight` | `"normal"` |
| `text_align` | `"left"` |
| `z_index` | `0` |

Cascaded (inherited by children): `color`, `font_family`, `font_size`, `highlight_style`, `opacity`, `stroke`, `stroke_width`, `z_index`

---

## Further Reading

- `references/properties.md` - Full property tables with types and values
- `references/patterns.md` - Layout patterns, tab navigation, splitting files, complete examples
- `references/paradigms.md` - Reactive state vs decoration layer: full examples of both approaches
- `docs/elements.md` - All elements with detailed examples
- `docs/actions.md` - All Talon actions
- `docs/concepts/state.md` - State management deep dive
- `docs/concepts/effect.md` - Lifecycle effects
- `docs/concepts/ref.md` - Imperative ref system
- `docs/concepts/components.md` - Reusable components
- `docs/concepts/style.md` - CSS-like styling
- `docs/concepts/transitions.md` - Animations
- `docs/concepts/window.md` - Window element
- `docs/concepts/svgs.md` - Custom SVG graphics
- `docs/tutorials/` - Step-by-step tutorials (hello_world, cheatsheet, game_keys)
