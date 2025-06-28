# 🪟 Option Selector Tutorial

Build a flexible confirmation dialog and option selector system. Perfect for voice-activated choices, settings, and decision-making interfaces!

## What You'll Build

A modal-style interface for presenting choices and getting user input through voice commands or clicking.

## What You'll Learn

- Creating modal overlays and dialogs
- Building reusable choice interfaces
- Using callbacks for decision handling
- Creating confirmation workflows
- Modal positioning and styling

## Step 1: Basic Choice Interface

Let's start with a simple yes/no dialog. Create `option_selector.py`:

```python
from talon import actions

def option_selector_ui():
    div, screen, text, button, state = actions.user.ui_elements(["div", "screen", "text", "button", "state"])

    question = state.get("question", "Are you sure?")

    def handle_yes():
        print("User chose: Yes")
        actions.user.ui_elements_hide_all()

    def handle_no():
        print("User chose: No")
        actions.user.ui_elements_hide_all()

    return screen(
        justify_content="center",
        align_items="center",
        background_color="00000099"  # Semi-transparent overlay
    )[
        div(
            background_color="333333",
            padding=24,
            border_radius=8,
            gap=16,
            min_width=300
        )[
            text(question, color="FFFFFF", font_size=18, text_align="center"),

            div(flex_direction="row", gap=12, justify_content="center")[
                button(
                    "Yes",
                    background_color="4CAF50",
                    color="FFFFFF",
                    padding=12,
                    border_radius=4,
                    on_click=handle_yes,
                    min_width=80
                ),
                button(
                    "No",
                    background_color="F44336",
                    color="FFFFFF",
                    padding=12,
                    border_radius=4,
                    on_click=handle_no,
                    min_width=80
                )
            ]
        ]
    ]
```

**What's happening?**

- The screen has a semi-transparent background (`00000099`) creating a modal overlay
- `justify_content="center"` and `align_items="center"` center the dialog
- Each button has its own click handler that closes the dialog
- `min_width=80` ensures buttons are consistently sized

## Step 2: Make It More Flexible

Let's make it work with different types of choices:

```python
from talon import actions

def option_selector_ui():
    div, screen, text, button, state = actions.user.ui_elements(["div", "screen", "text", "button", "state"])

    question = state.get("question", "Make a choice:")
    options = state.get("options", ["Yes", "No"])
    callback = state.get("callback", None)

    def handle_choice(choice):
        print(f"User chose: {choice}")

        # Call the callback if provided
        if callback:
            callback(choice)

        actions.user.ui_elements_hide_all()

    return screen(
        justify_content="center",
        align_items="center",
        background_color="00000099"
    )[
        div(
            background_color="333333",
            padding=24,
            border_radius=8,
            gap=16,
            min_width=300
        )[
            text(question, color="FFFFFF", font_size=18, text_align="center"),

            div(
                flex_direction="row" if len(options) <= 3 else "column",
                gap=12,
                justify_content="center"
            )[
                *[
                    button(
                        option,
                        background_color="555555",
                        color="FFFFFF",
                        padding=12,
                        border_radius=4,
                        on_click=lambda opt=option: handle_choice(opt),
                        min_width=80
                    )
                    for option in options
                ]
            ]
        ]
    ]
```

**What's new?**

- `options = state.get("options", [...])` allows customizable choices
- `callback = state.get("callback", None)` allows custom response handling
- Dynamic layout: row for 3 or fewer options, column for more
- `lambda opt=option: handle_choice(opt)` captures each option correctly

## Step 3: Add Convenience Functions

Let's add helper functions to make it easy to use:

```python
from talon import Module, actions

mod = Module()

def option_selector_ui():
    # ... (same as Step 2) ...

@mod.action_class
class Actions:
    def show_option_selector(question: str, options: list, callback=None):
        """Show option selector with custom question and choices"""
        actions.user.ui_elements_set_state("question", question)
        actions.user.ui_elements_set_state("options", options)
        actions.user.ui_elements_set_state("callback", callback)
        actions.user.ui_elements_show(option_selector_ui)

    def show_yes_no_dialog(question: str, on_yes=None, on_no=None):
        """Show a simple yes/no confirmation dialog"""

        def handle_choice(choice):
            if choice == "Yes" and on_yes:
                on_yes()
            elif choice == "No" and on_no:
                on_no()

        actions.user.show_option_selector(question, ["Yes", "No"], handle_choice)

    def show_confirmation(message: str, action_to_confirm):
        """Show confirmation before executing an action"""

        def on_confirm():
            action_to_confirm()

        actions.user.show_yes_no_dialog(
            f"{message}\n\nAre you sure?",
            on_yes=on_confirm
        )

    def hide_option_selector():
        """Hide the option selector"""
        actions.user.ui_elements_hide_all()
```

**What's new?**

- `show_option_selector()` is the main flexible function
- `show_yes_no_dialog()` is a convenience wrapper for simple confirmations
- `show_confirmation()` adds a confirmation step before dangerous actions

## Step 4: Add Voice Commands

Create `option_selector.talon`:

```talon
# Basic commands
show selector: user.show_option_selector("What would you like to do?", ["Option 1", "Option 2", "Option 3"])
hide selector: user.hide_option_selector()

# Quick yes/no
confirm action: user.show_yes_no_dialog("Do you want to proceed?")

# Choice by voice (when selector is visible)
choose <user.text>: user.select_option_by_voice(text)
yes: user.select_option_by_voice("yes")
no: user.select_option_by_voice("no")
```

And add the voice selection function:

