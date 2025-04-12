# State

`state` is for reactive state that rerenders all containing component(s) when changed. If no ancestor components are found, then the entire tree is rerendered.

- [State](#state)
  - [`state.get`](#stateget)
  - [`state.set`](#stateset)
  - [`state.use`](#stateuse)
  - [`state.use_local`](#stateuse_local)
  - [State scope and components](#state-scope-and-components)
  - [Setting initial state](#setting-initial-state)
  - [Complex state](#complex-state)
  - [Using ref instead for faster performance](#using-ref-instead-for-faster-performance)
  - [Lifecycle](#lifecycle)

## `state.get`

Gets the value of a global key

```py
..., state = actions.user.ui_elements([..., "state"])

mode = state.get("mode")
mode = state.get("mode", "default")

```

## `state.set`

Sets the value of a global key

```py
..., state = actions.user.ui_elements([..., "state"])

state.set("mode", "new_mode")
state.set("mode", lambda prev: "new_mode")
```

You can also use
```
actions.user.ui_elements_set_state("mode", "new_mode")
actions.user.ui_elements_set_state("mode", lambda prev: "new_mode")
```


## `state.use`

Returns the value and setter of a global key

```py
..., state = actions.user.ui_elements([..., "state"])

mode, set_mode = state.use("mode", "default")
```

## `state.use_local`

Returns the value and setter of a local key. Must be used within a component. Not for voice commands.

```py
..., state = actions.user.ui_elements([..., "state"])

expanded, set_expanded = state.use_local("expanded", False)
```

## State scope and components
A state change will try to limit rerendering to the containing component(s). If no ancestor components are found, then the entire tree is rerendered.  Read about [components](components.md) for more information.

## Setting initial state
If you want to set initial state outside of the UI, you can pass `initial_state` to `ui_elements_show`:

```py
actions.user.ui_elements_show(
    hello_world_ui,
    initial_state={
        "mode": "default",
        "expanded": False
    }
)
```

## Complex state
State is not restricted to simple values.
You can store objects, arrays, or any other data structure.

If you use a callback in the setter, it will give you the previous value, and you can return the new value.

```py
actions.user.ui_elements_set_state("form", lambda form: {**form, "name": "new_name"})
```

## Using ref instead for faster performance
If you just need to change a text value, you can instead use `actions.user.ui_elements_set_text` or a `ref`, as those text updates render on a separate decoration layer and do not cause a relayout.

## Lifecycle
States are cleared when the UI is hidden/destroyed.