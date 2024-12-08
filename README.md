# ui_elements

ui_elements is an experimental library for building stateful voice activated overlays and UIs using HTML/CSS/React-like syntax. For use with Talon.

## Usage
Choose [elements](#elements) from `actions.user.ui_elements` and create a renderer function

```py
def hello_world_ui():
    (screen, div, text) = actions.user.ui_elements(["screen", "div", "text"])

    return screen()[
        div()[
            text("Hello world")
        ]
    ]

actions.user.ui_elements_show(hello_world_ui)
```

To define styles, we put it inside of the **parentheses**. To define children, we put it inside the **square brackets**.
```py
def hello_world_ui():
    (screen, div, text) = actions.user.ui_elements(["screen", "div", "text"])

    return screen(align_items="flex_end", justify_content="center")[
        div(gap=24)[
            text("Hello world", font_size=24, color="FF0000"),
            text("Cool")
        ]
    ]

actions.user.ui_elements_show(hello_world_ui)
```

To hide and destroy the UI:
```py
actions.user.ui_elements_hide(hello_world_ui)
# or
actions.user.ui_elements_hide_all()
```


## Elements
- `screen` - The root element. Basically a div the size of your screen.
- `div` - Standard container element.
- `text`
- `button`
- `input_text` - Uses Talon's experimental `TextArea` for input.
- `state` - Global reactive state that rerenders respective UIs when changed.
- `effect` - Run side effects on mount, unmount, or state change.
- `ref` - Reference to an element "id", which provides a way to imperatively get and set properties, with reactive updates.

## Examples
Say 'elements test' to view live examples.
Checkout the examples here: [examples.py](./examples.py)

## Box Model
ui_elements have the same box model as normal HTML, with `padding`, `margin`, `border`, and `width` and `height` and operate under `box-sizing: border-box` assumption, meaning padding and border are included in the width and height.

## Flex by default
Most ui_elements operate under `display: flex` assumption, and default to `flex_direction="column"`with `align_items="stretch"`. This means when you don't provide anything, it will act similarly to `display: block`.

## Alignment examples
```py
# children of screen will be bottom right
screen(align_items="flex_end", justify_content="flex_end")

# children of screen will be center
screen(align_items="center", justify_content="center")

# children of screen will be top left
screen(align_items="flex_start", justify_content="flex_start")

# children of screen will be top right
screen(flex_direction="row", align_items="flex_start", justify_content="flex_end")

# full width or height depending on flex_direction
div(flex=1)
```

## Updating text
We must give a unique id to the thing we want to update.
```py
text("Hello world", id="test"),
```

Then we can use this action to update the text:
```py
actions.user.ui_elements_update_text("test", "New text")
```

## Highlighting elements
We must give a unique id to the thing we want to highlight.
```py
div(id="box")[
    text("Hello world"),
]
```

We can then use these actions to trigger a highlight or unhighlight:
```py
actions.user.ui_elements_highlight("box")
actions.user.ui_elements_highlight_briefly("box")
actions.user.ui_elements_unhighlight("box")

# highlight color FF0000 with transparency of aa
actions.user.ui_elements_highlight_briefly("box", "FF0000aa")
```

## Buttons
If you use a button, the UI will block the mouse instead of being pass through.
```py
# button
button("Click me", on_click=lambda: print("clicked")),
button("Click me", on_click=actions.user.hide_my_custom_ui),
```

## Text inputs
```py
div()[
    input_text(id="your_name", on_change=lambda value: print(value)),
],

# later
actions.user.ui_elements_get_value("your_name")
```

## Unpacking a list into elements
```py
commands = [
    "left",
    "right",
    "up",
    "down"
]
div(gap=8)[
    text("Commands", font_weight="bold"),
    *[text(command) for command in commands]
],
```

## Opacity
```py
# 50% opacity
div(background_color="FF0000", opacity=0.5)[
    text("Hello world")
]

# or we can use the last 2 digits of the color
div(background_color="FF000088")[
    text("Hello world")
]
```

## Alternate screen
```py
# screen 1
screen(1, align_items="flex_end", justify_content="center")[
    div()[
        text("Hello world")
    ]
]
# or
screen(screen=2, align_items="flex_end", justify_content="center")[
    div()[
        text("Hello world")
    ]
]
```

## On mount

It it takes time to render the UI, you can use `on_mount` to know when it's done.

```py
def on_mount():
    print("Mounted")

my_ui = screen()[
    div()[
        text("Hello world")
    ]
]

my_ui.show(on_mount)
```

## Properties

| Property | Type |
| -- | -- |
| align_items | `'flex_start'`, `'flex_end'`, `'center'` |
| background_color | `str` - 6-digit hexadecimal with 2 optional digits for opacity e.g. `'FF0000'` or `FF000088` for opacity of `88` from `00` to `FF` |
| border_color | `str` |
| border_radius | `int` - for rounded corners |
| border_bottom | `int` - border bottom only width |
| border_left | `int` - border left only width |
| border_right | `int` - border right only width |
| border_top | `int` - border top only width |
| border_width | `int` - for border on all sides |
| bottom | `int` |
| color | `str` - 6-digit hexadecimal with 2 optional digits for opacity e.g. `'FF0000'` or `FF000088` for opacity of `88` from `00` to `FF` |
| flex | `int` - 1 for full width |
| flex_direction | `'row'`, `'column'` |
| font_size | `int` - for text |
| font_weight | `str` - e.g. `'bold'` |
| gap | `int` - gap between children |
| height | `int` |
| highlight_color | `str` - 6-digit hexadecimal with 2 optional digits for opacity e.g. `'FF0000'` or `FF000088` for opacity of `88` from `00` to `FF`. Only works for screen component at the moment. |
| id | `str` - Required on builder, and for 'highlight' feature to work on a div |
| justify | `str` |
| justify_content | `'flex_start'`, `'flex_end'`, `'center'` |
| left | `int` |
| margin | `int` - Margin in every direction |
| margin_bottom | `int` |
| margin_left | `int` |
| margin_right | `int` |
| margin_top | `int` |
| on_click | `Callable[[], None]` - Callback function to call when button is clicked. Takes 0 arguments. |
| on_change | `Callable[[str], None]` - Callback function to call when value of input changes. Takes 1 argument for the current value. |
| opacity | `float` - 0.0 to 1.0. Or you can use the last 2 digits of the color instead of opacity |
| padding | `int` - Padding in every direction |
| padding_bottom | `int` |
| padding_left | `int` |
| padding_right | `int` |
| padding_top | `int` |
| right | `int` |
| screen | `int` - Screen number (only applicable to screen element). Defaults to main screen if omitted. |
| top | `int` |
| value | `str` - For input |
| width | `int` |

## Actions
| **Action** | **Description** |
|------------|-----------------|
| `ui_elements` | This acts like an import for the components you want to use. div, text, screen, button, input_text. |
| `ui_elements_screen` | Only the screen ui element. Has .show() method. Give it an id if you want to specifically hide it later with actions.user.ui_elements_hide(id) |
| `ui_elements_hide` | Hide and destroys a ui_element based on the id assigned to the screen ui_element |
| `ui_elements_hide_all` | Hide and destroys all currently active ui_elements |
| `ui_elements_set_text` | set text based on id |
| `ui_elements_highlight` | highlight based on id |
| `ui_elements_unhighlight` | unhighlight based on id |
| `ui_elements_highlight_briefly` | highlight briefly based on id |
| `ui_elements_get` | Get the UI builder with the given ID. Only for informational purposes. Not for mutation. |
| `ui_elements_get_value` | Get value of an input based on id |
| `ui_elements_register_on_lifecycle` | Register a callback to be called on mount or unmount |
| `ui_elements_unregister_on_lifecycle` | Unregister a lifecycle callback |

## Dependencies
none