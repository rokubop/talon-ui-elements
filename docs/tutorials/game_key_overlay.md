# 🎮 Game Key Overlay Tutorial

Build a visual overlay showing game controls that you can toggle on and off during gameplay. Perfect for learning new games or streaming!

![Game Keys Preview](../../examples/game_keys_preview.png)

## Step 1: See full code
See [examples/game_keys_ui.py](../../examples/game_keys_ui.py) for the complete code.

Say "elements test" to see examples in action.

## Code Breakdown

**Reusable Functions**: Helper functions like `key()` and `key_icon()` let you create consistent buttons without repeating code. Each takes an `id` and content, returning a styled element.

**Class-Based Styling**: The `style()` call defines `.key` class properties that apply to all buttons with `class_name="key"`. Change `background_color`, `width`, `height`, etc. here to affect all keys at once.

**Screen Positioning**: The overlay appears in the bottom-right because `screen(justify_content="flex_end")` pushes content to the bottom. Use `"flex_start"` for top, `"center"` for middle, or add `align_items` to control horizontal positioning.

**IDs for Highlighting**: Each key gets a unique `id` (like `"up"`, `"space"`, `"q"`) - this is crucial because you'll use these exact strings with `actions.user.ui_elements_highlight("up")` to light up specific keys.

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