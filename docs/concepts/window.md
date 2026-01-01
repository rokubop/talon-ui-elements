# Window

The `window` element creates a draggable window with a title bar, minimize/maximize buttons, and a close button.

## Basic Window

```python
from talon import actions

def my_window_ui():
    screen, window, div, text = actions.user.ui_elements(
        ["screen", "window", "div", "text"]
    )

    return screen(justify_content="center", align_items="center")[
        window(
            title="My Window",
            background_color="#333333",
            min_width=400,
            min_height=300
        )[
            div(padding=16)[
                text("Window content goes here", color="#FFFFFF")
            ]
        ]
    ]
```

Windows are draggable by default. Click and drag the title bar to move them.

**Note:** This isn't a true OS window - it's a canvas overlay that displays on top of everything. When you click minimize, it doesn't minimize to the taskbar. Instead, it collapses to just show the title bar. You'll usually want to either provide a custom `minimized_body` (shown below) or hide the minimize button with `show_minimize=False`.

## Minimize and Restore

You can show different content when the window is minimized:

```python
from talon import actions

def minimized_content():
    div, text = actions.user.ui_elements(["div", "text"])
    return div(padding=8)[
        text("Minimized")
    ]

def my_window_ui():
    screen, window, div, text = actions.user.ui_elements(
        ["screen", "window", "div", "text"]
    )

    return screen(justify_content="center", align_items="center")[
        window(
            title="My Window",
            minimized_body=minimized_content,
            minimized_style={
                "position": "absolute",
                "top": 100,
                "right": 100
            }
        )[
            div(padding=16)[
                text("Full window content")
            ]
        ]
    ]
```

## Window Events

Use callbacks to handle window actions:

```python
def my_window_ui():
    screen, window, div, text, state = actions.user.ui_elements(
        ["screen", "window", "div", "text", "state"]
    )

    def on_close():
        print("Window closed")
        actions.user.ui_elements_hide(my_window_ui)

    def on_minimize():
        state.set("minimized", True)

    def on_restore():
        state.set("minimized", False)

    return screen(justify_content="center", align_items="center")[
        window(
            title="My Window",
            on_close=on_close,
            on_minimize=on_minimize,
            on_restore=on_restore
        )[
            div(padding=16)[
                text("Content")
            ]
        ]
    ]
```

The window element handles the minimize/maximize/close buttons automatically. You just provide the callbacks for what should happen.

## Customize Window Controls

You can hide the minimize button, close button, or entire title bar:

```python
def my_window_ui():
    screen, window, div, text = actions.user.ui_elements(
        ["screen", "window", "div", "text"]
    )

    return screen(justify_content="center", align_items="center")[
        window(
            title="Simple Window",
            show_minimize=False,  # Hide minimize button
            show_close=True,      # Show close button (default)
            show_title_bar=True   # Show title bar (default)
        )[
            div(padding=16)[
                text("No minimize button")
            ]
        ]
    ]
```

Set `show_title_bar=False` to hide the entire title bar and make the window fully custom.

## Additional Properties

See [Window-Specific Properties](../properties.md#window-specific-properties) for all available window properties like `show_title_bar`, `drag_title_bar_only`, `title_bar_style`, and more.