```python
# Add to your Actions class:
def select_option_by_voice(choice: str):
    """Select an option by voice when selector is visible"""
    options = actions.user.ui_elements_get_state("options", [])
    callback = actions.user.ui_elements_get_state("callback", None)

    # Find matching option (case-insensitive)
    choice_lower = choice.lower()
    for option in options:
        if option.lower() == choice_lower or option.lower().startswith(choice_lower):
            if callback:
                callback(option)
            actions.user.ui_elements_hide_all()
            return

    print(f"No option found matching '{choice}'")
```

## Step 5: Add Practical Examples

Here are some real-world usage examples:

```python
# Add to your Actions class:
def confirm_delete_file():
    """Confirm before deleting a file"""

    def delete_file():
        print("File deleted!")
        # Add actual file deletion logic here

    actions.user.show_confirmation(
        "This will permanently delete the file.",
        delete_file
    )

def choose_editor():
    """Let user choose their preferred editor"""

    def set_editor(editor):
        print(f"Editor set to: {editor}")
        # Save editor preference

    actions.user.show_option_selector(
        "Choose your preferred editor:",
        ["VS Code", "Vim", "Emacs", "Sublime Text"],
        set_editor
    )

def select_git_branch():
    """Choose a git branch to switch to"""

    branches = ["main", "development", "feature/new-ui", "bugfix/critical"]

    def switch_branch(branch):
        print(f"Switching to branch: {branch}")
        # Add git checkout logic here

    actions.user.show_option_selector(
        "Select branch to switch to:",
        branches,
        switch_branch
    )

def quick_action_menu():
    """Show a quick action menu"""

    def handle_action(action):
        if action == "Save All":
            print("Saving all files...")
        elif action == "Run Tests":
            print("Running tests...")
        elif action == "Deploy":
            actions.user.show_confirmation("Deploy to production?", lambda: print("Deploying..."))
        elif action == "Cancel":
            pass  # Just close

    actions.user.show_option_selector(
        "Quick Actions:",
        ["Save All", "Run Tests", "Deploy", "Cancel"],
        handle_action
    )
```

Add to your `.talon` file:

```talon
confirm delete: user.confirm_delete_file()
choose editor: user.choose_editor()
select branch: user.select_git_branch()
quick actions: user.quick_action_menu()
```

## Step 6: Add Styling Variants

Let's add different visual styles for different types of dialogs:

```python
def option_selector_ui():
    div, screen, text, button, state = actions.user.ui_elements(["div", "screen", "text", "button", "state"])

    question = state.get("question", "Make a choice:")
    options = state.get("options", ["Yes", "No"])
    callback = state.get("callback", None)
    style = state.get("style", "default")  # default, warning, info, success

    # Style configurations
    styles = {
        "default": {
            "bg": "333333",
            "button_bg": "555555",
            "title_color": "FFFFFF"
        },
        "warning": {
            "bg": "442222",
            "button_bg": "FF6B6B",
            "title_color": "FFCCCC"
        },
        "info": {
            "bg": "223344",
            "button_bg": "4ECDC4",
            "title_color": "CCE7FF"
        },
        "success": {
            "bg": "224422",
            "button_bg": "4CAF50",
            "title_color": "CCFFCC"
        }
    }

    current_style = styles.get(style, styles["default"])

    def handle_choice(choice):
        if callback:
            callback(choice)
        actions.user.ui_elements_hide_all()

    return screen(
        justify_content="center",
        align_items="center",
        background_color="00000099"
    )[
        div(
            background_color=current_style["bg"],
            padding=24,
            border_radius=8,
            gap=16,
            min_width=300,
            border=f"2px solid #{current_style['button_bg']}"
        )[
            text(
                question,
                color=current_style["title_color"],
                font_size=18,
                text_align="center"
            ),

            div(
                flex_direction="row" if len(options) <= 3 else "column",
                gap=12,
                justify_content="center"
            )[
                *[
                    button(
                        option,
                        background_color=current_style["button_bg"],
                        color="FFFFFF",
                        padding=12,
                        border_radius=4,
                        on_click=lambda opt=option: handle_choice(opt),
                        min_width=80
                    )
                    for option in options
                ]
            ]
        ]
    ]

# Update your convenience functions:
def show_warning_dialog(question: str, options: list, callback=None):
    """Show a warning-styled option selector"""
    actions.user.ui_elements_set_state("style", "warning")
    actions.user.show_option_selector(question, options, callback)

def show_info_dialog(question: str, options: list, callback=None):
    """Show an info-styled option selector"""
    actions.user.ui_elements_set_state("style", "info")
    actions.user.show_option_selector(question, options, callback)
```

## 🎉 Excellent Work!

You've built a complete, flexible dialog system! Here's what you mastered:

- ✅ **Modal dialogs** - Overlay interfaces that focus attention
- ✅ **Flexible option handling** - Dynamic choices and responses
- ✅ **Callback patterns** - Functions that respond to user choices
- ✅ **Voice integration** - Selecting options by speaking
- ✅ **Visual theming** - Different styles for different contexts
- ✅ **Practical patterns** - Real-world confirmation workflows

## Real-World Applications

This pattern is incredibly useful for:

- **Confirmation dialogs** - Before destructive actions
- **Settings selection** - Choosing preferences
- **Branch/file selection** - Picking from lists
- **Quick action menus** - Context-sensitive options
- **Error handling** - Giving users recovery choices

## Advanced Challenges

Ready to extend further? Try these:

1. **Keyboard shortcuts** - Number keys to select options quickly
2. **Auto-close timer** - Dismiss after inactivity
3. **Multiple selection** - Checkboxes for choosing multiple options
4. **Search filtering** - Type to filter long option lists
5. **Custom icons** - Visual indicators for different option types
6. **Animation** - Smooth show/hide transitions

## Next Tutorial

Want to build numeric interfaces? Try the **[Dual Counters](dual_counters.md)** tutorial to create interactive number controls and trackers!
