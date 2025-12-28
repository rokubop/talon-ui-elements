from talon import actions
from ..common import example_with_code, code
import textwrap

def checkbox_stories():
    component, div, text, checkbox, icon, input_text = actions.user.ui_elements([
        "component", "div", "text", "checkbox", "icon", "input_text"
    ])
    state = actions.user.ui_elements("state")

    # State management example with different default values
    notifications_enabled, set_notifications_enabled = state.use("notifications_enabled", False)
    dark_mode, set_dark_mode = state.use("dark_mode", True)
    auto_save, set_auto_save = state.use("auto_save", True)

    return div(padding=32, gap=24)[
        text("Checkbox", font_size=22, font_weight="bold", color="#F1F1F1"),
        code(
            textwrap.dedent("""\
                checkbox = actions.user.ui_elements(['checkbox'])"""
            )
        ),

        div(gap=16)[
            text("Stories", font_size=18, font_weight="bold", color="#F1F1F1", border_bottom=1, padding_bottom=12,border_color="#333333"),
            component(example_with_code, props={
                "title": "Default Checkbox",
                "example": checkbox(),
                "code": textwrap.dedent("""\
                    checkbox()"""
                )
            }),
            component(example_with_code, props={
                "title": "With label",
                "example": div(
                    flex_direction="row",
                    align_items="center",
                    gap=8,
                )[
                    checkbox(id="a"),
                    text("Label", for_id="a")
                ],
                "code": textwrap.dedent("""\
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(id="a"),
                        text("Label", for_id="a")
                    ]"""
                )
            }),
            component(example_with_code, props={
                "title": "Disabled",
                "example": div(
                    flex_direction="row",
                    align_items="center",
                    gap=8,
                )[
                    checkbox(id="b", disabled=True),
                    text("Label", for_id="b")
                ],
                "code": textwrap.dedent("""\
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(id="b", disabled=True),
                        text("Label", for_id="b")
                    ]"""
                )
            }),
            component(example_with_code, props={
                "title": "State management with different defaults",
                "example": div(gap=12)[
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(
                            id="notifications",
                            checked=notifications_enabled,
                            on_change=lambda e: set_notifications_enabled(e.checked)
                        ),
                        text("Enable notifications (default: False)", for_id="notifications")
                    ],
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(
                            id="dark_mode",
                            checked=dark_mode,
                            on_change=lambda e: set_dark_mode(e.checked)
                        ),
                        text("Dark mode (default: True)", for_id="dark_mode")
                    ],
                    div(
                        flex_direction="row",
                        align_items="center",
                        gap=8,
                    )[
                        checkbox(
                            id="auto_save",
                            checked=auto_save,
                            on_change=lambda e: set_auto_save(e.checked)
                        ),
                        text("Auto-save (default: True)", for_id="auto_save")
                    ],
                ],
                "code": textwrap.dedent("""\
                    state = actions.user.ui_elements("state")
                    notifications_enabled, set_notifications_enabled = state.use("notifications_enabled", False)
                    dark_mode, set_dark_mode = state.use("dark_mode", True)
                    auto_save, set_auto_save = state.use("auto_save", True)

                    div(gap=12)[
                        div(
                            flex_direction="row",
                            align_items="center",
                            gap=8,
                        )[
                            checkbox(
                                id="notifications",
                                checked=notifications_enabled,
                                on_change=lambda e: set_notifications_enabled(e.checked)
                            ),
                            text("Enable notifications (default: False)", for_id="notifications")
                        ],
                        div(
                            flex_direction="row",
                            align_items="center",
                            gap=8,
                        )[
                            checkbox(
                                id="dark_mode",
                                checked=dark_mode,
                                on_change=lambda e: set_dark_mode(e.checked)
                            ),
                            text("Dark mode (default: True)", for_id="dark_mode")
                        ],
                        div(
                            flex_direction="row",
                            align_items="center",
                            gap=8,
                        )[
                            checkbox(
                                id="auto_save",
                                checked=auto_save,
                                on_change=lambda e: set_auto_save(e.checked)
                            ),
                            text("Auto-save (default: True)", for_id="auto_save")
                        ],
                    ]"""
                )
            }),
        ],
    ]
