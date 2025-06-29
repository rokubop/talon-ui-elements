# 🎮 Game Key Overlay Tutorial

Build a visual overlay showing game controls that you can toggle on and off during gameplay. Perfect for learning new games or streaming!

![Game Keys Preview](../../examples/game_keys_preview.png)

## Step 1: See full code
See [examples/game_keys_ui.py](../../examples/game_keys_ui.py) for the complete code.

Say "elements test" to see examples in action.

## Code Breakdown

**Reusable Functions**: Abstracting helper functions like `key()` and `key_icon()` lets you have consistency. Each takes an `id` and content, returning a styled element.

**Class-Based Styling**: We use `class_name="key"`, which can then be controlled by the `style()` element, defining the properties for `.key`.

**Screen Positioning**: All elements are `flex_direction="column"` by default, so `screen(justify_content="flex_end")` means that it in the vertical axis, it pushes the content to the bottom. Since `align_items` is not defined, it defaults to `flex_start`, which means the content is aligned to the left side of the screen.

**IDs for Highlighting**: Each key gets a unique `id` (like `"up"`, `"space"`, `"q"`) - this is necessary to target it with talon actions such as `actions.user.ui_elements_highlight("up")` to light up specific keys.

**Customizable Highlight Style**: The `highlight_style` property in the `.key` class controls what happens when a key is highlighted. Change `background_color` or add other properties to customize the highlight effect.

**Using the Function**: Import this function into your Talon voice commands and control visibility with `actions.user.ui_elements_show(game_keys_ui)`, `actions.user.ui_elements_hide(game_keys_ui)`, `actions.user.ui_elements_hide_all()`, or `actions.user.ui_elements_toggle(game_keys_ui)`.

## Step 2: Setting Up Interaction

Use the following for visibility
```python
actions.user.ui_elements_show(game_keys_ui)
actions.user.ui_elements_hide(game_keys_ui)
actions.user.ui_elements_hide_all()
actions.user.ui_elements_toggle(game_keys_ui)
```

Use the following for highlighting and unhighlighting keys
```python
actions.user.ui_elements_highlight("id_of_key")
actions.user.ui_elements_highlight_briefly("id_of_key")
actions.user.ui_elements_unhighlight("id_of_key")
```

For more information on setting up voice commands, see [hello_world.md](../tutorials/hello_world.md).

Highlight actions render on the decoration layer, which is faster than state changes. See [Rendering](../concepts/rendering.md) for more details.