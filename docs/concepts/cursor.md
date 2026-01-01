# Cursor

The `cursor` element follows your mouse and lets you display content at the cursor position.

## Text to the Right

```python
from talon import actions

def cursor_ui():
    screen, cursor, div, text = actions.user.ui_elements(
        ["screen", "cursor", "div", "text"]
    )

    return screen()[
        cursor()[
            div(
                position="absolute",
                left=20,
                background_color="#333333",
                padding=8,
                border_radius=4
            )[
                text("Command mode")
            ]
        ]
    ]
```

## Circle at Bottom Right

```python
from talon import actions

def cursor_ui():
    screen, cursor, svg, circle = actions.user.ui_elements(
        ["screen", "cursor", "svg", "circle"]
    )

    return screen()[
        cursor()[
            svg(position="absolute", left=20, top=20)[
                circle(r=8, cx=8, cy=8, fill="#FF0000")
            ]
        ]
    ]
```

## Refresh Rate

You can control how often the cursor position updates with `refresh_rate` (in milliseconds):

```python
cursor(refresh_rate=16)[  # Updates every 16ms (≈ 60 FPS)
    div(position="absolute", left=20)[
        text("Smooth")
    ]
]
```

The default is `16` milliseconds (about 60 FPS). Lower values update more frequently but use more resources.

## Show Briefly

You can show cursor UI temporarily with the `duration` parameter:

```python
from talon import actions

def flash_cursor():
    screen, cursor, svg, circle = actions.user.ui_elements(
        ["screen", "cursor", "svg", "circle"]
    )

    return screen()[
        cursor()[
            svg(position="absolute", left=20, top=20)[
                circle(r=12, cx=12, cy=12, fill="#00FF00")
            ]
        ]
    ]

# Show for 1 second then auto-hide
actions.user.ui_elements_show(flash_cursor, duration="1s")
```

This is useful for temporary visual feedback at the cursor position.
