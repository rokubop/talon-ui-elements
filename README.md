# UI Elements

[ui_elements](.) is an experimental library for building stateful voice activated canvas UIs using a HTML/CSS/React-inspired syntax for python, for use with [Talon](https://talonvoice.com/).

![ui_elements](./examples/ui_elements_preview.png)

## Features
- 20+ elements such as `div`, `text`, `button`, `table`, `icon`, `input_text`
- 90+ CSS-like properties such as `width`, `background_color`, `margin`, `padding_left`, `flex_direction`
- Reactive utilties `state`, `effect`, and `ref`
- Dragging and scrolling
- Talon actions for highlighting elements, changing state, setting text
- Voice activated hints
- Skia canvas based rendering

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

Done! 🎉 Start learning below.

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

## Examples

Say "elements test" to bring up the examples.

![examples](./examples/examples_preview.png)

## ✨ What You Can Build - Tutorials

| Use Case |  |
|----------|---|
| 📜 Command Cheatsheet | [Start the tutorial →](docs/tutorials/cheatsheet.md) |
| 🧭 Dashboard | [Start the tutorial →](docs/tutorials/dashboard.md) |
| 🎮 Game Key Overlay | [Start the tutorial →](docs/tutorials/game_key_overlay.md) |
| 📝 TODO list | [Start the tutorial →](docs/tutorials/todo_list.md) |

## 🚀 Your First UI in 3 Minutes

📘 [Start the Hello World tutorial →](docs/tutorials/hello_world.md)

You'll learn:
- How to create a renderer
- Show and hide it
- Style elements
- Use Talon commands

## 🛠️ Core Actions

```python
actions.user.ui_elements(...)       # Provides elements to compose your UI
actions.user.ui_elements_show(...)  # Show your UI
actions.user.ui_elements_hide(...)  # Hide your UI
```

### 5. Concepts and Reference
- [Talon actions](docs/concepts/actions.md)
- [Components](docs/concepts/components.md)
- [Defaults](docs/concepts/defaults.md)
- [Effect](docs/concepts/effect.md)
- [Elements](docs/concepts/elements.md)
- [Properties](docs/concepts/properties.md)
- [Ref](docs/concepts/ref.md)
- [Rendering](docs/concepts/rendering.md)
- [State](docs/concepts/state.md)

## 🔍 More Examples

You can say `"elements test"` to open the built-in examples UI.

📂 See the [examples folder](./examples) for code and screenshots.

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