from talon import actions
from ..common import code, example_with_code
from .. import theme as t
import textwrap


SAMPLE_DATA = [
    {"name": "dictation mode", "command": "user.dictation_mode()", "source": "community", "type": "mode"},
    {"name": "command mode", "command": "user.command_mode()", "source": "community", "type": "mode"},
    {"name": "sleep mode", "command": "user.sleep_mode()", "source": "community", "type": "mode"},
    {"name": "save file", "command": "user.save()", "source": "community", "type": "action"},
    {"name": "undo that", "command": "edit.undo()", "source": "core", "type": "action"},
    {"name": "redo that", "command": "edit.redo()", "source": "core", "type": "action"},
    {"name": "copy this", "command": "edit.copy()", "source": "core", "type": "action"},
    {"name": "paste that", "command": "edit.paste()", "source": "core", "type": "action"},
    {"name": "select all", "command": "edit.select_all()", "source": "core", "type": "action"},
    {"name": "go to top", "command": "edit.file_start()", "source": "core", "type": "navigation"},
    {"name": "go to bottom", "command": "edit.file_end()", "source": "core", "type": "navigation"},
    {"name": "page up", "command": "edit.page_up()", "source": "core", "type": "navigation"},
    {"name": "page down", "command": "edit.page_down()", "source": "core", "type": "navigation"},
    {"name": "zoom in", "command": "user.zoom_in()", "source": "community", "type": "action"},
    {"name": "zoom out", "command": "user.zoom_out()", "source": "community", "type": "action"},
]


TYPE_COLORS = {
    "mode": "#67A4FF",
    "action": "#4ADE80",
    "navigation": "#FBBF24",
}

STATUS_DATA = [
    {"name": "Voice Engine", "status": "running", "uptime": "2h 14m", "cpu": "3.2%"},
    {"name": "Noise Model", "status": "running", "uptime": "2h 14m", "cpu": "1.1%"},
    {"name": "Eye Tracker", "status": "stopped", "uptime": "-", "cpu": "0%"},
    {"name": "Screen Reader", "status": "error", "uptime": "0m 32s", "cpu": "12.4%"},
    {"name": "Input Manager", "status": "running", "uptime": "2h 14m", "cpu": "0.4%"},
    {"name": "Command Parser", "status": "running", "uptime": "2h 13m", "cpu": "2.8%"},
]

STATUS_COLORS = {
    "running": "#4ADE80",
    "stopped": "#888888",
    "error": "#EF4444",
}


