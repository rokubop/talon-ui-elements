from talon import Module
from typing import List, Any, Union
from .src.elements import ui_elements
from .src.entity_manager import entity_manager
from .src.state_manager import state_manager
from .src.hints import hint_clear_state
from .src.tree import render_ui
from .src.utils import get_version
from .examples._tests import ui_elements_test

mod = Module()

@mod.action_class
class Actions:
    def ui_elements(elements: List[str]) -> Union[tuple[callable], callable]:
        """
        Provides elements and utilities to build your UI.

        ```
        # Example 1
        div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

        # Example 2 - All elements
        elements = ["screen", "div", "text", "button", "input_text", "state", "ref", "effect"]
        screen, div, text, button, input_text, state, ref, effect = actions.user.ui_elements(elements)
        ```
        """
        return ui_elements(elements)

    def ui_elements_show(
            renderer: callable,
            props: dict[str, Any] = None,
            on_mount: callable = None,
            on_unmount: callable = None,
            show_hints: bool = None,
            initial_state: dict[str, Any] = None,
        ):
        """
        Render and show the UI

        ```
        (div, text, screen) = actions.user.ui_elements(["div", "text", "screen"])

        def ui():
            return screen()[
                div()[
                    text("Hello world"),
                ]
            ]

        actions.user.ui_elements_show(ui)

        # with initial state
        actions.user.ui_elements_show(ui, initial_state={"color": "red"})

        # `on_mount` (after UI is visible) and `on_unmount` (before UI is hidden)
        actions.user.ui_elements_show(ui, on_mount=lambda: print("mounted"), on_unmount=lambda: print("unmounted"))
        ```
        """
        render_ui(renderer, props, on_mount, on_unmount, show_hints, initial_state)

    def ui_elements_hide(renderer: callable):
        """Destroy and hide a specific ui (compliments `ui_elements_show`)"""
        entity_manager.hide_tree(renderer)

    def ui_elements_hide_all():
        """Destroy and hide all UIs"""
        entity_manager.hide_all_trees()

    def ui_elements_set_state(name: Union[str, dict], value: Union[Any, callable] = None):
        """
        Set global state which will cause a rerender to any respective UIs using the state.

        ```
        actions.user.ui_elements_set_state("active_tab", 1)
        ```

        Set multiple states at once:
        ```
        actions.user.ui_elements_set_state({
            "title": "Notes",
            "subtitle": "Write a note"
            "actions": {
                "text": "Action 1",
                "action": lambda: print("Action 1 clicked")
            }
        })
        ```
        """
        if isinstance(name, dict):
            for key, val in name.items():
                state_manager.set_state_value(key, val)
        else:
            state_manager.set_state_value(name, value)

    def ui_elements_get_state(name: str):
        """
        Get global state value by its name.
        ```
        """
        state_manager.get_state_value(name)

    def ui_elements_set_text(id: str, text_or_callable: Union[str, callable]):
        """
        Set text based on its `id`. Renders on a decoration layer, and faster than using `ui_elements_set_state`.

        ```
        text("Hello", id="my_id")[...]

        actions.user.ui_elements_set_text("my_id", "Hello world")
        actions.user.ui_elements_set_text("my_id", lambda current_text: current_text + "!")
        ```
        """
        state_manager.set_text_mutation(id, text_or_callable)

    def ui_elements_set_property(id: str, property_name: str, value: Any):
        """
        Set a property of an element based on its `id`. Will cause a rerender.

        For example: `color`, `background_color`, `font_size`, `flex_direction`, `justify_content`, `align_items`, `width`, etc...
        ```
        div(id="my_id")[...]

        actions.user.ui_elements_set_property("my_id", "background_color", "red")
        actions.user.ui_elements_set_property("my_id", "justify_content", "flex_start")
        ```
        """
        state_manager.set_ref_property_override(id, property_name, value)

    def ui_elements_get_input_value(id: str):
        """Get the value of a `input_text` element based on its id"""
        return state_manager.get_input_value(id)

    def ui_elements_highlight(id: str, color: str = None):
        """Highlight element based on its id. Renders on a decoration layer."""
        state_manager.highlight(id, color)

    def ui_elements_unhighlight(id: str):
        """Unhighlight element based on its id. Renders on a decoration layer."""
        state_manager.unhighlight(id)

    def ui_elements_highlight_briefly(id: str, color: str = None):
        """Highlight element briefly based on its id. Renders on a decoration layer."""
        state_manager.highlight_briefly(id, color)

    def ui_elements_get_node(id: str):
        """Get node for informational purposes e.g. to access `.box_model`, `.tree`, `.parent_node`, `.children_nodes`, or other properties"""
        return entity_manager.get_node(id)

    def ui_elements_version():
        """Get the current version of `talon-ui-elements`"""
        return get_version()

    def ui_elements_reset():
        """Destroy all UIs, trees, nodes, and reset all states"""
        entity_manager.hide_all_trees()
        state_manager.clear_all()
        hint_clear_state()
        print("ui elements reset")

    def ui_elements_test():
        """Test examples"""
        ui_elements_test()

    def ui_elements_register_on_lifecycle(callback: callable):
        """
        DEPRECATED: Register a callback to be called on mount or unmount.

        Deprecated note: Use `effect` instead inside your renderer, or use `on_mount` and `on_unmount` kwargs in `ui_elements_show`.
        """
        print("ui_elements_register_on_lifecycle is deprecated. Use effects instead.")
        state_manager.deprecated_event_register_on_lifecycle(callback)

    def ui_elements_unregister_on_lifecycle(callback: callable):
        """
        DEPRECATED: Unregister a lifecycle callback.

        Deprecated note: Use `effect` instead inside your renderer, or use `on_mount` and `on_unmount` kwargs in `ui_elements_show`.
        """
        print("ui_elements_unregister_on_lifecycle is deprecated. Use effects instead.")
        state_manager.deprecated_event_unregister_on_lifecycle(callback)