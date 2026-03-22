from talon import actions


def todo_list_ui():
    elements = [
        "div", "text", "button", "screen", "state",
        "input_text", "ref", "icon", "style", "checkbox", "window",
    ]
    div, text, button, screen, state, input_text, ref, icon, style, checkbox, window = (
        actions.user.ui_elements(elements)
    )

    items, set_items = state.use("items", [
        {"text": "Buy groceries", "done": False},
        {"text": "Walk the dog", "done": True},
        {"text": "Read a book", "done": False},
    ])
    add_input = ref("add_input")

    style({
        ".item": {
            "flex_direction": "row",
            "align_items": "center",
            "gap": 12,
            "padding": 10,
            "padding_left": 14,
            "padding_right": 10,
            "border_radius": 6,
            "background_color": "2A2A2A",
        },
        ".item_text": {
            "font_size": 15,
            "flex": 1,
        },
        ".delete_btn": {
            "padding": 6,
            "border_radius": 4,
            "highlight_style": {"background_color": "442222"},
        },
    })

    def add_item():
        new_text = add_input.value
        if new_text:
            set_items(items + [{"text": new_text, "done": False}])
            add_input.clear()
            add_input.focus()

    def toggle_done(index):
        updated = list(items)
        updated[index] = {**updated[index], "done": not updated[index]["done"]}
        set_items(updated)

    def delete_item(index):
        set_items([item for i, item in enumerate(items) if i != index])

    remaining = sum(1 for item in items if not item["done"])

    def render_item(item, index):
        return div(class_name="item")[
            checkbox(
                checked=item["done"],
                on_change=lambda e, i=index: toggle_done(i),
                color="4CAF50",
                size=18,
            ),
            text(
                item["text"],
                class_name="item_text",
                color="888888" if item["done"] else "EEEEEE",
                font_style="italic" if item["done"] else "normal",
            ),
            button(
                class_name="delete_btn",
                on_click=lambda e, i=index: delete_item(i),
            )[icon("trash", size=14, color="666666")],
        ]

    return screen(justify_content="center", align_items="center")[
        window(title="Todo List", width=360)[
            div(padding=4, gap=16)[
                div(flex_direction="row", justify_content="flex_end")[
                    text(
                        f"{remaining} remaining",
                        font_size=12,
                        color="888888",
                    ),
                ],
                div(gap=6, max_height=300, overflow_y="scroll")[
                    *[render_item(item, i) for i, item in enumerate(items)],
                    text(
                        "No items yet",
                        color="555555",
                        font_size=14,
                        padding=12,
                        text_align="center",
                    ) if not items else None,
                ],
                div(flex_direction="row", gap=8, border_top=1, border_color="333333", padding_top=16)[
                    input_text(
                        id="add_input",
                        autofocus=True,
                        placeholder="Add a new item...",
                        background_color="252525",
                        border_radius=6,
                        border_width=1,
                        border_color="333333",
                        flex=1,
                        padding=10,
                        font_size=14,
                    ),
                    button(
                        on_click=add_item,
                        border_radius=6,
                        padding=8,
                        highlight_style={"background_color": "333333"},
                    )[icon("plus", size=20, color="CCCCCC")],
                ],
            ],
        ]
    ]


def show_todo_list():
    actions.user.ui_elements_show(todo_list_ui)


def hide_todo_list():
    actions.user.ui_elements_hide(todo_list_ui)


def toggle_todo_list():
    actions.user.ui_elements_toggle(todo_list_ui)
