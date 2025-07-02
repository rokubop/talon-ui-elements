# 🚀 Your First UI in 5 Minutes

Welcome to UI Elements! In this tutorial, you'll create your first voice-activated UI from scratch. Don't worry if you're new to programming or Talon - we'll guide you through every step.

## What You'll Build

A simple "Hello World" UI that you can show and hide with voice commands.

![Hello World Preview](../../examples/hello_world_preview.png)

## What You'll Learn

- How to create a renderer function
- Basic UI structure with `screen`, `div`, and `text`
- How to style elements
- How to show and hide your UI
- How to add voice commands

## Step 1: Create Your First File

Create a new file in your Talon user directory called `hello_world.py`:

```python
from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen()[
        div()[
            text("Hello world")
        ]
    ]
```

**What's happening here?**

- `actions.user.ui_elements()` gives us the building blocks we need
- `screen()` is like the canvas - it fills your entire screen
- `div()` is a container (like a box)
- `text()` displays text
- The `[]` after each element contains its children
- The `()` after each element contains its styling (we'll add that next)

## Step 2: Add Some Style

Let's make it look better by adding styling inside the parentheses:

```python
from talon import actions

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="#333333", padding=16, border_radius=8)[
            text("Hello world", font_size=24, color="#FFFFFF")
        ]
    ]
```

**What's new?**

- `justify_content="center"` and `align_items="center"` center the div on screen
- `background_color="#333333"` gives the div a dark gray background
- `padding=16` adds space inside the div around the text
- `border_radius=8` rounds the corners
- `font_size=24` makes the text bigger
- `color="#FFFFFF"` makes the text white

## Step 3: Add Show/Hide Functions

Now let's add functions to show and hide the UI:

```python
from talon import Module, actions

mod = Module()

def hello_world_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=16, border_radius=8)[
            text("Hello world", font_size=24, color="FFFFFF")
        ]
    ]

@mod.action_class
class Actions:
    def show_hello_world():
        """Show hello world UI"""
        actions.user.ui_elements_show(hello_world_ui)

    def hide_hello_world():
        """Hide hello world UI"""
        actions.user.ui_elements_hide_all()
```

**What's new?**

- `Module()` and `@mod.action_class` create Talon actions you can call
- `actions.user.ui_elements_show()` displays your UI
- `actions.user.ui_elements_hide_all()` hides all UIs

## Step 4: Add Voice Commands

Create a second file called `hello_world.talon` to add voice commands:

```talon
show hello world: user.show_hello_world()
hide hello world: user.hide_hello_world()
```

**What's happening?**

- When you say "show hello world", it calls `user.show_hello_world()`
- When you say "hide hello world", it calls `user.hide_hello_world()`

## Step 5: Test It Out!

1. Save both files
2. Say "show hello world" - your UI should appear!
3. Say "hide hello world" - it should disappear

## Step 6: Troubleshooting
If it doesn't work:
- Open and monitor the talon log for feedback on errors: say "talon open log" and check for errors
- Make sure both files are saved in your Talon user directory
- Try saving the files again to reload them
- Try restarting Talon if there are any breaking issues

## 🎉 Congratulations!

You've created your first UI! Here's what you accomplished:

- ✅ Created a renderer function
- ✅ Used basic elements (`screen`, `div`, `text`)
- ✅ Added styling with properties
- ✅ Connected it to Talon actions
- ✅ Added voice commands

## Next Steps

Now that you understand the basics, try these tutorials:

- **[Game Key Overlay](game_key_overlay.md)** - Build a visual key overlay for gaming
- **[Command Cheatsheet](cheatsheet.md)** - Create a dynamic command reference
- **[TODO List](todo_list.md)** - Build an interactive task manager

## Resources
**Need help?**
- Look at the [concepts documentation](../concepts/) for deeper understanding
