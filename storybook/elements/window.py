"""Window storybook: buttons launch standalone window configurations that
exercise layout edge cases (wrapping text + height-constrained window).

Each window is its own renderer so the trees are isolated -- the storybook
remains visible alongside the test window."""

from talon import actions
from .. import theme as t
import textwrap
from ..common import example_with_code, code


# ----- shared content factory -----

def _conflict_card(use_long_paragraph: bool, use_long_path: bool):
    """Mimics the structure of gamekit's app_registered_conflict_view:
    header row, paragraph, "Registered by:" label, match row card, continue
    button. Knobs toggle the two cases that historically broke layout."""
    div, text, button = actions.user.ui_elements(["div", "text", "button"])

    paragraph_long = (
        "Another Talon package already declares mod.apps.windows_terminal. "
        "Creating a new gamekit package here would duplicate that registration "
        "and likely conflict with the existing one. Open the existing package "
        "below to extend it in place, or continue anyway if you know what "
        "you're doing."
    )
    paragraph = paragraph_long if use_long_paragraph else "Short test paragraph."

    long_path = (
        "C:\\Users\\Rokubop\\AppData\\Roaming\\talon\\user\\some\\windows_terminal"
    )
    path = long_path if use_long_path else "short_path"

    btn_kwargs = dict(
        font_size=14, color=t.TEXT, background_color=t.BG_ACTIVE,
        border_radius=6, border_width=1, border_color=t.BORDER,
        padding=8, padding_left=14, padding_right=14,
    )

    return div(padding=24, gap=16, max_width=640)[
        div(flex_direction="row", align_items="center", gap=12)[
            text("[!]", font_size=22, font_weight="bold", color="ffcc66"),
            text("Windows Terminal is already wired up",
                 font_size=22, font_weight="bold", color=t.TEXT),
        ],
        text(paragraph, font_size=14, color=t.TEXT_MUTED),
        text("Registered by:", font_size=14, font_weight="bold",
             color=t.TEXT_MUTED, margin_top=4),
        div(flex_direction="column", gap=8)[
            div(flex_direction="row", align_items="center", gap=12,
                padding=14, background_color=t.BG_RAISED, border_radius=6,
                border_width=1, border_color=t.BORDER)[
                div(flex=1, gap=4, min_width=0)[
                    text("windows_terminal",
                         font_size=15, font_weight="bold", color=t.TEXT),
                    text(path, font_size=13, color=t.TEXT_MUTED),
                ],
                div(flex_direction="row", gap=8)[
                    button("Open in Explorer", **btn_kwargs),
                    button("Open in VS Code", **btn_kwargs),
                ],
            ],
        ],
        div(flex_direction="row", justify_content="flex_end", margin_top=8)[
            div(
                flex_direction="row", align_items="center", gap=8,
                padding_top=12, padding_bottom=12,
                padding_left=20, padding_right=20,
                border_radius=6,
                background_color=t.BG_RAISED,
                border_width=1, border_color=t.BORDER,
            )[
                text("Continue with new package anyway",
                     font_size=14, font_weight="bold", color=t.TEXT_MUTED),
            ],
        ],
    ]


# ----- one renderer per window variant (separate trees) -----

def _make_window(title: str, body):
    screen, window = actions.user.ui_elements(["screen", "window"])
    return screen(align_items="center", justify_content="center")[
        window(
            title=title,
            max_width="85%",
            max_height="90%",
            padding=0,
            background_color=t.BG,
            resizable=True,
        )[body],
    ]


def _hide_all_test_windows():
    for fn in [
        _window_long_para_long_path,
        _window_short_para_long_path,
        _window_long_para_short_path,
        _window_short_para_short_path,
    ]:
        try:
            actions.user.ui_elements_hide(fn)
        except Exception:
            pass


def _window_long_para_long_path():
    return _make_window(
        "long paragraph + long path (squish bug)",
        _conflict_card(use_long_paragraph=True, use_long_path=True),
    )


def _window_short_para_long_path():
    return _make_window(
        "short paragraph + long path",
        _conflict_card(use_long_paragraph=False, use_long_path=True),
    )


def _window_long_para_short_path():
    return _make_window(
        "long paragraph + short path",
        _conflict_card(use_long_paragraph=True, use_long_path=False),
    )


def _window_short_para_short_path():
    return _make_window(
        "short paragraph + short path (control)",
        _conflict_card(use_long_paragraph=False, use_long_path=False),
    )


def _launch(fn):
    """Hide any open test window then show the requested one. Keeps only
    one variant on screen at a time so comparisons are unambiguous."""
    _hide_all_test_windows()
    actions.user.ui_elements_show(fn)


# ----- storybook page -----

def window_stories():
    div, text, button = actions.user.ui_elements(["div", "text", "button"])

    launch_btn_kwargs = dict(
        font_size=14, color=t.TEXT,
        background_color=t.BG_ACTIVE,
        border_radius=6,
        border_width=1, border_color=t.BORDER,
        padding=12, padding_left=18, padding_right=18,
    )

    return div(padding=32, gap=24)[
        text("Window", font_size=22, font_weight="bold", color=t.TEXT),
        code(textwrap.dedent("""\
            screen, window = actions.user.ui_elements(['screen', 'window'])""")),

        text(
            "Each button opens a window with a copy of the gamekit conflict "
            "view in a specific configuration. Use them to verify wrapping "
            "text inside a max_height-constrained window doesn't squish "
            "siblings or cut off content.",
            font_size=14, color=t.TEXT_MUTED,
        ),

        div(gap=12, flex_direction="column")[
            button("Open: long paragraph + long path",
                   on_click=lambda: _launch(_window_long_para_long_path),
                   **launch_btn_kwargs),
            button("Open: short paragraph + long path",
                   on_click=lambda: _launch(_window_short_para_long_path),
                   **launch_btn_kwargs),
            button("Open: long paragraph + short path",
                   on_click=lambda: _launch(_window_long_para_short_path),
                   **launch_btn_kwargs),
            button("Open: short paragraph + short path (control)",
                   on_click=lambda: _launch(_window_short_para_short_path),
                   **launch_btn_kwargs),
            button("Close all test windows",
                   on_click=lambda: _hide_all_test_windows(),
                   **launch_btn_kwargs),
        ],

        div(gap=16, margin_top=16)[
            text("Examples", font_size=18, font_weight="bold", color=t.TEXT,
                 border_bottom=1, padding_bottom=12, border_color=t.BORDER),

            component_example_with_code(
                title="Bare window (no body)",
                code_str=textwrap.dedent("""\
                    screen, window = actions.user.ui_elements(['screen', 'window'])

                    def my_ui():
                        return screen()[
                            window(title='Hello', max_width='60%', max_height='60%')[
                                # body content
                            ],
                        ]

                    actions.user.ui_elements_show(my_ui)"""),
            ),
        ],
    ]


def component_example_with_code(title: str, code_str: str):
    """Light wrapper -- regular example_with_code expects an example element
    to render inline, but windows can't render inline. So we just show the
    title and the code."""
    component = actions.user.ui_elements("component")
    div, text = actions.user.ui_elements(["div", "text"])
    return div(gap=8, flex_direction="column")[
        text(title, font_size=18, font_weight="bold", color=t.TEXT),
        code(code_str),
    ]
