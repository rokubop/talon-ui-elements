# UI Elements

[ui_elements](.) is an experimental library for building stateful voice activated canvas UIs using a HTML/CSS/React-inspired syntax for python, for use with [Talon](https://talonvoice.com/).

![ui_elements](./examples/ui_elements_preview.png)

- 20+ elements like `div`, `button`, `screen`, `window`, `text`, `table`, `input_text`
- Highlight elements by ID
- Reactive `state` you can update with talon actions
- `effect` for side effects
- Dragging and scrolling
- No dependencies besides Talon

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


## ✨ What You Can Build - Full Tutorials

| Use Case |  |
|----------|---|
| 🎮 Game Key Overlay | [Start the tutorial →](docs/tutorials/game_key_overlay.md) |
| 📜 Command Cheatsheet | [Start the tutorial →](docs/tutorials/command_cheatsheet.md) |
| 🪟 Confirmation option selector | [Start the tutorial →](docs/tutorials/option_selector.md)
| 🔢 Counters | [Start the tutorial →](docs/tutorials/dual_counters.md) |
| 🧭 Compact dashboard | [Start the tutorial →](docs/tutorials/dashboard.md) |
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
- [Elements](docs/concepts/elements.md)
- [Properties](docs/concepts/properties.md)
- [Talon actions](docs/concepts/actions.md)
- [State and Reactivity](docs/concepts/state.md)
- [Components](docs/concepts/components.md)
- [Effect Hooks](docs/concepts/effect.md)
- [Ref Access](docs/concepts/ref.md)

## 🔍 More Examples

You can say `"elements test"` to open the built-in examples UI.

📂 See the [examples folder](./examples) for code and screenshots.

## 🧪 Development Tips

- Use `"talon open log"` while working
- Restart Talon if things don’t refresh
- Use `"talon restart"` voice command (see script →)