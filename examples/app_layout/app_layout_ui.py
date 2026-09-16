from talon import actions

FILE_CONTENT = {
    # every 7th line is long, so the editor pane actually scrolls sideways
    "main.py": "\n".join([
        f"result_{i} = process(data, config, timeout=30, retries=3, on_error=handle_{i}, "
        f"logger=logger, cache=cache_store, backoff=exponential, validate=True, "
        f"normalize=True, dry_run=False, tags=['batch', 'nightly', 'region_{i}'])"
        if i % 7 == 0 else f"result_{i} = process(data, config)"
        for i in range(200)
    ]),
    "utils.py": "\n".join([f"    return transform(value_{i})" for i in range(50)]),
    "config.py": "\n".join([f"SETTING_{i} = {i * 10}" for i in range(30)]),
    "models.py": "\n".join([f"class Model{i}(Base):" for i in range(80)]),
}


def show_app_layout():
    actions.user.ui_elements_show(app_layout_ui)

def app_layout_ui():
    screen, div, text, window, input_text, code = actions.user.ui_elements(
        ["screen", "div", "text", "window", "input_text", "code"]
    )
    state = actions.user.ui_elements(["state"])

    files = list(FILE_CONTENT.keys())
    active_file = state.get("active_file", files[0])
    content = FILE_CONTENT[active_file]

    def select_file(name):
        return lambda e: state.set("active_file", name)

    return screen(justify_content="center", align_items="center")[
        window(
            title="App Layout",
            width="80%",
            height="80%",
            background_color="#1f2435",
            title_bar_style={"background_color": "#151928"},
        )[
            # Main row
            div(flex_direction="row", flex=1, overflow="hidden")[
                # Sidebar
                div(id="sidebar", width=280, min_width=150, max_width=500, flex_shrink=0,
                    padding=16, gap=4, overflow_y="auto", resizable="right",
                    background_color="#1a1e2a", border_right_width=1, border_color="#333a50")[
                    text("EXPLORER", font_size=13, color="#8892aa", margin_bottom=8),
                    input_text(id="search", placeholder="Search files...",
                               background_color="#2c3348", color="#e4e8f0",
                               padding=10, width="100%", font_size=16),
                    text("OPEN FILES", font_size=12, color="#666d82", margin_top=16, margin_bottom=4),
                    *[div(
                        on_click=select_file(f),
                        padding=8,
                        background_color="#2c3348" if f == active_file else None,
                        border_radius=4,
                        highlight_color="#2c334880",
                    )[
                        text(f, font_size=16, color="#4da6ff"),
                    ] for f in files],
                ],
                # Editor area
                div(flex=1, min_width=0, background_color="#1f2435")[
                    # Tab bar
                    div(flex_direction="row", background_color="#151928", gap=0)[
                        *[div(
                            on_click=select_file(f),
                            padding_left=16, padding_right=16, padding_top=10, padding_bottom=10,
                            background_color="#1f2435" if f == active_file else None,
                            border_top_width=2 if f == active_file else 0,
                            border_color="#4da6ff",
                            highlight_color="#1f243580",
                        )[
                            text(f, font_size=16,
                                 color="#e4e8f0" if f == active_file else "#666d82"),
                        ] for f in files],
                    ],
                    # Code area
                    div(flex=1, padding=16, overflow_x="auto", overflow_y="auto")[
                        code(content, font_size=16, line_numbers=True, copyable=False),
                    ],
                ],
            ],
            # Status bar
            div(flex_direction="row", justify_content="space_between",
                padding_left=16, padding_right=16, padding_top=8, padding_bottom=8,
                background_color="#151928", border_top_width=1, border_color="#333a50")[
                div(flex_direction="row", gap=16)[
                    text("main", font_size=14, color="#4da6ff"),
                    text("Python", font_size=14, color="#8892aa"),
                ],
                div(flex_direction="row", gap=16)[
                    text(f"{active_file}", font_size=14, color="#8892aa"),
                    text("UTF-8", font_size=14, color="#8892aa"),
                    text("Spaces: 4", font_size=14, color="#8892aa"),
                ],
            ],
        ]
    ]
