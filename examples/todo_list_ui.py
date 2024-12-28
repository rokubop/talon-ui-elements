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

    def delete_item(item_name):
        set_items([item for item in items if item != item_name])

    def item(item_name):
        return div(background_color="333333", justify_content="space_between", flex_direction="row", align_items="center", gap=8)[
            text(item_name, color="FFFFFF", font_size=16),
            button("X", background_color="FF0000", font_size=10, on_click=lambda: delete_item(item_name), border_radius=2)
        ]

    return screen(justify_content="center", align_items="center")[
        div(background_color="333333", padding=16, border_radius=8, gap=16)[
            text("Todo list", font_size=24, padding=8),
            div(gap=8, max_height=300, margin_top=8)[
                *[item(item_name) for item_name in items]
            ],
            div(border_top=1, margin_top=8, padding_top=16, gap=16)[
                text("New Item", font_size=12, id="label"),
                div(flex_direction="row", gap=8)[
                    input_text(id="add_input", background_color="222222", border_radius=4, width=200),
                    button("Add", on_click=add_item, background_color="42A5F5", border_radius=4, padding=12)
                ]
            ]
        ]
    ]