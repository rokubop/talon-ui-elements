# Store

`state` is cleared when a UI hides. A store is not.

Put data in a store when it still means something with no UI open: bindings, the selected game, an unsaved draft. Keep `state` for the window itself: active tab, selected row, is the sheet open.

- [Store](#store)
  - [Create one](#create-one)
  - [Read it in a UI](#read-it-in-a-ui)
  - [Read and write it anywhere](#read-and-write-it-anywhere)
  - [Reset](#reset)
  - [Save it to disk](#save-it-to-disk)
  - [Defaults](#defaults)
  - [What stays out of a store](#what-stays-out-of-a-store)
  - [Lifetime](#lifetime)

## Create one

```py
from talon import actions

gk = actions.user.ui_elements_store("gk", {
    "game": None,
    "bindings": {},
})
```

Module level, one per package. The name cannot contain a `.`.

The second argument seeds it. Existing values win, so saving the file picks up new keys without discarding what the user changed.

## Read it in a UI

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
