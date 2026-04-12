from talon import actions


ACCENT = "3B82F6"
ACCENT_HOVER = "60A5FA"
WINDOW_BG = "2D2D30"
INPUT_BG = "3A3A3D"
BORDER = "454549"
TEXT_PRIMARY = "F0F0F0"
TEXT_SECONDARY = "A0A0A4"
TEXT_MUTED = "707074"


def todo_list_ui():
    elements = [
        "div", "text", "button", "screen", "state",
        "input_text", "ref", "icon", "style", "checkbox", "window", "form",
    ]
    div, text, button, screen, state, input_text, ref, icon, style, checkbox, window, form = (
        actions.user.ui_elements(elements)
    )

    items, set_items = state.use("items", [
        {"id": "i1", "text": "Buy groceries", "done": False},
        {"id": "i2", "text": "Walk the dog", "done": True},
        {"id": "i3", "text": "Read a book", "done": False},
    ])
    next_id, set_next_id = state.use("next_id", 4)
    add_input = ref("add_input")

    style({
        ".item_row": {
            "flex_direction": "row",
            "align_items": "center",
            "gap": 14,
            "padding_top": 12,
            "padding_bottom": 12,
            "padding_left": 4,
            "padding_right": 4,
            "border_bottom": 1,
            "border_color": BORDER,
        },
        ".item_text": {
            "font_size": 16,
            "flex": 1,
        },
        ".delete_btn": {
            "padding": 6,
            "border_radius": 4,
            "highlight_style": {"background_color": "4A2929"},
        },
    })

    def add_item():
        new_text = (add_input.value or "").strip()
        if new_text:
            set_items(items + [{"id": f"i{next_id}", "text": new_text, "done": False}])
            set_next_id(next_id + 1)
            add_input.clear()
            add_input.focus()

    def toggle_done(item_id):
        set_items([
            {**item, "done": not item["done"]} if item["id"] == item_id else item
            for item in items
        ])

    def delete_item(item_id):
        set_items([item for item in items if item["id"] != item_id])

    def render_item(item):
        checked = item["done"]
        cb_id = f"todo_check_{item['id']}"
        item_id = item["id"]
        return div(key=item_id, class_name="item_row")[
            checkbox(
                id=cb_id,
                checked=checked,
                on_change=lambda e, i=item_id: toggle_done(i),
                color="FFFFFF" if checked else ACCENT,
                background_color=ACCENT if checked else "1F1F22",
                border_width=1,
                border_color=ACCENT if checked else "6A6A70",
                border_radius=4,
                size=20,
            ),
            text(
                item["text"],
                for_id=cb_id,
                class_name="item_text",
                color=TEXT_MUTED if item["done"] else TEXT_PRIMARY,
                font_style="italic" if item["done"] else "normal",
            ),
            button(
                class_name="delete_btn",
                on_click=lambda e, i=item_id: delete_item(i),
            )[icon("trash", size=18, color=TEXT_MUTED)],
        ]

    return screen(justify_content="center", align_items="center")[
        window(title="Todos", width=400, background_color=WINDOW_BG)[
            div(padding=24, gap=20)[
                text("Todos", font_size=24, font_weight="bold", padding_left=4, color=TEXT_PRIMARY),
                div(gap=0, max_height=320, overflow_y="scroll")[
                    *[render_item(item) for item in items],
                    text(
                        "No todos yet",
                        color=TEXT_MUTED,
                        font_size=16,
                        padding=20,
                        text_align="center",
                    ) if not items else None,
                ],
                form(on_submit=add_item, flex_direction="row", gap=8, width="100%")[
                    input_text(
                        id="add_input",
                        autofocus=True,
                        placeholder="What needs to be done?",
                        background_color=INPUT_BG,
                        border_radius=6,
                        border_width=1,
                        border_color=BORDER,
                        flex=1,
                        padding=10,
                        font_size=16,
                        color=TEXT_PRIMARY,
                    ),
                    button(
                        type="submit",
                        background_color=ACCENT,
                        border_radius=6,
                        padding=10,
                        padding_left=14,
                        padding_right=14,
                        highlight_style={"background_color": ACCENT_HOVER},
                    )[icon("plus", size=18, color="FFFFFF")],
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
