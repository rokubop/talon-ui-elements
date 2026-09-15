# Store

`store` is similar to `state` but it persists across UI hide/shows. But does not survive Talon restarts.

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
  - [Reading the store](#reading-the-store)
  - [Read and write using the store variable](#read-and-write-using-the-store-variable)
  - [Talon actions](#talon-actions)
  - [Reset](#reset)
  - [Subscribe](#subscribe)
  - [Exempt](#exempt)

## Create a store

```py
from talon import actions

my_store = actions.user.ui_elements_store("my_store", {
    "game": None,
    "bindings": {},
})
```

Creates an arbitrary store named `my_store` if it doesn't exist, seeded with initial values.  If you call this a second time, you are just retrieving the store.

## Reading the store

We still use the `state` element to access the `store`. The only difference is we provide the full name with the `"<store>.<key>"` format.

The full name is `"<store>.<key>"`.

```py
def app():
    div, text, state = actions.user.ui_elements(["div", "text", "state"])
    game = state.get("my_store.game")
    return div()[text(f"Game: {game}")]
```

`state.get`, `state.use` and `state.set` all work, and it rerenders like any other state. Nothing to pass to `ui_elements_show` - the `my_store.` prefix does the routing.

## Read and write using the store variable

```py
my_store.set("game", "celeste")
my_store.set({"game": "celeste", "folder": "Celeste"})
my_store.set("count", lambda count: count + 1)

my_store.get("game")
my_store.get("game", "default if unset")
my_store.get_all()
```

Works with the UI open or closed. Open, it rerenders. Closed, it just stores the value.

## Talon actions

```
set game <user.text>: user.ui_elements_set_state("my_store.game", text)
```

```py
actions.user.ui_elements_set_state("my_store.game", "celeste")
actions.user.ui_elements_get_state("my_store.game")
actions.user.ui_elements_get_state("my_store.game", "default if unset")
```

Same writes as `my_store.set`, `my_store.subscribe` included.

`ui_elements_get_state` does not register a rerender dependency. Use it outside a render, and `state.get("my_store.game")` inside one.

## Reset

```py
my_store.reset()            # back to the seed
my_store.reset(["game"])    # only these
my_store.clear()            # empty it
```

## Subscribe

```py
my_store.subscribe(lambda: save_config(my_store.get_all()))
```

Runs after the values change, returns a function that unsubscribes. Load at startup with `my_store.set(...)`.

## Exempt

`state.use_local`