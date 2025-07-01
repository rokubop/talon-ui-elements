# Components

Components are just functions wrapped with `component`, and help encapsulate some functionality.

- Ability to use `state.use_local` to use local state instead of global
- Use of `style` will be constrained to the component's scope

## Function vs Component

Most of the time, you'll just write regular functions that return UI elements:

```python
def play_button():
    text, icon, button, state = actions.user.ui_elements(["text", "icon", "button", "state"])
    play, set_play = state.use("play", True)

    return button(on_click=lambda: set_play(not play))[
        icon("pause" if play else "play"),
        text("PAUSE" if play else "START"),
    ]

# Usage - just call it like any function
def main_ui():
    screen, window = actions.user.ui_elements(["screen", "window"])
    return screen()[
        window()[
            play_button()
        ]
    ]
```

This is just a regular function call - no special "component" wrapper needed.

## When to Use `component()`

You only need to wrap functions with `component()` when you want to use:
1. **Local state** (`state.use_local`)
2. **Scoped styles** (`style`)

### Local State Example

```python
def counter(props):
    div, button, text, state = actions.user.ui_elements(["div", "button", "text", "state"])
    # This creates isolated state per component instance
    count, set_count = state.use_local("count", 0)

    return div()[
        text(props["name"]),
        button("-", on_click=lambda: set_count(count - 1)),
        text(str(count)),
        button("+", on_click=lambda: set_count(count + 1)),
    ]

def app():
    div, component = actions.user.ui_elements(["div", "component"])

    return div()[
        component(counter, { "name": "Counter 1" }),  # First counter - independent state
        component(counter, { "name": "Counter 2" }),  # Second counter - independent state
        component(counter, { "name": "Counter 3" }),  # Third counter - independent state
    ]
```

### Scoped Styles Example

```python
def styled_table():
    table, tr, td, style = actions.user.ui_elements(["table", "tr", "td", "style"])

    # This style only applies within this component
    style({
        "td": {
            "padding": 8,
            "border_width": 1,
            "border_color": "gray"
        },
        "tr": {
            "background_color": "f5f5f5"
        }
    })

    return table()[
        tr()[
            td()[
                text("Name")
            ],
            td()[
                text("Value")
            ]
        ],
        tr()[
            td()[
                text("Item 1")
            ],
            td()[
                text("100")
            ]
        ],
    ]

def app():
    div, component = actions.user.ui_elements(["div", "component"])

    return div()[
        component(styled_table)  # Styles won't leak outside
    ]
```

## Summary

- **Functions**: Use for organizing UI code - just call them directly
- **`component()`**: Only wrap functions when you need `state.use_local` or scoped `style`
- Most of your UI code will be regular functions
- Components are the exception, not the rule
