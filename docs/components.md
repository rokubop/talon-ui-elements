# Components

Components are for limiting render calculations when using `state`.

```py
def HelloImAComponent():
    ...

def hello_im_not_a_component():
    ...

screen()[
    div()[
        HelloImAComponent,
        hello_im_not_a_component()
    ]
]
```

`HelloImAComponent` in this example is a component, while `hello_im_not_a_component` is not.

## When to Use
When you you want to isolate `state` rerender calculations.

## How to Use
You can define a component in two ways:
1) Using it as a reference rather than calling it.
2) Explicitly wrapping it with the `component` element.

The only benefit of wrapping it with `component` is that you can pass additional arguments like `props` to it.

## Why Use?

The primary reason to use components is **performance optimization**. When state changes, components allow you to isolate rerendering calculations.

## Examples

### 1. Direct Function Reference

This is the simplest way to use a component. You define a function that returns the UI structure and pass it as a reference.

```python
def SimpleComponent():
    div, text, state = actions.user.ui_elements(["div", "text", "state"])

    count = state.get("count", 0)

    return div(flex_direction="column", gap=8)[
        text("Count", font_size=14, color="FFFFFF"),
        text(count, font_size=12, color="AAAAAA"),
    ]

# Usage
screen, window = actions.user.ui_elements(["screen", "window"])
screen()[
    window(title="Example Window")[
        SimpleComponent
    ]
]
```

In this example, `SimpleComponent` is passed as a reference, allowing it to be treated as a component during rendering. Using Pascal Case for the name helps indicate that it is a component.

---

### 2. Explicitly Wrapping a Component with `component`

When you need to pass additional arguments (props) to a component, you can wrap it explicitly using the `component` function.

```python
def StatefulComponent(props):
    div, text, button, state = actions.user.ui_elements(["div", "text", "button", "state"])
    count, set_count = state.use_local("count", 0)

    return div(flex_direction="column", gap=8)[
        text(props["title"], color="FFFFFF"),
        text(f"Count: {count}", font_size=14, color="FFFFFF"),
        button("Click to increment", font_size=12, color="AAAAAA", on_click=lambda: set_count(count + 1)),
    ]

# Wrapping the component to pass props
def ExampleWithComponent():
    div, component = actions.user.ui_elements(["div", "component"])
    return div(flex_direction="column", gap=8)[
        component(StatefulComponent, {
            "title": "Stateful Example"
        })
    ]
```

In this example:
- `StatefulComponent` is wrapped using the `component` function.
- Wrapping allows you to pass additional arguments (props) to the component.
- Regardless of using `state.get`, `state.get`, or `state.use_local`, rerender will try to limit to the containing component(s).

---

## Pascal Case Recommendation

To help distinguish components from non components, you may want to differentiate by using Pascal Case for components.

---
