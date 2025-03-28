# State

`state` is for global reactive state that rerenders all respective UIs when changed.

## `state.use`
```py
screen, div, text, state = actions.user.ui_elements(["screen", "div", "text", "state"])

mode, set_mode = state.use("mode", "default")

return screen()[
    div()[
        text("Mode: " + mode),
        button("Change mode", on_click=lambda: set_mode("new_mode")),
    ],
]
```

`state.use` behaves like React’s `use_state`. It returns a tuple `(value, set_value)`. You must define a state key (e.g. `"mode"` in this case), so that `actions.user.ui_elements*` can also target it, and optionally a default value.

## `state.get`
```py
mode = state.get("mode")
mode = state.get("mode", "default")
```

Same as `state.use`, but only gets the value.

## `state.set`
```py
state.set("mode", "new_mode")
state.set("mode", lambda prev: "new_mode")
```

Just the setter. No return value.

## `user.actions` vs `state`
| Talon `user.actions` | `state` equivalent |
| --- | --- |
| `ui_elements_set_state("mode", "new_mode")` | `set_mode("new_mode")` from `state.use` or `state.set("mode", "new_mode")`|
| `ui_elements_get_state("mode")` | `mode = state.get("mode")` or `mode, set_mode = state.use("mode")` |

## Setting initial state
If you want to set initial state outside of the UI, you can pass `initial_state` to `ui_elements_show`:

```py
actions.user.ui_elements_show(hello_world_ui, initial_state={"mode": "default"})
```

## Complex state
State is not restricted to simple values. You can store objects, arrays, or any other data structure. If you use a callback in the setter, it will give you the previous value, and you can return the new value.

```py
actions.user.ui_elements_set_state("form", lambda form: {**form, "name": "new_name"})
```

## Rerenders
State changes do a full rerender every time (for now). If you just need to change the text, use `actions.user.ui_elements_set_text` or a `ref`, as those text updates render on a separate decoration layer and do not cause a relayout.

## Lifecycle
States are cleared when the UI is hidden/destroyed.