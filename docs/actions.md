# Talon Actions

All actions are prefixed with `user.ui_elements_*`

## Core UI Management

| Action | Parameters | Description |
| -- | -- | -- |
| `user.ui_elements()` | `elements: Union[str, List[str]]` | **Primary method for building UIs.** Get UI elements by name. Returns tuple or single element. Example: `div, text = actions.user.ui_elements(["div", "text"])`. See [Elements documentation](../elements.md)<br><br>**Root elements:** `screen`, `active_window`<br>**Standard elements:** `window`, `div`, `text`, `button`, `input_text`, `checkbox`, `link`, `icon`, `table`, `tr`, `th`, `td`, `cursor`<br>**SVG elements:** `svg`, `path`, `rect`, `circle`, `line`, `polyline`, `polygon`<br>**Utility elements:** `state`, `ref`, `effect`, `component`, `style` |
| `user.ui_elements_show()` | `renderer: Callable`<br>`props: dict = None`<br>`on_mount: Callable = None`<br>`on_unmount: Callable = None`<br>`show_hints: bool = None`<br>`initial_state: dict = None`<br>`min_version: str = None`<br>`duration: str = None`<br>`scale: float = None` | **Primary method for displaying UIs.** Render and show the UI. The `renderer` parameter (required) is a function that returns an element tree (typically starting with `screen()` or `active_window()`). All other parameters are optional. `on_mount` runs after visible, `on_unmount` runs before hidden. `duration` auto-hides (e.g., `"1s"`). `scale` overrides default scale |
| `user.ui_elements_hide()` | `renderer_or_tree_id: Union[str, Callable]` | Destroy, garbage collect, and hide a specific UI by renderer function or tree ID |
| `user.ui_elements_hide_all()` | None | Destroy, garbage collect, and hide all UIs |
| `user.ui_elements_toggle()` | `renderer: Union[str, Callable]`<br>`props: dict = None`<br>`on_mount: Callable = None`<br>`on_unmount: Callable = None`<br>`show_hints: bool = None`<br>`initial_state: dict = None`<br>`min_version: str = None`<br>`scale: float = None` | Toggle visibility of a UI. Same parameters as `ui_elements_show()`. Returns boolean indicating new state |
| `user.ui_elements_is_active()` | `renderer: Union[str, Callable]` | Check if a specific UI is active by renderer function or tree ID. Returns boolean |

## State Management

| Action | Parameters | Description |
| -- | -- | -- |
| `user.ui_elements_set_state()` | `name: Union[str, dict]`<br>`value: Any = UNSET` | Set global state. Triggers full re-render with relayout. Pass dict to set multiple: `{"key": value}`. Pass callable to update: `lambda current: current + 1` |
| `user.ui_elements_get_state()` | `name: str = None`<br>`initial_state: Any = None` | Get global state value by name. Returns `initial_state` if not found. Pass no args to get all states. Does not trigger re-render |

## Element Manipulation (No Relayout - Faster)

**These render on decoration layer only. No relayout.**

| Action | Parameters | Description |
| -- | -- | -- |
| `user.ui_elements_set_text()` | `id: str`<br>`text_or_callable: Any` | Set text content by element ID. Fast, no rerender. Pass callable to update: `lambda current: current + "!"` |
| `user.ui_elements_highlight()` | `id: str`<br>`color: str = None` | Highlight element by ID. Optional color override. Decoration layer only |
| `user.ui_elements_unhighlight()` | `id: str` | Remove highlight from element by ID. Decoration layer only |
| `user.ui_elements_highlight_briefly()` | `id: str`<br>`color: str = None` | Highlight element briefly (auto-removes). Optional color override. Decoration layer only |

## Element Manipulation (Does Relayout)

**These trigger full re-renders with relayout.**

| Action | Parameters | Description |
| -- | -- | -- |
| `user.ui_elements_set_property()` | `id: str`<br>`property_name: Union[str, dict]`<br>`value: Any` | Set element property by ID. Triggers rerender. Pass dict to set multiple: `{"background_color": "red", "padding": 20}` |

## Interactive Elements

