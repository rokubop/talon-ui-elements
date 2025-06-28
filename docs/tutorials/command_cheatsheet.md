# 📜 Command Cheatsheet Tutorial

Build a dynamic command reference that shows context-aware shortcuts. Perfect for learning new applications or remembering complex workflows!

## What You'll Build

A floating cheatsheet that displays different commands based on what you're doing. It updates automatically and can be positioned anywhere on screen.

![Cheatsheet Preview](../../examples/cheatsheet_preview.png)

## What You'll Learn

- Using reactive `state` for dynamic content
- Building context-aware interfaces
- Advanced positioning and alignment
- Creating professional reference overlays
- Updating UI content from voice commands

## Step 1: Start with Static Commands

Let's begin with a simple list of commands. Create `cheatsheet.py`:

```python
from talon import actions

def cheatsheet_ui():
    div, screen, text = actions.user.ui_elements(["div", "screen", "text"])

    commands = [
        "copy",
        "paste",
        "undo",
        "save"
    ]

    return screen()[
        div()[
            text("Commands", font_weight="bold"),
            *[text(command) for command in commands]
        ]
    ]
```

**What's happening?**

- `commands = [...]` creates a list of command names
- `*[text(command) for command in commands]` creates a text element for each command
- The `*` unpacks the list so each text element becomes a separate child

## Step 2: Make It Look Like a Real Cheatsheet

Cheatsheets should be easy to scan and positioned out of the way:

```python
from talon import actions

def cheatsheet_ui():
    div, screen, text = actions.user.ui_elements(["div", "screen", "text"])

    commands = [
        "copy",
        "paste",
        "undo",
        "save",
        "find",
        "replace"
    ]

    return screen(
        flex_direction="row",
        align_items="center",
        justify_content="flex_end"  # Position on the right
    )[
        div(
            background_color="333333DD",  # Semi-transparent
            padding=16,
            border_radius=8,
            margin=20,
            gap=8,
            min_width=150
        )[
            text("Commands", font_weight="bold", color="FFFFFF", margin_bottom=8),
            *[text(command, color="CCCCCC") for command in commands]
        ]
    ]
```

**What's new?**

- `flex_direction="row"` and `justify_content="flex_end"` positions on the right
- `background_color="333333DD"` adds transparency with "DD"
- `gap=8` adds consistent spacing between commands
- `min_width=150` ensures a minimum width for readability
- Different colors for title (`FFFFFF`) and commands (`CCCCCC`)

## Step 3: Make It Dynamic with State

This is where it gets interesting! Let's use `state` to make the commands update dynamically:

```python
from talon import actions

def cheatsheet_ui():
    div, screen, text, state = actions.user.ui_elements(["div", "screen", "text", "state"])

    # Get commands from state, with a default fallback
    commands = state.get("commands", [
        "copy",
        "paste",
        "undo",
        "save"
    ])

    return screen(
        flex_direction="row",
        align_items="center",
        justify_content="flex_end"
    )[
        div(
            background_color="333333DD",
            padding=16,
            border_radius=8,
            margin=20,
            gap=8,
            min_width=150
        )[
            text("Commands", font_weight="bold", color="FFFFFF", margin_bottom=8),
            *[text(command, color="CCCCCC") for command in commands]
        ]
    ]
```

**What's new?**

- `state = actions.user.ui_elements(["state"])` gives us access to reactive state
- `state.get("commands", [...])` gets the "commands" state value, with a default list
- Now the UI will automatically update when the commands state changes!

## Step 4: Add Functions to Update Commands

Let's add the ability to change what commands are shown:

```python
from talon import Module, actions

mod = Module()

def cheatsheet_ui():
    div, screen, text, state = actions.user.ui_elements(["div", "screen", "text", "state"])

    commands = state.get("commands", [
        "copy",
        "paste",
        "undo",
        "save"
    ])

    return screen(
        flex_direction="row",
        align_items="center",
        justify_content="flex_end"
    )[
        div(
            background_color="333333DD",
            padding=16,
            border_radius=8,
            margin=20,
            gap=8,
            min_width=150
        )[
            text("Commands", font_weight="bold", color="FFFFFF", margin_bottom=8),
            *[text(command, color="CCCCCC") for command in commands]
        ]
    ]

@mod.action_class
class Actions:
    def show_cheatsheet():
        """Show command cheatsheet"""
        actions.user.ui_elements_show(cheatsheet_ui)

    def hide_cheatsheet():
        """Hide command cheatsheet"""
        actions.user.ui_elements_hide_all()

    def set_coding_commands():
        """Show coding-related commands"""
        commands = [
            "comment line",
            "format document",
            "go to definition",
            "find references",
            "rename symbol",
            "toggle breakpoint"
        ]
        actions.user.ui_elements_set_state("commands", commands)

    def set_editing_commands():
        """Show text editing commands"""
        commands = [
            "select all",
            "copy line",
            "delete line",
            "duplicate line",
            "move line up",
            "move line down"
        ]
        actions.user.ui_elements_set_state("commands", commands)

    def set_navigation_commands():
        """Show navigation commands"""
        commands = [
            "go back",
            "go forward",
            "go to file",
            "go to line",
            "switch tab",
            "close tab"
        ]
        actions.user.ui_elements_set_state("commands", commands)
```

