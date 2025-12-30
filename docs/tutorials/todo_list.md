# 📝 TODO List Tutorial

Build a fully interactive task manager with real-time updates, input fields, and dynamic state management. This tutorial covers the most advanced UI patterns!

![TODO List Preview](../../examples/todo_list/todo_list_preview.png)

## Step 1: See full code
See [examples/todo_list_ui.py](../../examples/todo_list/todo_list_ui.py](../../examples/todo_list_ui.py) for the complete code.

Say "elements test" to see examples in action.

## Code Breakdown

**Interactive Components**: This tutorial combines multiple UI elements - `input_text` for adding tasks, `button` elements for actions, and dynamic list rendering for displaying tasks.

**State Management**: Uses `state.use('tasks', [...])` to create reactive state that automatically updates the UI when tasks are added or removed. This returns both the current value and a setter function.

**Event Handling**: Button `on_click` handlers execute functions that modify state, demonstrating how user interactions trigger UI updates in real-time.

**Ref System**: The `ref('new_task_input')` creates a reference to the input field, allowing programmatic access to `.value`, `.clear()`, and `.focus()` methods for smooth user experience.

**Dynamic Rendering**: Uses list comprehension `[task_item(task, lambda t=task: delete_task(t)) for task in tasks]` to render a variable number of task components based on current state.

**Form Patterns**: Demonstrates proper form handling with input validation, clearing fields after submission, and maintaining focus for continuous input.

**Component Structure**: Shows how to break down complex UIs into reusable components like `task_item()` that encapsulate both appearance and behavior.

**Using the Function**: Import this function into your Talon voice commands and control visibility with `actions.user.ui_elements_show(todo_list_ui)`, `actions.user.ui_elements_hide(todo_list_ui)`, `actions.user.ui_elements_hide_all()`, or `actions.user.ui_elements_toggle(todo_list_ui)`.

## Step 2: Setting Up Interaction

Use the following for visibility
```python
actions.user.ui_elements_show(todo_list_ui)
actions.user.ui_elements_hide(todo_list_ui)
actions.user.ui_elements_hide_all()
actions.user.ui_elements_toggle(todo_list_ui)
```

Interact with tasks using state
```python
actions.user.ui_elements_get_state("tasks", [])
actions.user.ui_elements_set_state("tasks", new_task_list)
```

For more information on setting up voice commands, see [hello_world.md](../tutorials/hello_world.md).

This is the most complex tutorial, showcasing advanced patterns like form handling, state management, and component composition that you can apply to any interactive application.
