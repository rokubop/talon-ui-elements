# 🧭 Dashboard Tutorial

Build draggable, scrollable dashboard UI.

![Dashboard Preview](../../examples/dashboard_preview.png)

## Step 1: See full code
See [examples/dashboard_ui.py](../../examples/dashboard_ui.py) for the complete code.

Say "elements test" to see examples in action.

## Code Breakdown

**Window** - This pattern is used for showing a window.
```
screen()[
    window()[
        ...
    ]
]
```

**Layout**:
`screen(justify_content="center", align_items="center")` centers the window on the screen.

**Component**:
`component` is used to encapsulate `style`. Not actually necessary in this example, and `body()` instead of `component(body)` could be used and have the same effect.

**Scrolling**:
`overflow_y="scroll"` allows vertical scrolling of the content.

**Visibility**:
`dashboard_ui` is imported into another file, and visibily is controlled with `actions.user.ui_elements_show(dashboard_ui)`, `actions.user.ui_elements_hide(dashboard_ui)`, `actions.user.ui_elements_hide_all()`, or `actions.user.ui_elements_toggle(dashboard_ui)`.

For more information on setting up voice commands, see [hello_world.md](../tutorials/hello_world.md).