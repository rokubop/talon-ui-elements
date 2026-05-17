"""
State testing playground.

Exercises controlled vs uncontrolled inputs and key-based component identity
in lists. Designed so visual behavior reveals correctness:

- Controlled section: parent flips state, the input must reflect it.
- Uncontrolled section: input owns its own state, persists across rerenders.
- Keyed list: reorder/delete - per-item check state must follow the item.
- Unkeyed list (control): same actions - state will leak by position. This
  exists to make the bug visible by comparison.
"""
from talon import actions


ACCENT = "3B82F6"
WINDOW_BG = "2D2D30"
PANEL_BG = "37373A"
BORDER = "454549"
TEXT_PRIMARY = "F0F0F0"
TEXT_SECONDARY = "A0A0A4"


def panel(div, text, title, *children):
    return div(
        background_color=PANEL_BG,
        padding=16,
        border_radius=8,
        border_width=1,
        border_color=BORDER,
        gap=12,
        flex=1,
    )[
        text(title, font_size=18, font_weight="bold", color=TEXT_PRIMARY),
        *children,
    ]


def row(div, *children, **kwargs):
    return div(flex_direction="row", align_items="center", gap=10, **kwargs)[*children]


def small_btn(button, label, on_click, **kwargs):
    return button(
        label,
        on_click=on_click,
        font_size=14,
        padding_top=4,
        padding_bottom=4,
        padding_left=10,
        padding_right=10,
        border_radius=4,
        background_color="4A4A4D",
        highlight_style={"background_color": "5A5A5D"},
        **kwargs,
    )


def state_counter_panel():
    div, text, button, state = actions.user.ui_elements(
        ["div", "text", "button", "state"]
    )
    count, set_count = state.use("counter_state", 0)

    return panel(
        div, text,
        "state",
        text(
            "Global reactive state. Causes a full rerender every time.",
            font_size=14, color=TEXT_SECONDARY,
        ),
        row(
            div,
            text(str(count), font_size=32, color=TEXT_PRIMARY),
            small_btn(button, "Increment", lambda e: set_count(count + 1)),
        ),
    )


def ref_counter_panel():
    div, text, button, ref = actions.user.ui_elements(
        ["div", "text", "button", "ref"]
    )
    text_ref = ref("ref_counter_text")

    def increment(e):
        text_ref.text = int(text_ref.text) + 1

    return panel(
        div, text,
        "ref",
        text(
            "Tied to a specific id. Direct reactive update of properties, no rerender.",
            font_size=14, color=TEXT_SECONDARY,
        ),
        row(
            div,
            text("0", id="ref_counter_text", font_size=32, color=TEXT_PRIMARY),
            small_btn(button, "Increment", increment),
        ),
    )


def controlled_checkbox_panel():
    div, text, button, checkbox, state = actions.user.ui_elements(
        ["div", "text", "button", "checkbox", "state"]
    )
    checked, set_checked = state.use("ctrl_cb", False)
    cb_id = "ctrl_cb_box"

    return panel(
        div, text,
        "Controlled checkbox",
        text(
            "Parent owns state. Toggle from either side.",
            font_size=14, color=TEXT_SECONDARY,
        ),
        row(
            div,
            checkbox(
                id=cb_id,
                checked=checked,
                on_change=lambda e: set_checked(e.checked),
                color="FFFFFF" if checked else ACCENT,
                background_color=ACCENT if checked else "1F1F22",
                border_width=1,
                border_color=ACCENT if checked else "6A6A70",
                border_radius=4,
                size=20,
            ),
            text(f"value: {checked}", for_id=cb_id, font_size=14, color=TEXT_PRIMARY),
            small_btn(button, "Flip from parent", lambda e: set_checked(not checked)),
        ),
    )


