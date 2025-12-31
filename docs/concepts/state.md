# State

`state` is for global reactive state that rerenders the entire UI when changed. Can be updated with `actions.user.ui_elements_set_state`.

> **Note:** If you just want to highlight something (e.g., change background color or show an overlay), consider using `actions.user.ui_elements_highlight` or `actions.user.ui_elements_highlight_briefly` instead. These only update the decoration layer and don't require state or trigger a full UI re-render.

- [State](#state)
  - [`state.get`](#stateget)
  - [`state.set`](#stateset)
  - [`state.use`](#stateuse)
  - [`state.use_local`](#stateuse_local)
  - [Setting initial state](#setting-initial-state)
  - [Batching state updates](#batching-state-updates)
  - [Complex state](#complex-state)
  - [Other considerations for faster performance](#other-considerations-for-faster-performance)
  - [Lifecycle](#lifecycle)

## `state.get`

Gets the value of a global key

```py
..., state = actions.user.ui_elements([..., "state"])

color = state.get("color")
color = state.get("color", "red")  # Default to initial value "red"

```

## `state.set`

Sets the value of a global key

```py
..., state = actions.user.ui_elements([..., "state"])

state.set("color", "new_color")
state.set("color", lambda prev: "new_color")
```

You can also use
```
actions.user.ui_elements_set_state("color", "new_color")
actions.user.ui_elements_set_state("color", lambda prev: "new_color")
```


## `state.use`

Returns the value and setter of a global key

```py
..., state = actions.user.ui_elements([..., "state"])

color, set_color = state.use("color", "default")
```

## `state.use_local`

Same as `state.use` but instead of global state, the state will be local to a `component`. Use this when you want to have multiple instances of the same component each with their own state.

```py
def accordion(props):
  div, text, state = actions.user.ui_elements(["div", "text", "state"])
  expanded, set_expanded = state.use_local("expanded", False)
  name = props["name"]

  return div()[
      text(name, font_size=20),
      button("Click to expand", on_click=lambda: set_expanded(not expanded)),
      div(padding=16)[
          text(f"Details about {name}")
      ] if expanded else None
  ]

def main_ui():
    screen, div = actions.user.ui_elements(["screen", "div"])
    return screen()[
        component(accordion, {"name": "Accordion 1"}),
        component(accordion, {"name": "Accordion 2"}),
    ]
```

## Setting initial state
If you want to set initial state outside of the UI, you can pass `initial_state` to `ui_elements_show`:

```py
actions.user.ui_elements_show(
    hello_world_ui,
    initial_state={
        "color": "default",
        "expanded": False
    }
)
```

## Batching state updates
Any state updates that happen within 1 millisecond will be batched together, resulting in a single re-render.

So if you have multiple state updates in a row, they will all be applied at once, which is more efficient.

```py
actions.user.ui_elements_set_state("color", "red")
actions.user.ui_elements_set_state("size", 20)
# This will only cause one re-render
```

## Complex state
State is not restricted to simple values. You can have dictionaries, arrays, or tuples as well.

If you use a callback in the setter, it will give you the previous value, and you can return the new value.

```py
actions.user.ui_elements_set_state("form", lambda form: {**form, "name": "new_name"})
```

## Other considerations for faster performance
Because `state` causes a full re-render of the UI, you may want to consider these alternatives for better performance:
- Use `actions.user.ui_elements_set_text` for changing text, which only rerenders the decoration layer.
- Use `actions.user.ui_elements_highlight`, `actions.user.ui_elements_highlight_briefly`, and `actions.user.ui_elements_unhighlight` to highlight elements which only affects the decoration layer and is faster than state updates.

## Lifecycle
States are cleared when the UI is hidden/destroyed.