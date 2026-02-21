from talon import actions, cron


def notification_ui():
    elements = ["div", "text", "screen"]
    div, text, screen = actions.user.ui_elements(elements)

    return screen(justify_content="center", align_items="center")[
        div(
            padding=15,
            background_color="#0088ffdd",
            border_radius=10,
            opacity=1.0,
            top=0,
            position="relative",
            mount_style={"opacity": 0, "top": 20},
            unmount_style={"opacity": 0, "top": 20},
            transition={"opacity": 300, "top": 300},
        )[
            text("Notification: saved!", font_size=20, color="white", font_weight="bold"),
        ],
    ]


def show_notification():
    cron.after("200ms", lambda: actions.user.ui_elements_show(notification_ui, duration="2s"))


def hide_notification():
    actions.user.ui_elements_hide(notification_ui)
