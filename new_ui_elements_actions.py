from talon import Module, actions
from typing import List, Dict, Any, Union
# from .src.elements.index import (
#     div,
#     text,
#     screen,
# )
from .src.actions import ui_elements_new
from .src.entity_manager import entity_manager
from .src.state_manager import state_manager
from .src.entities.tree import render_ui

mod = Module()

@mod.action_class
class Actions:
    def ui_elements_new_show(ui: callable, props: dict[str, Any] = None, on_mount: callable = None, on_unmount: callable = None, show_hints: bool = False):
        """Render and show the UI"""
        render_ui(ui, props, on_mount, on_unmount, show_hints)

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

    def ui_elements_new_hide_all():
        """Hide all UI elements"""
        entity_manager.hide_all_trees()

    def ui_elements_new_set_state(name: str, value: Union[Any, callable]):
        """set any arbitrary state which will automatically rerender"""
        state_manager.set_state_value(name, value)

    def ui_elements_new_set_text(id: str, text_or_callable: Union[str, callable]):
        """Set text of an element"""
        state_manager.set_text_mutation(id, text_or_callable)