| Action | Parameters | Description |
| -- | -- | -- |
| `user.ui_elements_get_input_value()` | `id: str` | Get the current value of an `input_text` element by ID |
| `user.ui_elements_toggle_hints()` | `enabled: bool = None` | Toggle hints visibility. Pass `True`/`False` to set explicitly, or no args to toggle |

## Advanced Features

| Action | Parameters | Description |
| -- | -- | -- |
| `user.ui_elements_register_effect()` | `callback: Callable`<br>`arg2: Any`<br>`arg3: Any = None` | Register effect independently. Works like `effect` element but outside component tree. Use `(on_mount, [])` or `(on_change, [deps])` |
| `user.ui_elements_get_node()` | `id: str` | Get node object by ID for inspection. Access `.box_model`, `.tree`, `.parent_node`, `.children_nodes`, etc. |
| `user.ui_elements_get_trees()` | None | Get all tree objects. Each tree represents a rendered UI with all information and methods |

## Development Tools

| Action | Parameters | Description |
| -- | -- | -- |
| `user.ui_elements_dev_tools()` | None | Toggle dev tools UI for debugging |
| `user.ui_elements_debug_gc()` | None | Print garbage collection debug info to log |
| `user.ui_elements_version()` | None | Get version object with `.major`, `.minor`, `.patch` attributes. Supports comparison: `version < "0.6.2"` |
| `user.ui_elements_reset_all_scale_overrides()` | None | Clear all manual scale overrides (from Ctrl/Cmd +/-) |
| `user.ui_elements_storybook_toggle()` | None | Toggle storybook UI for component examples |
| `user.ui_elements_examples()` | None | Toggle example UIs |
| `user.ui_elements_test_runner()` | None | Toggle test runner UI |

## Usage Examples

### Basic Show/Hide

```python
div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

def my_ui():
    return screen()[
        div()[
            text("Hello world")
        ]
    ]

# Show
actions.user.ui_elements_show(my_ui)

# Hide
actions.user.ui_elements_hide(my_ui)

# Toggle
actions.user.ui_elements_toggle(my_ui)
```

### With Options

```python
actions.user.ui_elements_show(
    my_ui,
    props={"title": "My App"},
    on_mount=lambda: print("Mounted"),
    on_unmount=lambda: print("Hidden"),
    show_hints=True,
    initial_state={"count": 5},
    min_version="0.9.0",
    duration="3s",  # Auto-hide after 3 seconds
    scale=1.5
)
```

### State Management

```python
# Set state
actions.user.ui_elements_set_state("counter", 10)
actions.user.ui_elements_set_state("counter", lambda c: c + 1)
actions.user.ui_elements_set_state({"name": "John", "age": 30})

# Get state
value = actions.user.ui_elements_get_state("counter", 0)
all_states = actions.user.ui_elements_get_state()
```

### Fast Updates (Decoration Layer)

```python
# Update text (no rerender)
actions.user.ui_elements_set_text("status", "Processing...")

# Highlight
actions.user.ui_elements_highlight("button_1", "#FF0000")
actions.user.ui_elements_highlight_briefly("button_2")
actions.user.ui_elements_unhighlight("button_1")
```

### Property Updates (Full Rerender)

```python
# Single property
actions.user.ui_elements_set_property("my_div", "background_color", "#FF0000")

# Multiple properties
actions.user.ui_elements_set_property("my_div", {
    "background_color": "#0000FF",
    "color": "#FFFFFF",
    "padding": 20
})
```

### Voice Commands

```talon
# In your .talon file
show my app: user.ui_elements_show(user.my_app_ui)
hide my app: user.ui_elements_hide(user.my_app_ui)
toggle my app: user.ui_elements_toggle(user.my_app_ui)

# State updates
set counter <number>: user.ui_elements_set_state("counter", number)
increase counter:
    user.ui_elements_set_state("counter", user.ui_elements_get_state("counter", 0) + 1)

# Fast updates
status <user.text>: user.ui_elements_set_text("status", text)
highlight <user.text>: user.ui_elements_highlight_briefly(text)
```

## Next Steps

- Learn about [State and Reactivity](concepts/state.md) for reactive patterns
- Explore [Elements](../elements.md) for available components
- Check [Components](concepts/components.md) for reusable action patterns
- See the [tutorials](../tutorials/) for complete examples
