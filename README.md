# UI Elements

[ui_elements](.) is an experimental library for building stateful voice activated canvas UIs using a HTML/CSS/React-inspired syntax for python, for use with [Talon](https://talonvoice.com/).

![ui_elements](./examples/ui_elements_preview.png)

## Features
- 20+ elements such as `div`, `text`, `button`, `table`, `icon`, `input_text`, `cursor`
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

## Examples

Say "elements test" to bring up the examples.

![examples](./examples/examples_preview.png)

## ✨ Tutorials

| Use Case |  |
|----------|---|
| 👋 Hello World | [Start the tutorial →](docs/tutorials/hello_world.md) |
| 📜 Command Cheatsheet | [Start the tutorial →](docs/tutorials/cheatsheet.md) |
| 🧭 Dashboard | [Start the tutorial →](docs/tutorials/dashboard.md) |
| 🎮 Game Key Overlay | [Start the tutorial →](docs/tutorials/game_key_overlay.md) |
| 📝 TODO list | [Start the tutorial →](docs/tutorials/todo_list.md) |

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