def data_table_stories():
    div, text, icon, button, component, data_table, state, ref = actions.user.ui_elements([
        "div", "text", "icon", "button", "component", "data_table", "state", "ref"
    ])

    selected_row, set_selected_row = state.use("dt_story_selected", None)

    def render_type_badge(value, row):
        color = TYPE_COLORS.get(value, "#888888")
        return div(
            background_color=color + "22",
            border_radius=4,
            padding_left=8,
            padding_right=8,
            padding_top=2,
            padding_bottom=2,
        )[
            text(value, font_size=12, color=color),
        ]

    def render_status(value, row):
        color = STATUS_COLORS.get(value, "#888888")
        icon_name = "check" if value == "running" else "close" if value == "error" else "minus"
        return div(flex_direction="row", align_items="center", gap=6)[
            icon(icon_name, size=14, color=color, stroke_width=2),
            text(value, font_size=14, color=color),
        ]

    return div(padding=32, gap=24)[
        text("Data Table", font_size=22, font_weight="bold", color=t.TEXT),
        code(
            textwrap.dedent("""\
                data_table = actions.user.ui_elements(['data_table'])""")
        ),

        div(gap=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT, border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            # Basic sortable with search
            component(example_with_code, props={
                "title": "Sortable with search",
                "example": div()[
                    data_table(
                        id="story_dt_1",
                        columns=[
                            {"key": "name", "label": "Name", "sortable": True, "width": 180},
                            {"key": "command", "label": "Command", "sortable": True, "width": 250},
                            {"key": "source", "label": "Source", "sortable": True, "width": 120},
                            {"key": "type", "label": "Type", "sortable": True, "width": 120},
                        ],
                        data=SAMPLE_DATA,
                        row_key="name",
                        on_select=lambda e: set_selected_row(e.row["name"]),
                        sort_key="name",
                        body_height=300,
                        width=700,
                        border_width=1,
                        border_color="444444",
                        border_radius=8,
                    ),
                    div(flex_direction="row", gap=8, margin_top=8)[
                        button(
                            on_click=lambda e: actions.user.ui_elements_scroll_to_key("story_dt_1", "zoom out"),
                            padding=8,
                            background_color="333333",
                            border_radius=4,
                        )[text("Scroll to 'zoom out' (action)", font_size=12, color=t.TEXT)],
                        button(
                            on_click=lambda e: ref("story_dt_1").scroll_to_key("zoom out"),
                            padding=8,
                            background_color="333333",
                            border_radius=4,
                        )[text("Scroll to 'zoom out' (ref)", font_size=12, color=t.TEXT)],
                        button(
                            on_click=lambda e: actions.user.ui_elements_scroll_to_top("story_dt_1"),
                            padding=8,
                            background_color="333333",
                            border_radius=4,
                        )[text("Scroll to top (action)", font_size=12, color=t.TEXT)],
                        button(
                            on_click=lambda e: ref("story_dt_1").scroll_to_top(),
                            padding=8,
                            background_color="333333",
                            border_radius=4,
                        )[text("Scroll to top (ref)", font_size=12, color=t.TEXT)],
                    ],
                    text(
                        f"Selected: {selected_row}" if selected_row else "Click a row to select",
                        font_size=13,
                        color=t.TEXT_MUTED,
                        margin_top=8,
                    ),
                ],
                "code": textwrap.dedent("""\
                    data_table(
                        id="my_table",
                        columns=[
                            {"key": "name", "label": "Name", "sortable": True, "width": 180},
                            {"key": "command", "label": "Command", "sortable": True},
                            {"key": "source", "label": "Source", "sortable": True, "width": 120},
                        ],
                        data=[...],
                        on_select=lambda e: print(e.row),
                        sort_key="name",
                        body_height=300,
                    )"""),
            }),

            # Custom cell rendering
            component(example_with_code, props={
                "title": "Custom cell rendering",
                "example": data_table(
                    id="story_dt_2",
                    columns=[
                        {"key": "name", "label": "Name", "sortable": True, "width": 180},
                        {"key": "command", "label": "Command", "width": 250},
                        {"key": "type", "label": "Type", "sortable": True, "width": 130,
                         "render": render_type_badge},
                    ],
                    data=SAMPLE_DATA,
                    sort_key="name",
                    body_height=250,
                    width=590,
                    border_width=1,
                    border_color="444444",
                    border_radius=8,
                ),
                "code": textwrap.dedent("""\
                    def render_type_badge(value, row):
                        color = {"mode": "#67A4FF", "action": "#4ADE80"}[value]
                        return div(background_color=color + "22", border_radius=4,
                                   padding_left=8, padding_right=8, padding_top=2, padding_bottom=2)[
                            text(value, font_size=12, color=color),
                        ]

                    data_table(
                        id="my_table",
                        columns=[
                            {"key": "name", "label": "Name", "sortable": True},
                            {"key": "command", "label": "Command"},
                            {"key": "type", "label": "Type", "render": render_type_badge},
                        ],
                        data=[...],
                    )"""),
            }),

            # Status dashboard with icons
            component(example_with_code, props={
                "title": "Status with icons",
                "example": data_table(
                    id="story_dt_3",
                    columns=[
                        {"key": "name", "label": "Service", "sortable": True, "width": 180},
                        {"key": "status", "label": "Status", "sortable": True, "width": 140,
                         "render": render_status},
                        {"key": "uptime", "label": "Uptime", "width": 120},
                        {"key": "cpu", "label": "CPU", "sortable": True, "width": 100, "align": "right"},
                    ],
                    data=STATUS_DATA,
                    sort_key="name",
                    searchable=False,
                    width=570,
                    border_width=1,
                    border_color="444444",
                    border_radius=8,
                ),
                "code": textwrap.dedent("""\
                    def render_status(value, row):
                        color = {"running": "#4ADE80", "stopped": "#888", "error": "#EF4444"}[value]
                        icon_name = "check" if value == "running" else "close"
                        return div(flex_direction="row", align_items="center", gap=6)[
                            icon(icon_name, size=14, color=color, stroke_width=2),
                            text(value, font_size=14, color=color),
                        ]

                    data_table(
                        id="my_table",
                        columns=[
                            {"key": "name", "label": "Service", "sortable": True},
                            {"key": "status", "label": "Status", "render": render_status},
                            {"key": "uptime", "label": "Uptime"},
                            {"key": "cpu", "label": "CPU", "align": "right"},
                        ],
                        data=[...],
                        searchable=False,
                    )"""),
            }),

            # Multi-select
            component(example_with_code, props={
                "title": "Multi-select",
                "example": div()[
                    data_table(
                        id="story_dt_4",
                        columns=[
                            {"key": "name", "label": "Name", "sortable": True, "width": 180},
                            {"key": "command", "label": "Command", "width": 250},
                            {"key": "source", "label": "Source", "width": 120},
                        ],
                        data=SAMPLE_DATA,
                        multi_select=True,
                        row_key="name",
                        on_change=lambda e: set_selected_row(
                            f"{len(e.selected_rows)} rows" if len(e.selected_rows) > 3
                            else ", ".join(r["name"] for r in e.selected_rows) or None
                        ),
                        sort_key="name",
                        body_height=250,
                        width=600,
                        border_width=1,
                        border_color="444444",
                        border_radius=8,
                    ),
                    text(
                        f"Selected: {selected_row}" if selected_row else "Click rows to select",
                        font_size=13,
                        color=t.TEXT_MUTED,
                        margin_top=8,
                    ),
                ],
                "code": textwrap.dedent("""\
                    selected, set_selected = state.use("selected", None)

                    data_table(
                        id="my_table",
                        columns=[
                            {"key": "name", "label": "Name", "sortable": True, "width": 180},
                            {"key": "command", "label": "Command", "width": 250},
                            {"key": "source", "label": "Source", "width": 120},
                        ],
                        data=[
                            {"name": "dictation mode", "command": "user.dictation_mode()", "source": "community"},
                            {"name": "command mode", "command": "user.command_mode()", "source": "community"},
                            ...
                        ],
                        multi_select=True,
                        row_key="name",  # unique key for tracking selection
                        on_change=lambda e: set_selected(e.selected_rows),
                        sort_key="name",
                        body_height=250,
                        width=600,
                        border_width=1,
                        border_color="444444",
                        border_radius=8,
                    )"""),
            }),
        ],
    ]
