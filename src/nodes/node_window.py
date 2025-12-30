from talon import actions, cron
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..events import WindowCloseEvent
from ..properties import Properties, NodeWindowProperties
from ..utils import generate_hash, adjust_color_brightness
from ..core.entity_manager import entity_manager
import inspect

last_pos_map = {}

class NodeWindow(NodeContainer):
    def __init__(self, window_properties: dict, body_properties: dict = None):
        global last_pos_map
        div, icon, button, text, state = actions.user.ui_elements(["div", "icon", "button", "text", "state"])
        self.hash = generate_hash({
            **window_properties,
            **body_properties,
        })
        self.init_position()
        self.destroying = False
        last_pos = self.last_pos
        last_docked_pos = self.last_docked_pos

        try:
            is_minimized, set_is_minimized = state.use(
                f"is_minimized_{self.hash}",
                window_properties.get("minimized", False)
            )
        except Exception as e:
            is_minimized, set_is_minimized = window_properties.get("minimized", False), lambda x: actions.user.ui_elements_set_state(
                f"is_minimized_{self.hash}", x
            )

        self.is_minimized = is_minimized
        minimized_style = window_properties.get("minimized_style", None)

        self.has_dock_behavior = minimized_style is not None and any(
            minimized_style.get(dir) is not None
            for dir in ["top", "left", "right", "bottom"]
        )

        # Cap at 18 because title bar has finite height and larger radii don't render well
        border_radius = min(window_properties.get("border_radius", 4), 18)

        if isinstance(border_radius, (list, tuple)):
            title_bar_border_radius = (border_radius[0] + 2, border_radius[1] + 2, 0, 0)
        else:
            title_bar_border_radius = (border_radius + 2, border_radius + 2, 0, 0)

        resolved_window_props = {
            "draggable": True,
            "background_color": "222222",
            "drop_shadow": (0, 20, 25, 25, "000000CC"),
            "border_radius": 4,
            "border_width": 1,
            **window_properties,
            "on_drag_end": self.update_saved_positions
        }
        title_bar_style = {
            "background_color": adjust_color_brightness(
                window_properties.get("background_color", None), 10
            ) if window_properties.get("background_color", None) else "272727",
            "border_radius": title_bar_border_radius,
        }
        title_style = {
            "padding": 8,
            "padding_left": 10,
        }
        icon_style = {
            "stroke_width": 1,
        }
        button_style = {}

        if self.is_minimized:
            resolved_window_props.update({
                "position": "absolute" if last_pos is not None else "static",
                "top": last_pos.top if last_pos is not None else None,
                "left": last_pos.left if last_pos is not None else None,
                "width": None,
                "min_height": None,
                "height": None,
                "min_width": 200,
            })
            if minimized_style and self.has_dock_behavior:
                if last_docked_pos is not None:
                    resolved_window_props.update({
                        **minimized_style,
                        "top": last_docked_pos.top,
                        "left": last_docked_pos.left,
                        "bottom": None,
                        "right": None,
                    })
                else:
                    resolved_window_props.update({
                        "top": minimized_style.get("top", None),
                        "left": minimized_style.get("left", None),
                        "right": minimized_style.get("right", None),
                        "bottom": minimized_style.get("bottom", None),
                    })
        else:
            resolved_window_props.update({
                "position": resolved_window_props.get("position", "static"),
                "top": resolved_window_props.get("top", None),
                "left": resolved_window_props.get("left", None),
            })

        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["window"],
            properties=NodeWindowProperties(**resolved_window_props)
        )

        def on_minimize():
            global last_pos_map
            new_is_minimized = not self.is_minimized
            self.update_saved_positions()
            set_is_minimized(new_is_minimized)
            if new_is_minimized:
                self.prepare_minimized_body()
                if window_properties.get("on_minimize", None):
                    window_properties.get("on_minimize")()
            elif not new_is_minimized:
                self.prepare_non_minimized_body()
                if window_properties.get("on_restore", None):
                    window_properties.get("on_restore")()

        def on_close(e: WindowCloseEvent):
            if not self.destroying:
                def deferred_close():
                    if not self.destroying:
                        if window_properties.get("on_close", None):
                            if len(inspect.signature(window_properties.get("on_close")).parameters) == 1:
                                window_properties.get("on_close")(e)
                            else:
                                window_properties.get("on_close")()

                        if e.default_prevented:
                            return

                        if e.hide and not (self.tree and self.tree.render_manager.is_destroying):
                            self.destroying = True
                            if self.tree and self.tree.id:
                                entity_manager.hide_tree(self.tree.id)
                            else:
                                entity_manager.hide_all_trees()

                # This helps break call stack and avoid recursive action errors
                # in case user called actions.user.ui_elements_hide in the on_close handler
                cron.after("1ms", deferred_close)

        def on_button_click_close():
            on_close(WindowCloseEvent(hide=True))

        self.on_minimize = on_minimize
        self.on_close = on_close

        if window_properties.get("title_bar_style", None):
            for key, value in window_properties.get("title_bar_style", {}).items():
                if key in ["color"]:
                    title_style[key] = value
                    icon_style[key] = value
                elif key in ["size", "stroke_width"]:
                    icon_style[key] = value
                elif key in ["font_size", "font_weight", "font_family"]:
                    title_style[key] = value
                elif key in ["highlight_style"]:
                    button_style[key] = value
                else:
                    title_bar_style[key] = value

        drag_title_bar_only = window_properties.get("drag_title_bar_only", True)

        def title_bar():
            title_bar_props = {"drag_handle": True} if drag_title_bar_only else {}
            return div(title_bar_style, **title_bar_props, flex_direction="row", justify_content="space_between", align_items="center")[
                text(window_properties.get("title", ""), **title_style),
                div(flex_direction="row")[
                    button(on_click=on_minimize, padding=8, padding_left=12, padding_right=12, **button_style)[
                        icon("minimize" if not self.is_minimized else "testing2", size=18, **icon_style),
                    ] if window_properties.get("show_minimize", True) else None,
                    button(on_click=on_button_click_close, padding=8, padding_left=12, padding_right=12, **button_style)[
                        icon("close", size=20, **icon_style),
                    ] if window_properties.get("show_close", True) else None,
                ],
            ],

        self.body = div(**body_properties)
        if window_properties.get("show_title_bar", True):
            self.add_child(title_bar())
        if window_properties.get("minimized_body", None) and self.is_minimized:
            self.add_child(window_properties.get("minimized_body")())
        else:
            self.add_child(self.body)

    def init_position(self):
        if not last_pos_map.get(self.hash):
            last_pos_map[self.hash] = {
                "last_pos": None,
                "last_docked_pos": None,
                "last_pos_drag_offset": None,
                "last_docked_pos_drag_offset": None,
            }

    @property
    def last_pos(self):
        return last_pos_map.get(self.hash, {}).get("last_pos", None)

    @property
    def last_docked_pos(self):
        return last_pos_map.get(self.hash, {}).get("last_docked_pos", None)

    def update_saved_positions(self):
        if self.has_dock_behavior and self.is_minimized:
            self.set_last_docked_pos(
                actions.user.ui_elements_get_node(self.id).box_model.border_rect
            )
        else:
            self.set_last_pos(
                actions.user.ui_elements_get_node(self.id).box_model.border_rect
            )

    def prepare_minimized_body(self):
        # Our tree meta state only keeps track of one drag offset
        # But window has two - minimized vs non-minimized
        # so we update the tree meta state to reflect our internal state
        if self.has_dock_behavior and last_pos_map[self.hash].get("last_docked_pos_drag_offset", None):
            try:
                self.tree.meta_state._draggable_offset[self.id] = \
                    last_pos_map[self.hash].get("last_docked_pos_drag_offset", None)
            except Exception as e:
                print(f"Error setting draggable offset: {e}")

    def prepare_non_minimized_body(self):
        # Our tree meta state only keeps track of one drag offset
        # But window has two - minimized vs non-minimized
        # so we update the tree meta state to reflect our internal state
        if self.has_dock_behavior and last_pos_map[self.hash].get("last_pos_drag_offset", None):
            try:
                self.tree.meta_state._draggable_offset[self.id] = \
                    last_pos_map[self.hash].get("last_pos_drag_offset", None)
            except Exception as e:
                print(f"Error setting draggable offset: {e}")

    def set_last_pos(self, pos):
        try:
            offset = self.tree.meta_state.get_accumulated_drag_offset(self.id)
            last_pos_map[self.hash]["last_pos_drag_offset"] = offset
        except Exception as e:
            print(f"Error setting last pos drag offset: {e}")
        last_pos_map[self.hash]["last_pos"] = pos

    def set_last_docked_pos(self, pos):
        try:
            offset = self.tree.meta_state.get_accumulated_drag_offset(self.id)
            last_pos_map[self.hash]["last_docked_pos_drag_offset"] = offset
        except Exception as e:
            print(f"Error setting last docked pos drag offset: {e}")
        last_pos_map[self.hash]["last_docked_pos"] = pos

    def __getitem__(self, children_nodes=None):
        if self.is_minimized:
            return self

        if children_nodes is None:
            children_nodes = []

        if not isinstance(children_nodes, list):
            children_nodes = [children_nodes]

        for node in children_nodes:
            self.body.add_child(node)

        return self

    def destroy(self):
        self.on_minimize = None
        self.on_close = None
        super().destroy()
