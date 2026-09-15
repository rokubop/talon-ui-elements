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

## Window Icon

You can display an icon in the title bar. It auto-scales to match the title font size. Pass a built-in icon name or a custom SVG element.

```python
# Built-in icon name
window(title="Settings", icon="settings")
```

```python
# Custom SVG
def my_window_ui():
    screen, window, div, text = actions.user.ui_elements(
        ["screen", "window", "div", "text"]
    )
    svg, path = actions.user.ui_elements_svg(["svg", "path"])

    return screen(justify_content="center", align_items="center")[
        window(
            title="My Window",
            icon=svg(fill="none", stroke="FF6600")[
                path(d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5")
            ]
        )[
            div(padding=16)[
                text("Window with custom icon", color="#FFFFFF")
            ]
        ]
    ]
```

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

## Click Outside

A window can react to a press that lands anywhere off it.

```python
window(
    title="My Window",
    minimize_on_click_outside=True,
    minimized_body=minimized_content,
)
```

- `minimize_on_click_outside=True` collapses it to the minimized body
- `close_on_click_outside=True` hides it
- `on_click_outside=callback` for anything else

Combine them and the declarative action runs first.

Anything inside the window's border counts as inside, text inputs included. Releasing off the window after a drag, resize or scrollbar grab does not count. While a `modal` is open anywhere in the tree, click outside is suppressed, because the modal owns dismissal.

The click still reaches whatever is underneath. For one that is consumed instead, use `modal` with `backdrop_click_close=True`. See [Mouse](./mouse.md).

## Modals in a window

A `modal` declared inside a window anchors to that window rather than the screen. It covers the window, centers on it, and follows it when dragged, onto another monitor included. With no enclosing window it covers the screen, as before.

```python
window(title="My Window")[
    div(padding=16)[text("Content")],
    modal(open=is_open, title="Confirm", on_close=close)[
        text("Centered on the window, not the screen")
    ],
]
```

It covers the title bar too. While a modal is open the title bar is inert anyway, so leaving it uncovered would show live-looking controls that do nothing.

## Minimize Flash

A window minimizes to a corner while the eye is elsewhere, so the collapse is easy to miss. Every window washes white on the way out. On by default.

```python
window(flash_on_minimize=False)                                   # off
window(flash_on_minimize="4a9af5AA")                              # colour
window(flash_on_minimize={"color": "4a9af5AA", "duration": 800})  # both
```

Defaults to `"FFFFFF59"` over 450ms. Covers the whole window, and fires on every minimize rather than just the first.

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
