# Style

`style` lets you set styles for multiple elements at once instead of applying properties inline to each element.

## Basic Usage

```py
screen, div, text, style = actions.user.ui_elements(["screen", "div", "text", "style"])

style({
    "text": {
        "color": "FFFFFF",
        "font_size": 16
    }
})

return screen()[
    div()[
        text("Hello"),  # Automatically gets color and font_size
        text("World")   # This too
    ]
]
```

## Selector Types

### Universal Selector (`*`)

Apply styles to all elements:

```py
style({
    "*": {
        "highlight_color": "BBBBCC33",
        "focus_outline_color": "BBBBCC",
    }
})
```

### Element Type Selectors

Target specific element types:

```py
style({
    "text": {
        "color": "EEEEFF",
        "stroke_color": "000000",
        "stroke_width": 4
    },
    "button": {
        "padding": 12,
        "background_color": "333333"
    },
    "td": {
        "padding": 8,
    }
})
```

### Class Selectors

Target elements by `class_name`:

```py
style({
    ".key": {
        "padding": 8,
        "background_color": "#33333366",
        "width": 60,
        "height": 60,
        "opacity": 0.8,
    }
})

# Use with class_name property
div(class_name="key")[...]
```

## Nested Styles

You can nest special styles like `highlight_style`:

```py
style({
    ".key": {
        "background_color": "#333333",
        "highlight_style": {
            "background_color": "#44BCE799",
        },
    }
})
```

## Component Scoping

When used inside a `component()`, styles only apply within that component and won't leak outside:

```py
def styled_table():
    table, tr, td, style = actions.user.ui_elements(["table", "tr", "td", "style"])

    style({
        "td": {
            "padding": 8,
            "border_width": 1
        }
    })

    return table()[...]  # Styles only apply here

def table_component():
    component = actions.user.ui_elements(["component"])
    return component(styled_table)  # Styles won't affect elements outside
```

See [components.md](components.md) for more on component scoping.