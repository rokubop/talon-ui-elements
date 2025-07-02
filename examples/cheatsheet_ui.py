from talon import actions

commands_list_1 = [
    "up",
    "down",
    "left",
    "right",
    "jump",
    "shoot",
    "pause",
    "back",
]

commands_list_2 = [
    "go",
    "stop",
    "wait",
    "look",
    "say",
    "sprint",
    "reload",
]

commands_table = {
    "up": "Move up",
    "down": "Move down",
    "left": "Move left",
    "right": "Move right",
    "jump": "Jump",
    "shoot": "Shoot",
    "pause": "Pause",
    "back": "Go back",
    "go": "Go",
    "stop": "Stop",
    "wait": "Wait",
    "look": "Look",
    "say": "Say",
    "sprint": "Sprint",
    "reload": "Reload",
}

def table_commands():
    table, tr, th, td = actions.user.ui_elements(['table', 'tr', 'th', 'td'])
    text, style = actions.user.ui_elements(['text', 'style'])

    style({
        "th": {
            "padding": 6,
            "color": "#FFCC00",
        },
        "td": {
            "padding": 6
        },
    })

    return table()[
        tr()[
            th()[text("Command")],
            th()[text("Description")],
        ],
        *[tr()[
            td()[text(command)],
            td()[text(description)],
        ] for command, description in commands_table.items()]
    ]

def list_commands():
    div, text = actions.user.ui_elements(['div', 'text'])

    return div(flex_direction="row", gap=16)[
        div(flex=1, padding=12, border_radius=4, border_color="#444444", border_width=1)[
            text("List 1", color="#FFCC00", font_weight="bold"),
            *[text(command) for command in commands_list_1]
        ],
        div(flex=1, padding=12, border_radius=4, border_color="#444444", border_width=1)[
            text("List 2", color="#FFCC00", font_weight="bold"),
            *[text(command) for command in commands_list_2]
        ]
    ]

def cheatsheet_ui():
    """Main UI for cheatsheet"""
    div, screen, text, style = actions.user.ui_elements(['div', 'screen', 'text', 'style'])

    style({
        ".title": {
            "font_weight": "bold",
            "font_size": 16,
            "color": "#FFFFFF",
            "padding_bottom": 8,
            "border_bottom": 1,
            "border_color": "#FFCC00"
        }
    })

    return screen(flex_direction="row", align_items="center", justify_content="flex_end")[
        div(
            draggable=True,
            flex_direction="column",
            opacity=0.7,
            margin=16,
            background_color="#333333",
            padding=16,
            gap=16,
            border_radius=8,
        )[
            text("List commands", class_name="title"),
            list_commands(),
            text("Table commands", class_name="title"),
            table_commands()
        ]
    ]