def uncontrolled_checkbox_panel():
    div, text, button, checkbox, state = actions.user.ui_elements(
        ["div", "text", "button", "checkbox", "state"]
    )
    rerenders, set_rerenders = state.use("uncon_cb_rerenders", 0)
    cb_id = "uncon_cb_box"

    return panel(
        div, text,
        "Uncontrolled checkbox",
        text(
            "No `checked` prop. Owns its own state via use_local.",
            font_size=14, color=TEXT_SECONDARY,
        ),
        row(
            div,
            checkbox(
                id=cb_id,
                color=ACCENT,
                background_color="1F1F22",
                border_width=1,
                border_color="6A6A70",
                border_radius=4,
                size=20,
            ),
            text(
                "click me to toggle",
                for_id=cb_id,
                font_size=14, color=TEXT_PRIMARY,
            ),
            text(
                f"(forced: {rerenders})",
                font_size=14, color=TEXT_SECONDARY,
            ),
            small_btn(button, "Force rerender", lambda e: set_rerenders(rerenders + 1)),
        ),
    )


def controlled_switch_panel():
    div, text, button, switch, state = actions.user.ui_elements(
        ["div", "text", "button", "switch", "state"]
    )
    on, set_on = state.use("ctrl_sw", False)
    sw_id = "ctrl_sw_box"

    return panel(
        div, text,
        "Controlled switch",
        text("Parent owns state. Toggle from either side.", font_size=14, color=TEXT_SECONDARY),
        row(
            div,
            switch(
                id=sw_id,
                checked=on,
                on_change=lambda e: set_on(e.checked),
                color=ACCENT,
                size=22,
            ),
            text(f"value: {on}", for_id=sw_id, font_size=14, color=TEXT_PRIMARY),
            small_btn(button, "Flip from parent", lambda e: set_on(not on)),
        ),
    )


def uncontrolled_switch_panel():
    div, text, button, switch, state = actions.user.ui_elements(
        ["div", "text", "button", "switch", "state"]
    )
    rerenders, set_rerenders = state.use("uncon_sw_rerenders", 0)
    sw_id = "uncon_sw_box"

    return panel(
        div, text,
        "Uncontrolled switch",
        text(
            "No `checked` prop. Owns its own state via use_local.",
            font_size=14, color=TEXT_SECONDARY,
        ),
        row(
            div,
            switch(id=sw_id, color=ACCENT, size=22),
            text("click me to toggle", for_id=sw_id, font_size=14, color=TEXT_PRIMARY),
            text(f"(forced: {rerenders})", font_size=14, color=TEXT_SECONDARY),
            small_btn(button, "Force rerender", lambda e: set_rerenders(rerenders + 1)),
        ),
    )


def controlled_input_panel():
    div, text, button, input_text, state = actions.user.ui_elements(
        ["div", "text", "button", "input_text", "state"]
    )
    value, set_value = state.use("ctrl_input", "")
    inp_id = "ctrl_input_box"

    return panel(
        div, text,
        "Controlled input_text",
        text(
            "Parent owns state via value=. EXPECT BUG today: 'Set from parent' does "
            "not flow back into the input (value= is only initial value).",
            font_size=14, color=TEXT_SECONDARY,
        ),
        input_text(
            id=inp_id,
            value=value,
            on_change=lambda e: set_value(e.value),
            placeholder="type here",
        ),
        row(
            div,
            text(f"state: {value!r}", font_size=14, color=TEXT_PRIMARY, flex=1),
            small_btn(button, "Set from parent", lambda e: set_value("from parent")),
            small_btn(button, "Clear from parent", lambda e: set_value("")),
        ),
    )


def uncontrolled_input_panel():
    div, text, button, input_text, ref = actions.user.ui_elements(
        ["div", "text", "button", "input_text", "ref"]
    )
    inp_ref = ref("uncon_input_box")

    return panel(
        div, text,
        "Uncontrolled input_text",
        text(
            "No value= echo. Input owns its state. Read/write imperatively via ref.",
            font_size=14, color=TEXT_SECONDARY,
        ),
        input_text(id="uncon_input_box", placeholder="type here"),
        row(
            div,
            small_btn(button, "Set via ref", lambda e: inp_ref.set_value("from ref")),
            small_btn(button, "Clear via ref", lambda e: inp_ref.clear()),
            small_btn(button, "Log via ref", lambda e: print(f"ref value: {inp_ref.value!r}")),
        ),
    )


