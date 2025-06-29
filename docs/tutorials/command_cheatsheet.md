# 📜 Command Cheatsheet Tutorial

Build a dynamic command reference that shows context-aware shortcuts. Perfect for learning new applications or remembering complex workflows!

![Cheatsheet Preview](../../examples/cheatsheet_preview.png)

## Step 1: See full code
See [examples/cheatsheet_ui.py](../../examples/cheatsheet_ui.py) for the complete code.

Say "elements test" to see examples in action.

## Code Breakdown

**Context-Aware Content**: The cheatsheet uses reactive `state` to show different commands based on your current context - whether you're coding, browsing, or using specific applications.

**Organized Layout**: Commands are grouped into logical sections with clear headers, making it easy to find what you need quickly. Each command shows both the voice trigger and description.

**Dynamic Updates**: Voice commands can update the cheatsheet content in real-time using `actions.user.ui_elements_set_state("current_commands", new_commands)` to show relevant shortcuts for your current task.

**Professional Styling**: The clean, card-based design with proper spacing and typography makes the cheatsheet easy to read at a glance without being distracting.

**Compact Format**: Each command entry uses a two-column layout showing the voice command on the left and description on the right, maximizing information density.

**Positioning**: The cheatsheet appears in a convenient location that doesn't interfere with your work while remaining easily accessible when needed.

**Using the Function**: Import this function into your Talon voice commands and control visibility with `actions.user.ui_elements_show(cheatsheet_ui)`, `actions.user.ui_elements_hide(cheatsheet_ui)`, `actions.user.ui_elements_hide_all()`, or `actions.user.ui_elements_toggle(cheatsheet_ui)`.

## Step 2: Setting Up Interaction

Use the following for visibility
```python
actions.user.ui_elements_show(cheatsheet_ui)
actions.user.ui_elements_hide(cheatsheet_ui)
actions.user.ui_elements_hide_all()
actions.user.ui_elements_toggle(cheatsheet_ui)
```

Update cheatsheet content dynamically
```python
actions.user.ui_elements_set_state("current_commands", new_commands_list)
actions.user.ui_elements_set_state("context_title", "VSCode Commands")
```

For more information on setting up voice commands, see [hello_world.md](../tutorials/hello_world.md).