**What's new?**

- `actions.user.ui_elements_set_state("commands", commands)` updates the state
- Each function sets different command lists for different contexts
- The UI automatically updates when state changes!

## Step 5: Add Voice Commands for Context Switching

Create `cheatsheet.talon`:

```talon
show cheatsheet: user.show_cheatsheet()
hide cheatsheet: user.hide_cheatsheet()

coding commands: user.set_coding_commands()
editing commands: user.set_editing_commands()
navigation commands: user.set_navigation_commands()
```

Now you can say:
- "show cheatsheet" to display it
- "coding commands" to switch to coding shortcuts
- "editing commands" to switch to editing shortcuts
- etc.

## Step 6: Add Positioning Options

Let's make the position dynamic too:

```python
def cheatsheet_ui():
    div, screen, text, state = actions.user.ui_elements(["div", "screen", "text", "state"])

    commands = state.get("commands", [
        "copy", "paste", "undo", "save"
    ])

    # Get alignment preference from state
    align = state.get("align", "right")
    justify_content = "flex_end" if align == "right" else "flex_start"

    return screen(
        flex_direction="row",
        align_items="center",
        justify_content=justify_content
    )[
        div(
            id="cheatsheet",  # Add ID for easier targeting
            background_color="333333DD",
            padding=16,
            border_radius=8,
            margin=20,
            gap=8,
            min_width=150
        )[
            text("Commands", font_weight="bold", color="FFFFFF", margin_bottom=8),
            *[text(command, color="CCCCCC") for command in commands]
        ]
    ]

# Add to your Actions class:
def move_cheatsheet_left():
    """Move cheatsheet to left side"""
    actions.user.ui_elements_set_state("align", "left")

def move_cheatsheet_right():
    """Move cheatsheet to right side"""
    actions.user.ui_elements_set_state("align", "right")
```

Add to `cheatsheet.talon`:

```talon
move cheatsheet left: user.move_cheatsheet_left()
move cheatsheet right: user.move_cheatsheet_right()
```

## Step 7: Add Smart Context Detection (Advanced)

For a truly smart cheatsheet, you can detect the current application and show relevant commands automatically:

```python
# Add to your Actions class:
def update_cheatsheet_for_app():
    """Update cheatsheet based on current application"""
    from talon import ui

    try:
        active_app = ui.active_app()
        app_name = active_app.name.lower()

        if "code" in app_name or "vscode" in app_name:
            actions.user.set_coding_commands()
        elif "browser" in app_name or "chrome" in app_name or "firefox" in app_name:
            commands = [
                "new tab",
                "close tab",
                "refresh page",
                "go back",
                "go forward",
                "find in page"
            ]
            actions.user.ui_elements_set_state("commands", commands)
        else:
            actions.user.set_editing_commands()
    except:
        # Fallback to default commands
        pass
```

## 🎉 Congratulations!

You've built a sophisticated, context-aware command reference! Here's what you mastered:

- ✅ **Reactive state** - Making UIs that update automatically
- ✅ **Dynamic content** - Changing what's displayed based on context
- ✅ **State management** - Using `state.get()` and `ui_elements_set_state()`
- ✅ **Context switching** - Different command sets for different scenarios
- ✅ **Smart positioning** - User-controlled placement

## Real-World Usage Ideas

This pattern is incredibly useful for:

- **Application-specific shortcuts** - Show relevant commands for each app
- **Learning new tools** - Display available commands while using new software
- **Workflow assistance** - Context-aware help for complex tasks
- **Training others** - Show available voice commands during demos

## Advanced Challenges

Want to push further? Try these:

1. **Auto-hide timer** - Hide the cheatsheet after 30 seconds of inactivity
2. **Search functionality** - Filter commands by typing
3. **Categories** - Group commands into sections
4. **Favorites** - Let users star their most-used commands
5. **Export/Import** - Save custom command sets

## Next Tutorial

Ready for user interaction? Try the **[TODO List](todo_list.md)** tutorial to build a fully interactive task manager with inputs, buttons, and state management!