def _move(items, idx, delta):
    j = idx + delta
    if 0 <= j < len(items):
        out = list(items)
        out[idx], out[j] = out[j], out[idx]
        return out
    return items


def list_panel(title, state_key, use_keys: bool):
    div, text, button, checkbox, state = actions.user.ui_elements(
        ["div", "text", "button", "checkbox", "state"]
    )
    items, set_items = state.use(state_key, [
        {"id": "a", "text": "Apple"},
        {"id": "b", "text": "Banana"},
        {"id": "c", "text": "Cherry"},
    ])

    def render_row(item, i):
        cb_id = f"{state_key}_cb_{item['id']}"
        # Uncontrolled checkbox so its state lives in use_local. That's the
        # state we want to follow the item across reorders/deletes.
        cb = checkbox(
            id=cb_id,
            color=ACCENT,
            background_color="1F1F22",
            border_width=1,
            border_color="6A6A70",
            border_radius=4,
            size=20,
        )
        row_kwargs = {"key": item["id"]} if use_keys else {}
        return div(
            padding_top=6, padding_bottom=6,
            flex_direction="row", align_items="center", gap=10,
            **row_kwargs,
        )[
            cb,
            text(item["text"], for_id=cb_id, font_size=15, color=TEXT_PRIMARY, flex=1),
            small_btn(button, "up",   lambda e, idx=i: set_items(_move(items, idx, -1))),
            small_btn(button, "down", lambda e, idx=i: set_items(_move(items, idx,  1))),
            small_btn(button, "x",    lambda e, idx=i: set_items([x for k, x in enumerate(items) if k != idx])),
        ]

    def reset():
        set_items([
            {"id": "a", "text": "Apple"},
            {"id": "b", "text": "Banana"},
            {"id": "c", "text": "Cherry"},
        ])

    description = (
        "Toggle a check, then move that item up/down. The check should follow the item."
        if use_keys
        else "Toggle a check, then move that item up/down. EXPECT BUG: the check stays at the original position (now a different item)."
    )

    return panel(
        div, text,
        title,
        text(description, font_size=13, color=TEXT_SECONDARY),
        *[render_row(item, i) for i, item in enumerate(items)],
        row(div, small_btn(button, "Reset", lambda e: reset()), justify_content="flex_end"),
    )


def state_tests_ui():
    screen, div, text, window = actions.user.ui_elements(
        ["screen", "div", "text", "window"]
    )

    return screen(justify_content="center", align_items="center")[
        window(title="State Tests", background_color=WINDOW_BG)[
            div(padding=24, gap=20)[
                text("State Tests", font_size=24, font_weight="bold", color=TEXT_PRIMARY),
                text(
                    "Visual harness for controlled/uncontrolled inputs and key-based identity in lists.",
                    font_size=14, color=TEXT_SECONDARY,
                ),
                div(flex_direction="row", gap=16)[
                    state_counter_panel(),
                    ref_counter_panel(),
                ],
                div(flex_direction="row", gap=16)[
                    controlled_checkbox_panel(),
                    uncontrolled_checkbox_panel(),
                ],
                div(flex_direction="row", gap=16)[
                    controlled_switch_panel(),
                    uncontrolled_switch_panel(),
                ],
                div(flex_direction="row", gap=16)[
                    controlled_input_panel(),
                    uncontrolled_input_panel(),
                ],
                div(flex_direction="row", gap=16)[
                    list_panel("Keyed list (expect: state follows item)", "keyed_items", use_keys=True),
                    list_panel("Unkeyed list (expect bug: state stuck to position)", "unkeyed_items", use_keys=False),
                ],
            ],
        ]
    ]


def show_state_tests():
    actions.user.ui_elements_show(state_tests_ui)


def hide_state_tests():
    actions.user.ui_elements_hide(state_tests_ui)


def toggle_state_tests():
    actions.user.ui_elements_toggle(state_tests_ui)
