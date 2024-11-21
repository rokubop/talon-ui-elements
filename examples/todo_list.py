from talon import actions

def todo_list_ui():
    div, text, button, screen, use_state = actions.user.ui_elements_new(["div", "text", "button", "screen", "use_state"])

    items, set_items = use_state('items', [])

    def add_item():
        new_item = f"Item {len(items)}"
        set_items(items + [new_item])

    def delete_item(item_name):
        set_items([item for item in items if item != item_name])

    def item(item_name):
        return div(background_color="333333", width=300, justify_content="justify_between", flex_direction="row", align_items="center", gap=8)[
            text(item_name, color="FFFFFF", font_size=16),
            button("X", background_color="FF0000", font_size=10, on_click=lambda: delete_item(item_name))
        ]

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=16, border_radius=8, gap=16, width=300)[
            text("Todo List", color="FFFFFF", font_size=24),
            div(background_color="333333", gap=8)[
                *(item(item_name) for item_name in items)
            ],
            button("Add Item", color="FFFFFF", font_size=16, on_click=add_item)
        ]
    ]