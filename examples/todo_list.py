from talon import actions

def todo_list_ui():
    elements = ["div", "text", "button", "screen", "state", "input_text", "ref"]
    div, text, button, screen, state, input_text, ref = actions.user.ui_elements(elements)

    items, set_items = state.use('items', [])
    add_input = ref('add')

    def add_item():
        item_name = add_input.value
        new_item = item_name or f"Item {len(items)}"
        set_items(items + [new_item])
        add_input.clear()

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
            text("New Item", font_size=12),
            input_text(id="add", background_color="111111", border_radius=4),
            button("Add Item", font_size=16, on_click=add_item)
        ]
    ]