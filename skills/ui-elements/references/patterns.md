# Patterns & Examples

## Conditional Rendering

Return `None` to skip rendering an element:

```python
div()[
    text("Always shown"),
    text("Only if active") if is_active else None,
    div(background_color="red")[text("Error")] if has_error else None,
]
```

## Tab Navigation

```python
def page_home():
    return div()[text("Home page")]

def page_settings():
    return div()[text("Settings page")]

TAB_PAGES = {
    "home": page_home,
    "settings": page_settings,
}

def my_app():
    div, text, button, screen, state, component = actions.user.ui_elements(
        ["div", "text", "button", "screen", "state", "component"]
    )
    tab, set_tab = state.use("tab", "home")

    return screen()[
        div()[
            div(flex_direction="row", gap=8)[
                *[button(
                    label,
                    on_click=lambda e, t=t: set_tab(t),
                    background_color="444444" if tab == t else "222222",
                ) for t, label in [("home", "Home"), ("settings", "Settings")]],
            ],
            component(TAB_PAGES[tab]),
        ]
    ]
```

## Splitting UI Across Files

```python
# ui/colors.py
BG_DARK = "1E1E1E"
BG_PANEL = "2A2A2A"
TEXT_DIM = "888888"

# ui/sidebar.py
from talon import actions
from .colors import BG_PANEL

def sidebar(items, selected, on_select):
    div, text, button = actions.user.ui_elements(["div", "text", "button"])
    return div(background_color=BG_PANEL, min_width=160, padding=8, gap=4)[
        *[button(
            item,
            on_click=lambda e, item=item: on_select(item),
            background_color="444444" if item == selected else None,
        ) for item in items]
    ]

# ui/app.py
from talon import actions
from .sidebar import sidebar

def my_app():
    div, text, screen, state = actions.user.ui_elements(["div", "text", "screen", "state"])
    selected, set_selected = state.use("selected", "item1")

    return screen()[
        div(flex_direction="row")[
            sidebar(["item1", "item2", "item3"], selected, set_selected),
            div(flex=1, padding=16)[text(f"Selected: {selected}")],
        ]
    ]
```

Helper functions that return elements are just regular Python functions - you don't need `component()`. Only use `component()` when you need `state.use_local` or scoped styles.

## Updating UI from Voice Commands

```python
# my_package.py (Talon actions)
@mod.action_class
class Actions:
    def my_update_data(new_data: list):
        """Push data into the UI"""
        actions.user.ui_elements_set_state("my_data", new_data)

    def my_toggle_ui():
        """Show/hide the UI"""
        actions.user.ui_elements_toggle(my_dashboard)

# ui.py
def my_dashboard():
    div, text, screen, state, effect = actions.user.ui_elements(
        ["div", "text", "screen", "state", "effect"]
    )
    items = state.get("my_data", [])

    def on_mount():
        actions.user.my_fetch_initial_data()

    effect(on_mount, [])

    return screen()[div()[*[text(item) for item in items]]]
```

## Common Layout Patterns

**Sidebar + Main Content:**
```python
div(flex_direction="row", height=600)[
    div(min_width=200, border_right=1, padding=16)[...],  # Sidebar
    div(flex=1, padding=16)[...],                          # Main content
]
```

**Header + Scrollable Body + Footer:**
```python
div(height=500)[
    div(padding=8)[text("Header")],                        # Fixed header
    div(flex=1, overflow_y="scroll", padding=8)[...],      # Scrollable body
    div(padding=8, border_top=1)[text("Footer")],          # Fixed footer
]
```

**Overlay / Floating Element:**
```python
div(position="relative")[
    div()[...],  # Normal content
    div(position="absolute", bottom=8, right=8)[
        text("Overlay badge")
    ],
]
```

## Complete Example: Todo List

```python
from talon import actions

def todo_list_ui():
    elements = ["div", "text", "button", "screen", "state", "input_text", "ref"]
    div, text, button, screen, state, input_text, ref = actions.user.ui_elements(elements)

    items, set_items = state.use('items', [])
    add_input = ref('add_input')

    def add_item():
        new_item = add_input.value
        if new_item:
            set_items(items + [new_item])
            add_input.clear()
            add_input.focus()

    def delete_item(item_name):
        set_items([item for item in items if item != item_name])

    def item(item_name):
        return div(background_color="333333", justify_content="space_between", flex_direction="row", align_items="center", gap=8)[
            text(item_name, color="FFFFFF", font_size=16),
            button("X", background_color="FF0000", font_size=10, on_click=lambda: delete_item(item_name), border_radius=2)
        ]

    return screen(justify_content="center", align_items="center")[
        div(draggable=True, background_color="333333", padding=16, border_radius=8, gap=16)[
            text("Todo list", font_size=24, padding=8),
            div(gap=8, max_height=300, margin_top=8)[
                *[item(item_name) for item_name in items]
            ],
            div(border_top=1, margin_top=8, padding_top=16, gap=16)[
                text("New Item", font_size=12, id="label"),
                div(flex_direction="row", gap=8)[
                    input_text(id="add_input", autofocus=True, background_color="222222", border_radius=4, width=200),
                    button("Add", on_click=add_item, background_color="42A5F5", border_radius=4, padding=12)
                ]
            ]
        ]
    ]
```

## Complete Example: Notification with Animation

```python
from talon import actions

def notification_ui():
    div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

    return screen(justify_content="center", align_items="center")[
        div(
            padding=15, background_color="#0088ffdd", border_radius=10,
            opacity=1.0, top=0, position="relative",
            mount_style={"opacity": 0, "top": 20},
            unmount_style={"opacity": 0, "top": 20},
            transition={"opacity": 300, "top": 300},
        )[
            text("Notification: saved!", font_size=20, color="white", font_weight="bold"),
        ],
    ]

def show_notification():
    actions.user.ui_elements_show(notification_ui, duration="2s")
```
