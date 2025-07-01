# 🎮 Game Key Overlay Tutorial

Build a visual overlay showing game controls that you can toggle on and off during gameplay. Perfect for learning new games or streaming!

![Game Keys Preview](../../examples/game_keys_preview.png)

## Step 1: See full code
See [examples/game_keys_ui.py](../../examples/game_keys_ui.py) for the complete code.

Say "elements test" to see examples in action.

## Code Breakdown

**Reusable Functions**: Abstracting helper functions like `key()` and `key_icon()` lets you create reusable code.

**Class-Based Styling**: We use `class_name="key"`, which can then be controlled by the `style()` element, defining the properties for `.key`, This is the same as if you defined the properties directly on the element, but allows for easier reuse and consistency across multiple elements.

**Screen Positioning**: All elements are `flex_direction="column"` by default, so `screen(justify_content="flex_end")` means that it in the vertical axis, it pushes the content to the bottom. Since `align_items` is not defined, it defaults to `flex_start`, which means the content is aligned to the left side of the screen.
- bottom right: `flex_direction="row", justify_content="flex_end", align_items="flex_end"`
- top right: `flex_direction="row", justify_content="flex_end", align_items="flex_start"`
- top left: (default) or `flex_direction="row", justify_content="flex_start", align_items="flex_start"`
- bottom left: `flex_direction="column", justify_content="flex_end", align_items="flex_end"`

If you use `"column"` instead of `"row"`, justify_content and align_items will refer to the opposite axis.

Use `margin` to offset the contents from the edges of the screen.

**IDs for Highlighting**: Each key gets a unique `id` (like `"up"`, `"space"`, `"q"`) - this is necessary to target it with talon actions such as `actions.user.ui_elements_highlight("up")` to light up specific keys.

**Text style**: The `text` uses `"stroke_color": "000000", "stroke_width": 4` to create an outline effect, you can remove this if you want. `"color"` controls the text color, `font_size` controls the size, and you can change `font_family` to use different fonts.

**Highlight Style**: The `highlight_style` property in the `.key` class controls what happens when a key is highlighted. Only colors can be set here. `background_color`or `color` can bet set to customize the highlight effect when you do `actions.user.ui_elements_highlight("id_of_key")`.

**Using the Function**: Import this function into your Talon voice commands and control visibility with
```python
actions.user.ui_elements_show(game_keys_ui)
actions.user.ui_elements_hide(game_keys_ui)
actions.user.ui_elements_hide_all()
actions.user.ui_elements_toggle(game_keys_ui)`
```

Use the following for highlighting and unhighlighting keys
```python
actions.user.ui_elements_highlight("id_of_key")
actions.user.ui_elements_highlight_briefly("id_of_key")
actions.user.ui_elements_unhighlight("id_of_key")
```

For more information on setting up voice commands, see [hello_world.md](../tutorials/hello_world.md).

Highlight actions render on the decoration layer, which is faster than state changes. See [Rendering](../concepts/rendering.md) for more details.