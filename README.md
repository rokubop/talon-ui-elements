# ui_elements

[ui_elements](.) is an experimental library for building stateful voice activated overlays and UIs using HTML/CSS/React-like syntax, for use with [Talon](https://talonvoice.com/).

![ui_elements](./examples/ui_elements_preview.png)

- 8 Example UIs
- HTML-like elements such as `div`, `text`, `button`, `input_text`
- 40+ CSS-like properties such as `width`, `background_color`, `margin`, `padding_left`, `flex_direction`
- Reactive utilties `state`, `effect`, and `ref`
- Talon actions for setting text, highlighting elements, and changing state
- Voice activated hints displayed on all buttons and text inputs

## Prerequisites
- [Talon](https://talonvoice.com/)

## Installation
Download or clone this repository into your Talon user directory.

```sh
# mac and linux
cd ~/.talon/user

# windows
cd ~/AppData/Roaming/talon/user

git clone https://github.com/rokubop/talon-ui-elements.git
```

Done! 🎉 Say "elements test" to try out examples. Start learning below.

## Usage
Choose [elements](#elements) from `actions.user.ui_elements` and create a **renderer function** in any `.py` file in your Talon user directory.

```py
def hello_world_ui():
    screen, div, text = actions.user.ui_elements(["screen", "div", "text"])

    return screen()[
        div()[
            text("Hello world")
        ]
    ]
```

To define styles, we put it inside of the **parentheses**. To define children, we put it inside the **square brackets**.
```py
def hello_world_ui():
    screen, div, text = actions.user.ui_elements(["screen", "div", "text"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=16, border_radius=8, border_width=1)[
            text("Hello world", font_size=24)
        ]
    ]
```

Now we just need to show and hide it, so let's create two Talon actions. Here's the full `.py` code:
```py
from talon import Module, actions

mod = Module()

def hello_world_ui():
    screen, div, text = actions.user.ui_elements(["screen", "div", "text"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=16, border_radius=8, border_width=1)[
            text("Hello world", font_size=24)
        ]
    ]

@mod.action_class
class Actions:
    def show_hello_world():
        """Show hello world UI"""
        actions.user.ui_elements_show(hello_world_ui)

    def hide_hello_world():
        """Hide hello world UI"""
        actions.user.ui_elements_hide_all()
        # or actions.user.ui_elements_hide(hello_world_ui)
```

And in any `.talon` file:
```talon
show hello world: user.show_hello_world()
hide hello world: user.hide_hello_world()
```

Now when you say "show hello world", the UI should appear.

<p align="center">
  <img src="./examples/hello_world_preview.png" alt="hello_world" width="200"/>
</p>

Congratulations! You've created your first UI. 🎉

Start trying out properties to see how it changes. See all supported [properties](./docs/properties.md) for styling.

## Examples

Checkout out examples in the [examples](./examples) folder. Or say "elements test" to view live interactive examples.
| Example | Preview | Description |
|----|----|----|
| [alignment_ui](./examples/alignment_ui.py) | [preview](./examples/alignment_preview.png) |Showcase 9 different flexbox arrangements |
| [cheatsheet_ui](./examples/cheatsheet_ui.py) | [preview](./examples/cheatsheet_preview.png) | A list of commands on the left or right of your screen that can change state |
| [dashboard_ui](./examples/dashboard_ui.py) | [preview](./examples/dashboard_preview.png) | Has a title bar, a side bar, and a reactive body |
| [game_keys_ui](./examples/game_keys_ui.py) | [preview](./examples/game_keys_preview.png) | Game keys overlay for gaming, that highlights respective keys |
| [hello_world_ui](./examples/hello_world_ui.py) | [preview](./examples/hello_world_preview.png) | Simple hello world UI |
| [inputs_ui](./examples/inputs_ui.py) | [preview](./examples/inputs_preview.png) | Text input, ref, validation, and submit with a button |
| [state_vs_refs_ui](examples/state_vs_refs_ui.py) | [preview](./examples/state_vs_refs_preview.png) | Two versions of a counter using state or ref |
| [todo_list_ui](./examples/todo_list_ui.py) | [preview](./examples/todo_list_preview.png) | A todo list with an input, add, and remove functionality |


## Elements
returned from `actions.user.ui_elements`:

- `screen` - The root element. Basically a div the size of your screen.
- `div` - Standard container element.
- `text`
- `button`
- `input_text` - Uses Talon's experimental `TextArea` for input.
- `state` - Global reactive state that rerenders respective UIs when changed.
- `effect` - Run side effects on mount, unmount, or state change.
- `ref` - Reference to an element "id", which provides a way to imperatively get and set properties, with reactive updates. Useful for `input_text` value.

## Box Model
ui_elements have the same box model as normal HTML, with `margin`, `border`, `padding`, and `width` and `height` and operate under `box-sizing: border-box` assumption, meaning border and padding are included in the width and height.

## Flex by default
ui_elements are all `display: flex`, and default to `flex_direction="column"`with `align_items="stretch"`. This means when you don't provide anything, it will act similarly to `display: block`.

### Alignment examples
If you aren't familiar with flexbox, check out this [CSS Tricks Guide to Flexbox](https://css-tricks.com/snippets/css/a-guide-to-flexbox/).

Some examples:
```py
# children of screen will be bottom right
screen(align_items="flex_end", justify_content="flex_end")

# children of screen will be center
screen(align_items="center", justify_content="center")

# children of screen will be top left
screen(align_items="flex_start", justify_content="flex_start")

# children of screen will be top right
screen(flex_direction="row", align_items="flex_start", justify_content="flex_end")

# full width or height depending on flex_direction
div(flex=1)
```

See [alignment_ui](./examples/alignment_ui.py) for more.
## State

```py
..., state = actions.user.ui_elements([... "state"])

tab, set_tab = state.use("tab", 1)

# do conditional rendering with tab
```

`state.use` behaves like React’s `useState`. It returns a tuple (value, set_value). You must define a state key (e.g. `"tab"` in this case), so that `actions.user.ui_elements*` can also target it, and optionally a default value.

To change state, we can use `set_tab` from above, or we can use Talon actions:
```py
actions.user.ui_elements_set_state("tab", 2)
actions.user.ui_elements_set_state("tab", lambda tab: tab + 1)
```

State changes cause a full rerender (for now).


If the UI doesn't need a setter, than we can use `state.get`, which is just the value.

```py
tab = state.get("tab", 1)
```

Read more about [state](./docs/state.md).

### Disclaimer

If you just need to update text or highlight, use the below methods instead, as those render on a separate decoration layer which are faster, and do not cause a full rerender.

## Updating text
We must give a unique id to the thing we want to update.
```py
text("Hello world", id="test"),
```

Then we can use this action to update the text:
```py
actions.user.ui_elements_set_text("test", "New text")
```

Simple text updates like this render on a separate decoration layer, and are faster than a full rerender.

## Updating properties
We must give a unique id to the thing we want to update.

```py
div(id="box", background_color="FF0000")[
    text("Hello world"),
]
```

Then we can use `ui_elements_set_property` to update the properties.  Changes will cause a full rerender. (for now)
```py
actions.user.ui_elements_set_property("box", "background_color", "red")
actions.user.ui_elements_set_property("box", "width", "400")
actions.user.ui_elements_set_property("box", {
    "background_color": "red",
    "width": "400"
})
```

## Highlighting elements
```py
div(id="box")[
    text("Hello world"),
]
```

We can then use these actions to trigger a highlight or unhighlight, targeting an element with the id `"box"`:
```py
actions.user.ui_elements_highlight("box")
actions.user.ui_elements_highlight_briefly("box")
actions.user.ui_elements_unhighlight("box")
```

To use a custom highlight color, we can use the following property:
```py
div(id="box", highlight_color="FF0000")[
    text("Hello world"),
]
```

or we can specify the highlight color in the action:
```py
actions.user.ui_elements_highlight_briefly("box", "FF0000aa")
```

## Buttons
If you use a button, the UI will block the mouse instead of being pass through, and voice activated hints will automatially appear on the button.
```py
# button
button("Click me", on_click=lambda e: print("clicked")),
button("Click me", on_click=actions.user.ui_elements_hide_all),
```

## Text inputs
See [inputs_ui](./examples/inputs_ui.py) for example.

## Unpacking a list
```py
commands = [
    "left",
    "right",
    "up",
    "down"
]
div(gap=8)[
    text("Commands", font_weight="bold"),
    *[text(command) for command in commands]
],
```

## Opacity
```py
# 50% opacity
div(background_color="FF0000", opacity=0.5)[
    text("Hello world")
]

# or we can use the last 2 digits of the color
div(background_color="FF000088")[
    text("Hello world")
]
```

## Alternate screen
```py
# screen 1
screen(1, align_items="flex_end", justify_content="center")[
    div()[
        text("Hello world")
    ]
]
# or
screen(screen=2, align_items="flex_end", justify_content="center")[
    div()[
        text("Hello world")
    ]
]
```

## Documentation
| Documentation | Description |
|---------------|-------------|
| [Actions](./ui_elements.py) | Talon actions you can use (`actions.user.ui_elements*`) |
| [Defaults](./docs/defaults.md) | Default values for all properties |
| [Properties](./docs/properties.md) | List of all properties you can use |
| [Effect](./docs/effect.md) | Side effects on mount, unmount, or state change |
| [State](./docs/state.md) | Global reactive state that rerenders respective UIs when changed |
| [Ref](./docs/ref.md) | Reference to an element "id", which provides a way to imperatively get and set properties, with reactive updates |

## Development suggestions
While developing, you might get into a state where the UI gets stuck on your screen and you need to restart Talon. For this reason, it's recommended to have a "talon restart" command.

In a `.talon` file:
```
^talon restart$:            user.talon_restart()
```

Inside of a `.py` file:
```py
import os
from talon import Module, actions, ui

mod = Module()

@mod.action_class
class Actions:
    def talon_restart():
        """restart talon"""
        # for windows only
        talon_app = ui.apps(pid=os.getpid())[0]
        os.startfile(talon_app.exe)
        talon_app.quit()
```

- Sometimes the UI may not refresh after saving the file. Try hiding the UI, saving the file again, and showing again.

- Recommend using "Andreas Talon" VSCode extension + its dependency pokey command server, so you can get autocomplete for talon user actions, and hover over hint documentation on things like `actions.user.ui_elements()` or `actions.user.ui_elements_show()`.

## Under the hood
Uses Talon's `Canvas` and Skia canvas integration under the hood, along with Talon's experimental `TextArea` for input.

## Dependencies
none