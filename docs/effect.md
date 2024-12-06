# Effect

`effect` is for calling side effects on mount, unmount, or state change, similar to React's `useEffect`.

## Example
```py
screen, div, text, effect = actions.user.ui_elements(["screen", "div", "text", "effect"])

effect(lambda: print("Mounted"), [])

return screen()[
    div()[
        text("Hello world"),
    ],
]
```

`effect` takes a function and a list of dependencies. The function will be called when the dependencies change. If the dependencies are empty, the function will only be called on mount.

## On state change
```py
mode, set_mode = state.use("mode", "default")

effect(lambda: print("Mode changed to", mode), ["mode"])
```

Dependencies are strings, not values, and refer to the any global state key. Every time the global state `"mode"` changes, the effect will be called.

## Cleanup/Unmount

We can optionally include a cleanup function:
### Example 1
```py
def on_unmount():
    print("Unmounted")

def on_mount():
    print("Mounted")

# 3 arguments instead of 2
effect(on_mount, on_unmount, [])
```

### Example 2
```py
def on_unmount():
    print("Unmounted")

def on_mount():
    print("Mounted")

    # return an optional cleanup function
    return on_unmount

effect(on_mount, [])
```

If we have a cleanup function with dependencies, the cleanup function will be called on every dependency change, and on unmount.
