# Ref

`ref` is a reference to an element "id", which provides a way to imperatively get and set properties. Unlike React or Vue, `ref` is intended only for ids of elements, and DO cause reactive updates when set.

Example:
```py
screen, div, text, ref = actions.user.ui_elements(["screen", "div", "text", "ref"])

hello_ref = ref("hello") # id="hello"

return screen()[
    div()[
        text("Hello world", id="hello"),
    ],
]
```

We can now get any attribute/property from the `hello_ref`:
```py
print(hello_ref.text) # "Hello world"
print(hello_ref.color) # "FFFFFF"
print(hello_ref.background_color) # None
```

If we set an attribute/property on `hello_ref`, it will cause a reactive update:
```py
hello_ref.text = "New text"
hello_ref.color = "red"
hello_ref.background_color = "blue"

# Rerenders
```

## With inputs

```py
screen, div, input_text, ref = actions.user.ui_elements(["screen", "div", "input_text", "ref"])

input_ref = ref("input_id")

def submit():
    print(input_ref.value)

return screen()[
    div()[
        input_text("Type here", id="input_id"),
        button("Submit", on_click=submit),
    ],
]
```

To clear the input, we can set the value to an empty string, or use the `clear` method:
```py
input_ref.value = ""
# or
input_ref.clear()
```

## Scrolling and overflow

Use `scroll_to` to scroll to position
```py
hello_ref = ref("hello_id")
hello_ref.scroll_to(0, 0) # x, y
```

## `user.actions` vs `ref`
```py
text("Hello world", id="hello_id"),
```
| Talon `user.actions` | ref equivalent |
| --- | --- |
| `ui_elements_set_text("hello", "New text")` | `hello_ref.text = "New text"` |
| `ui_elements_update_property("hello", "color", "red")` | `hello_ref.color = "red"` |
| `ui_elements_get_input_value()` | `input_ref.value` |
| `ui_elements_highlight()` | `hello_ref.highlight()` |
| `ui_elements_highlight_briefly()` | `hello_ref.highlight_briefly()` |
| `ui_elements_unhighlight()` | `hello_ref.unhighlight()` |