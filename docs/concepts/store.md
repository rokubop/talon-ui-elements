# Store

Use `state` if you want data to be cleared when the UI hides.
Use `store` if you want data to persist across UI hide/shows.

`store` creates a prefixed namespace in `state`, and you can still interact with it like a normal `state`

Minimal example:
```py
my_store = actions.user.ui_elements_store("my_store", {
    "color": None,
})

def app():
    div, text, button, state = actions.user.ui_elements(["div", "text", "button", "state"])
    color, set_color = state.use("my_store.color")
    return div()[
        text(f"Color: {color}"),
        button("Change color", on_click=lambda: set_color("blue"))
    ]

actions.user.ui_elements_show(app)
actions.user.ui_elements_hide(app)

actions.user.ui_elements_get_state("my_store.color") # blue
```

- [Store](#store)
  - [Create a store](#create-a-store)
  - [Read it in a UI](#read-it-in-a-ui)
  - [Read and write it anywhere](#read-and-write-it-anywhere)
  - [Talon actions](#talon-actions)
  - [Reset](#reset)
  - [Save it to disk](#save-it-to-disk)
  - [Defaults](#defaults)
  - [What stays out of a store](#what-stays-out-of-a-store)
  - [Lifetime](#lifetime)

## Create a store

```py
from talon import actions

gk = actions.user.ui_elements_store("gk", {
    "game": None,
    "bindings": {},
})
```

Creates an arbitrary store named `gk` if it doesn't exist, seeded with initial values for "game" and "bindings".  If you call this a second time, you are just retrieving the store. The name cannot contain a `.`

Recommend calling this before initializing a UI

## Read it in a UI

We still use the `state` element to access the `store`. The only difference is we provide the full name with the `"<store>.<key>"` format.

The full name is `"<store>.<key>"`.

```py
def app():
    div, text, state = actions.user.ui_elements(["div", "text", "state"])
    game = state.get("gk.game")
    return div()[text(f"Game: {game}")]
```

`state.get`, `state.use` and `state.set` all work, and it rerenders like any other state. Nothing to pass to `ui_elements_show` - the `gk.` prefix does the routing.

## Read and write it anywhere

```py
gk.set("game", "celeste")
gk.set({"game": "celeste", "folder": "Celeste"})
gk.set("count", lambda count: count + 1)

gk.get("game")
gk.get("game", "default if unset")
gk.get_all()
```

Works with the UI open or closed. Open, it rerenders. Closed, it just stores the value.

## Talon actions

`.talon` files have no Python handle. The global state actions take the full name and route on the `gk.` prefix.

```
set game <user.text>: user.ui_elements_set_state("gk.game", text)
```

```py
actions.user.ui_elements_set_state("gk.game", "celeste")
actions.user.ui_elements_get_state("gk.game")
actions.user.ui_elements_get_state("gk.game", "default if unset")
```

Same writes as `gk.set`, `gk.subscribe` included.

`ui_elements_get_state` does not register a rerender dependency. Use it outside a render, and `state.get("gk.game")` inside one.

## Reset

```py
gk.reset()            # back to the seed
gk.reset(["game"])    # only these
gk.clear()            # empty it
```

## Save it to disk

ui_elements does not write files. Your package does, because a config file needs versioning, validation, and a plan for values that stopped making sense.

```py
gk.subscribe(lambda: save_config(gk.get_all()))
```

Runs after the values change, returns a function that unsubscribes. Load at startup with `gk.set(...)`.

## Defaults

A store's seed is its only default.

```py
state.get("gk.game", "celeste")
```

Returns `"celeste"` when the key is unset and does not write it, because renders never mutate a store. `initial_state` cannot seed a store key either - it warns and skips.

## What stays out of a store

`state.use_local` is always local. Its keys come from the component's position in the tree, so a reordered list would swap values between rows. To remember one, name it and lift it up:

```py
checkbox(checked=state.get("gk.spoilers"), on_change=on_spoilers)
```

## Lifetime

| | cleared when the UI hides | survives a Talon restart |
| -- | -- | -- |
| `state` | yes | no |
| `state.use_local` | yes | no |
| store | no | only if you save it |
