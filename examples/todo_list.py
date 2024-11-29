from talon import actions

def todo_list_ui():
    div, text, button, screen, state = actions.user.ui_elements(["div", "text", "button", "screen", "state"])

    items, set_items = state.use('items', [])

    def add_item():
        new_item = f"Item {len(items)}"
        set_items(items + [new_item])

    def delete_item(item_name):
        set_items([item for item in items if item != item_name])

    def item(item_name):
        return div(background_color="333333", justify_content="space_between", flex_direction="row", align_items="center", gap=8)[
            text(item_name, color="FFFFFF", font_size=16),
            button("X", background_color="FF0000", font_size=10, on_click=lambda: delete_item(item_name))
        ]

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=16, border_radius=8, gap=16, width=300)[
            text("Todo List", font_size=24),
            div(gap=8, max_height=300)[
                *(item(item_name) for item_name in items)
            ],
            button("Add Item", font_size=16, on_click=add_item)
        ]
    ]