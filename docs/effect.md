# Effect

`effect` is for calling side effects on mount, unmount, or state change, similar to React's `useEffect`.

## Example
```py
screen, div, text, effect = actions.user.ui_elements(["screen", "div", "text", "effect"])

def on_mount():
    print("Mounted")

effect(on_mount, [])

return screen()[
    div()[
        text("Hello world"),
    ],
]
```

`effect` takes a function and a list of dependencies. If there are no dependencies, the `effect`  above will only be called only on mount, after the UI is rendered.

## On state change
```py
mode, set_mode = state.use("mode", "default")

def on_mode_change():
    print("Mode changed to", mode)

effect(on_mode_change, ["mode"])
```

Dependencies are strings, not values, and refer to any global state key. The above will be called on mount, and whenever the `mode` state changes.

## Cleanup/Unmount

We can optionally include a cleanup function by passing 3 arguments to effect.
### Example 1
```py
def on_unmount():
    print("Unmounted")

def on_mount():
    print("Mounted")

effect(on_mount, on_unmount, [])
```

Or by RETURNING a cleanup function from the mount function.

### Example 2
```py
def on_unmount():
    print("Unmounted")

def on_mount():
    print("Mounted")

    return on_unmount

effect(on_mount, [])
```

If we have a cleanup function with dependencies, the cleanup function will be called on every dependency change, and on unmount.
