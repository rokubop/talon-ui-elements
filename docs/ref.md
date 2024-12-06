# Ref

`ref` is a reference to an element "id", which provides a way to imperatively get and set properties. Unlike React or Vue, `ref` is intended only for ids of elements, and DO cause reactive updates when set.

Example:
```py
screen, div, text, ref = actions.user.ui_elements(["screen", "div", "text", "ref"])

hello_ref = ref("hello")

return screen()[
    div()[
        text("Hello world", id="hello"),
    ],
]
```

We can now get any property from the `hello_ref`:
```py
print(hello_ref.text) # "Hello world"
print(hello_ref.color) # "FFFFFF"
print(hello_ref.background_color) # None
```

And we can set any property on the `hello_ref`, which will cause a reactive update:
```py
hello_ref.text = "New text"
hello_ref.color = "red"
hello_ref.background_color = "blue"
```

## `user.actions` vs `ref`
```py
text("Hello world", id="hello"),
```
| Talon `user.actions` | ref equivalent |
| --- | --- |
| `ui_elements_update_text("hello", "New text")` | `hello_ref.text = "New text"` |
| `ui_elements_update_property("hello", "color", "red")` | `hello_ref.color = "red"` |
| `ui_elements_get_input_value()` | `input_ref.value` |
| `ui_elements_highlight()` | `hello_ref.highlight()` |
| `ui_elements_highlight_briefly()` | `hello_ref.highlight_briefly()` |
| `ui_elements_unhighlight()` | `hello_ref.unhighlight()` |

Note: Updating text or highlighting renders on a separate decoration layer, and is more efficient than updating other properties. Other properties may cause a full rerender.