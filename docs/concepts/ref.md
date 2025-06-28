# Ref

`ref` is a reference to an element "id", which provides a way to imperatively get and set properties. Values are not available on initial render, so they should only be used asynchronously via callbacks or after the initial render.

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