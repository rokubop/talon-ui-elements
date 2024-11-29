from talon import Module
from typing import List, Any, Union
from .src.actions import ui_elements
from .src.entity_manager import entity_manager
from .src.state_manager import state_manager
from .src.tree import render_ui
from .src.utils import get_version

mod = Module()

@mod.action_class
class Actions:
    def ui_elements_show(
            renderer: callable,
            props: dict[str, Any] = None,
            on_mount: callable = None,
            on_unmount: callable = None,
            show_hints: bool = False,
            initial_state: dict[str, Any] = None,
        ):
        """Render and show the UI"""
        render_ui(renderer, props, on_mount, on_unmount, show_hints, initial_state)

    def ui_elements(elements: List[str]) -> tuple[callable]:
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
        return ui_elements(elements)

    def ui_elements_hide(renderer: callable):
        """Hide the UI"""
        entity_manager.hide_tree(renderer)

    def ui_elements_hide_all():
        """Hide all UI elements"""
        entity_manager.hide_all_trees()

    def ui_elements_set_state(name: Union[str, dict], value: Union[Any, callable] = None):
        """
        Set state which will cause a rerender

        ```
        actions.user.ui_elements_set_state("color", "red")
        actions.user.ui_elements_set_state({"color": "red", "align": "left"})
        ```
        """
        if isinstance(name, dict):
            for key, val in name.items():
                state_manager.set_state_value(key, val)
        else:
            state_manager.set_state_value(name, value)

    def ui_elements_set_text(id: str, text_or_callable: Union[str, callable]):
        """Set text of an element"""
        state_manager.set_text_mutation(id, text_or_callable)

    def ui_elements_highlight(id: str, color: str = None):
        """highlight based on id"""
        state_manager.highlight(id, color)

    def ui_elements_unhighlight(id: str):
        """unhighlight based on id"""
        state_manager.unhighlight(id)

    def ui_elements_highlight_briefly(id: str, color: str = None):
        """highlight briefly based on id"""
        state_manager.highlight_briefly(id, color)

    def ui_elements_get_node(id: str):
        """Get node for informational purposes e.g. '.box_model', '.tree'"""
        return entity_manager.get_node(id)

    def ui_elements_get_input_value(id: str):
        """Get the value of an input element"""
        return state_manager.get_input_value(id)

    def ui_elements_version():
        """Get the version of talon-ui-elements"""
        return get_version()

    def ui_elements_register_on_lifecycle(callback: callable):
        """Register a callback to be called on mount or unmount"""
        print("ui_elements_register_on_lifecycle is deprecated.")
        # event_register_on_lifecycle(callback)

    def ui_elements_unregister_on_lifecycle(callback: callable):
        """Unregister a lifecycle callback"""
        print("ui_elements_unregister_on_lifecycle is deprecated.")
        # event_unregister_on_lifecycle(callback)