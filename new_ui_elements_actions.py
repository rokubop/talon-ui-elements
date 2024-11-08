from talon import Module, actions
from typing import List, Dict, Any
from .src.elements.index import (
    div,
    text,
    screen,
)
from .src.state import state
from .src.actions import ui_elements_new

mod = Module()

show = True

@mod.action_class
class Actions:
    def ui_elements_new(elements: List[str]) -> tuple[callable]:
        """
        This acts like an import for the components you want to use.
        div, text, screen, button, input_text.

        Usage:
        ```py
        # def show
        (div, text, screen, button, input_text) = actions.user.ui_elements(["div", "text", "screen", "button", "input_text"])
        ui = screen(align_items="flex_end", justify_content="center")[
            div(id="box", padding=16, background_color="FF000088")[
                text("Hello world", color="FFFFFF"),
                text("Test", id="test", font_size=24),
                input_text(id="the_input"),
                button("Click me", on_click=lambda: print("Clicked"))
            ]
        ]
        ui.show()

        # def hide and destroy
        actions.user.ui_elements_hide_all()

        # trigger update text
        actions.user.ui_elements_set_text("test", "Updated")

        # trigger highlight
        actions.user.ui_elements_highlight("box")
        actions.user.ui_elements_highlight_briefly("box")
        actions.user.ui_elements_unhighlight("box")

        # trigger get value
        actions.user.ui_elements_get_value("the_input")
        ```
        """
        return ui_elements_new(elements)

    def ui_elements_test_new():
        """asdf"""
        global show

        if show:
            (div, text, screen) = actions.user.ui_elements_new(["div", "text", "screen"])

            ui = screen(justify_content="center", align_items="center")[
                div(background_color="white", padding=16, border_radius=16, border_width=1)[
                    text("Hello world", color="red", font_size=24)
                ]
            ]
            ui.show()
        else:
            for node in list(state.builders.values()):
                node.hide()

        show = not show