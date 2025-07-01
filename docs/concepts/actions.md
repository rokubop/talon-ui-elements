# Talon Actions

## Core Actions

### Elements for building UIs

```python
# Get UI elements by their names
div, text, screen = actions.user.ui_elements(["div", "text", "screen"])
```

See the [Elements documentation](elements.md) for available components.

### Display Management

```python
# Renders for the first time and shows the UI
actions.user.ui_elements_show(my_ui_function)

# Destroys, garbage collects, and hide all UIs
actions.user.ui_elements_hide_all()

# Destroys, garbage collects, and hides a specific UI
actions.user.ui_elements_hide(my_ui_function)

# Toggles between showing and hiding a UI
actions.user.ui_elements_toggle(my_ui_function)
```

### Advanced Display Options

```python
# Show with options
actions.user.ui_elements_show(
    my_ui_function,
    props={"title": "My App"},          # Pass props to the UI
    on_mount=lambda: print("Mounted"),  # Runs after visible
    on_unmount=lambda: print("Hidden"), # Runs before hidden
    show_hints=True,                    # Show voice hints if interactive elements are present
    initial_state={"count": 5}          # Initial global state accessed with `state` element
    min_version="0.9.0"  # Minimum ui_elements version required
)
```

You can also replace `ui_elements_show` with `ui_elements_toggle` to toggle between showing and hiding a UI.

## State Management Actions

### Getting and Setting State

These will trigger full re-renders.

```python
# Get state value
value = actions.user.ui_elements_get_state("counter", 0)

# Set state value
actions.user.ui_elements_set_state("counter", 10)

# Set state with function
actions.user.ui_elements_set_state("counter", lambda current: current + 1)

# Set multiple state values
actions.user.ui_elements_set_state({
    "counter": 10,
    "name": "John",
    "active": True
})
```

### State in Voice Commands

These will trigger full re-renders.

```talon
# Simple state update
mode edit: user.ui_elements_set_state("mode", "edit")

# State update with captured value
set counter to <number>: user.ui_elements_set_state("counter", number)
```

## Element Interaction Actions

These will trigger decoration-only renders (faster than state change). No layout changes occur, only visual updates.

### Text Updates

```python
# Update text content (fast, no re-render)
actions.user.ui_elements_set_text("my_element_id", "New text")

# Update with voice command
actions.user.ui_elements_set_text("status", "Voice command received")
```

### Highlighting

These will trigger decoration-only renders (faster than state change). No layout changes occur, only visual updates.

```python
# Highlight an element
actions.user.ui_elements_highlight("my_element_id")

# Highlight briefly (auto-removes)
actions.user.ui_elements_highlight_briefly("my_element_id")

# Remove highlight
actions.user.ui_elements_unhighlight("my_element_id")

# Highlight with custom color
actions.user.ui_elements_highlight("my_element_id", "FF0000")
```

### Property Updates

These will trigger full re-renders.

```python
# Update single property
actions.user.ui_elements_set_property("my_element_id", "background_color", "red")

# Update multiple properties
actions.user.ui_elements_set_property("my_element_id", {
    "background_color": "blue",
    "color": "white",
    "padding": 20
})
```

## Voice Integration Patterns

### Basic Show/Hide Commands

```python
# In your .py file
from talon import Module, actions

mod = Module()

@mod.action_class
class Actions:
    def show_my_app():
        """Show my application"""
        actions.user.ui_elements_show(my_app_ui)

    def hide_my_app():
        """Hide my application"""
        actions.user.ui_elements_hide_all()

    def toggle_my_app():
        """Toggle my application"""
        actions.user.ui_elements_toggle(my_app_ui)
```

```talon
# In your .talon file
show my app: user.show_my_app()
hide my app: user.hide_my_app()
toggle my app: user.toggle_my_app()
```

### State Control Commands

```python
@mod.action_class
class Actions:
    def increase_counter():
        """Increase the counter"""
        current = actions.user.ui_elements_get_state("counter", 0)
        actions.user.ui_elements_set_state("counter", current + 1)

    def set_counter_value(value: int):
        """Set counter to specific value"""
        actions.user.ui_elements_set_state("counter", value)

    def reset_counter():
        """Reset counter to zero"""
        actions.user.ui_elements_set_state("counter", 0)
```

```talon
increase counter: user.increase_counter()
set counter <number>: user.set_counter_value(number)
reset counter: user.reset_counter()
```

### Element Interaction Commands

```talon
highlight <user.text>: user.ui_elements_highlight_briefly(text)
status <user.text>: user.ui_elements_set_text("status", text)
```

## Debugging Actions

You can `elements debug` while you have a UI open to inspect state.

## Next Steps

- Learn about [State and Reactivity](state.md) for reactive patterns
- Explore [Elements](elements.md) for available components
- Check [Components](components.md) for reusable action patterns
- See the [tutorials](../tutorials/) for complete examples
