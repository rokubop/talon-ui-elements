from talon import Module, actions
from typing import List, Any, Union, Callable
from .src.core.entity_manager import entity_manager
from .src.core.state_manager import state_manager, debug_gc
from .src.dev_tools import DevTools
from .src.elements import ui_elements, ui_elements_svg, use_effect_without_tree
from .src.entry import render_ui
from .src.errors import show_error_if_not_compatible
from .src.utils import get_version
from .tests.test_runner_ui import runner_ui
from .examples.examples_ui import toggle_elements_examples
from .storybook.main import storybook_ui

mod = Module()
UNSET = object()

@mod.action_class
class Actions:
    def ui_elements(elements: Union[str, List[str]]) -> Union[tuple[callable], callable]:
        """
        Provides elements and utilities to build your UI.

        ```
        div, text, screen = actions.user.ui_elements(["div", "text", "screen"])
        screen, active_window, window = actions.user.ui_elements(["screen", "active_window", "window"])
        button, input_text, state = actions.user.ui_elements(["button", "input_text", "state"])
        ref, effect, icon = actions.user.ui_elements(["ref", "effect", "icon"])
        component, style = actions.user.ui_elements(["component", "style"])
        checkbox, link = actions.user.ui_elements(["checkbox", "link"])
        table, th, tr, td = actions.user.ui_elements(["table", "th", "tr", "td"])
        svg, path, rect, line = actions.user.ui_elements(["svg", "path", "rect", "line"])
        circle, polyline, polygon = actions.user.ui_elements(["circle", "polyline", "polygon"])
        ```
        """
        return ui_elements(elements)

    def ui_elements_show(
            renderer: Callable,
            props: dict[str, Any] = None,
            on_mount: Callable = None,
            on_unmount: Callable = None,
            show_hints: bool = None,
            initial_state: dict[str, Any] = None,
            min_version: str = None,
        ):
        """
        Render and show the UI

        ```
        div, text, screen = actions.user.ui_elements(["div", "text", "screen"])

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
        if min_version and show_error_if_not_compatible(renderer, min_version):
            return

        render_ui(renderer, props, on_mount, on_unmount, show_hints, initial_state)

    def ui_elements_hide(renderer_or_tree_id: Union[str, Callable]):
        """Destroy and hide a specific ui based on its renderer_or_tree_id function or an id on the root node (screen)"""
        entity_manager.hide_tree(renderer_or_tree_id)

    def ui_elements_hide_all():
        """Destroy and hide all UIs"""
        entity_manager.hide_all_trees()

    def ui_elements_toggle(
            renderer: Union[str, Callable],
            props: dict[str, Any] = None,
            on_mount: callable = None,
            on_unmount: callable = None,
            show_hints: bool = None,
            initial_state: dict[str, Any] = None,
        ):
        """Toggle visibility of a specific ui based on its renderer function or an id on the root node"""
        new_state_visible = not entity_manager.does_tree_exist(renderer)

        if new_state_visible:
            actions.user.ui_elements_show(renderer, props, on_mount, on_unmount, show_hints, initial_state)
        else:
            entity_manager.hide_tree(renderer)

        return new_state_visible

    def ui_elements_is_active(renderer: Union[str, Callable]):
        """Check if a specific ui is active based on its renderer function or an id on the root node"""
        return entity_manager.does_tree_exist(renderer)

    def ui_elements_set_state(name: Union[str, dict], value: Union[Any, callable] = UNSET):
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
            if value is UNSET:
                raise TypeError("actions.user.ui_elements_set_state requires a string key and a value.")
            state_manager.set_state_value(name, value)

    def ui_elements_get_state(name: str = None):
        """
        Get global state value by its name or None for all states.
        ```
        """
        return state_manager.get_state_value(name) if name else state_manager.get_all_states()

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

    def ui_elements_set_property(id: str, property_name: Union[str, dict], value: Any):
        """
        Set a property of an element based on its `id`. Will cause a rerender.

        For example: `color`, `background_color`, `font_size`, `flex_direction`, `justify_content`, `align_items`, `width`, etc...
        ```
        div(id="my_id")[...]

        actions.user.ui_elements_set_property("my_id", "background_color", "red")
        actions.user.ui_elements_set_property("my_id", "justify_content", "flex_start")
        actions.user.ui_elements_set_property("my_id", {
            "background_color": "red",
            "justify_content": "flex_start"
        })
        ```
        """
        if isinstance(property_name, dict):
            for key, val in property_name.items():
                state_manager.set_property_override(id, key, val)
        else:
            state_manager.set_ref_property_override(id, property_name, value)

    def ui_elements_toggle_hints(enabled: bool = None):
        """Toggle hints visibility"""
        state_manager.toggle_hints(enabled)

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

    def ui_elements_get_trees():
        """Get all trees. A tree is responsible for each individual UI that is rendered and has all information and methods related to that UI."""
        return entity_manager.get_all_trees()

    def ui_elements_storybook_toggle():
        """Toggle the storybook UI"""
        actions.user.ui_elements_toggle(storybook_ui)

    def ui_elements_version():
        """
        Get the current version of `talon-ui-elements`.

        Returns:
            Version: A dataclass with the following attributes:
                - `major` (int): The major version number.
                - `minor` (int): The minor version number.
                - `patch` (int): The patch version number.

        Usage:
            version = ui_elements_version()
            print(version.minor)  # Access the minor version
            print(version.major)  # Access the major version
            print(version)        # Print the full version as a string
            print(version < "0.6.2")  # Compare with a string version
        """
        return get_version()

    def ui_elements_examples():
        """Test example UIs"""
        toggle_elements_examples()

    def ui_elements_dev_tools():
        """Opens dev tools"""
        actions.user.ui_elements_toggle(DevTools)

    def ui_elements_debug_gc():
        """Debug garbage collection - print to log"""
        debug_gc()

    def ui_elements_svg(elements: List[str]) -> Union[tuple[callable], callable]:
        """
        Provides elements to create standard SVG elements, based on view_box 0 0 24 24.

        ```
        # Example 1
        svg, path = actions.user.ui_elements_svg(["svg", "path"])

        # Example 2 - All elements
        elements = ["svg", "path", "rect", "circle", "line", "polyline", "polygon"]
        svg, path, rect, circle, line, polyline, polygon = actions.user.ui_elements_svg(elements)

        svg()[
            path(d="M150 0 L75 200 L225 200 Z", fill="red"),
            rect(x=10, y=10, width=100, height=100, fill="blue"),
        ]
        ```
        """
        return ui_elements_svg(elements)

    def ui_elements_register_effect(callback: callable, arg2: Any, arg3: Any = None):
        """
        Same as `effect`, but can be registered independently, and will be attached to current or upcoming renderer.

        `ui_elements_register_effect(on_mount, [])`

        `ui_elements_register_effect(on_mount, on_unmount, [])`

        `ui_elements_register_effect(on_change, [state_key])`

        Dependencies are `str` state keys, or empty `[]` for mount/unmount effects.
        ```
        """
        use_effect_without_tree(callback, arg2, arg3)

    def ui_elements_test_runner():
        """Run the test runner for regression tests"""
        actions.user.ui_elements_toggle(runner_ui)