# 📜 Command Cheatsheet Tutorial

![Cheatsheet Preview](../../examples/cheatsheet_preview.png)

## Step 1: See full code
See [examples/cheatsheet_ui.py](/examples/cheatsheet_ui.py) for the complete code.

Say "elements test" to see examples in action.

## Code Breakdown

### Root element
`screen` is the root element. It is basically a `div` that fills the screen, and is used to position the elements inside.

### Layout
Because the screen has `flex_direction="row"`, `justify_content` refers to the horizontal axis, and `align_items` refers to the vertical axis.

The initial value of `justify_content` is `"flex_end"` which means the contents are justified to the right side of the screen. `align_items="center"` means it is vertically centered in this case. These are common concepts in CSS Flexbox, and you can read more about them in the [Flexbox alignment](https://www.joshwcomeau.com/css/interactive-guide-to-flexbox/#alignment-3).

If you want to offset from the edge of the screen, you can use `padding` on the screen, or `margin` on the child element. For example, `div(margin_right=20)` would offset the content 20 pixels from the right edge of the screen.

### State
`state` initial value is actually set by another file in this case, during show, `user.ui_elements_show(cheatsheet_ui, initial_state={ "commands": ["Command 1", "Command 2", "Command 3"]})`, but it could have been defined directly in the ui with the second parameter `state.get("key", initial_value)` instead.

### Visibility
The `cheatsheet_ui` function is imported from another file, and visibility can be controlled with `actions.user.ui_elements_show(cheatsheet_ui)`, `actions.user.ui_elements_hide(cheatsheet_ui)`, `actions.user.ui_elements_hide_all()`, or `actions.user.ui_elements_toggle(cheatsheet_ui)`.

### IDs
The reason `div` is given an `id`, is because we want to do something dynamic with it. In this example we use `actions.user.ui_elements_set_property("cheatsheet", "background_color", value)` to dynamically set the background color on it. This could have been done with `state` as well, and would have been the same performance.

If instead you wanted to highlight the target id, you could use `actions.user.ui_elements_highlight("cheatsheet")` or `actions.user.ui_elements_highlight_briefly("cheatsheet")`, which is faster performance because highlight only affects the decoration layer and does not cause a full re-render.

### List comprehension
Use `*[text(command) for command in commands]` python pattern to render a list of `text` components dynamically. This is the same as if we had listed out `text("Command 1")`, `text("Command 2")`, etc. but allows for dynamic updates to the list without needing to change the UI code.

### Setting up actions
For more information on setting up voice commands, see [hello_world.md](../tutorials/hello_world.md).
