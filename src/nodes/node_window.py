from talon import actions
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..events import WindowCloseEvent
from ..properties import Properties, NodeWindowProperties
from ..core.entity_manager import entity_manager
import inspect

last_pos_map = {}

class NodeWindow(NodeContainer):
    def __init__(self, properties: Properties):
        global last_pos_map
        div, icon, button, text, state = actions.user.ui_elements(["div", "icon", "button", "text", "state"])
        self.hash = properties.hash()
        self.init_position()
        self.destroying = False
        last_pos = self.last_pos
        last_docked_pos = self.last_docked_pos

        is_minimized, set_is_minimized = state.use(f"is_minimized_{self.hash}", properties.minimized)
        self.is_minimized = is_minimized

        window_properties = properties

        self.has_dock_behavior = properties.minimized_style is not None and any(
            properties.minimized_style.get(dir) is not None
            for dir in ["top", "left", "right", "bottom"]
        )

        if self.is_minimized:
            default_minimized_properties = {
                "position": "absolute" if last_pos is not None else "static",
                "top": last_pos.top if last_pos is not None else None,
                "left": last_pos.left if last_pos is not None else None,
                "min_width": 200,
                "draggable": True,
                "background_color": properties.background_color,
                "border_radius": properties.border_radius,
                "border_width": properties.border_width,
                "border_color": properties.border_color,
                "drop_shadow": properties.drop_shadow,
            }
            if properties.minimized_style:
                if self.has_dock_behavior:
                    if last_docked_pos is not None:
                        default_minimized_properties.update({
                            "top": last_docked_pos.top,
                            "left": last_docked_pos.left,
                        })
                    else:
                        default_minimized_properties.update({
                            "top": properties.minimized_style.get("top", None),
                            "left": properties.minimized_style.get("left", None),
                            "right": properties.minimized_style.get("right", None),
                            "bottom": properties.minimized_style.get("bottom", None),
                        })

                window_properties = NodeWindowProperties(
                    **default_minimized_properties
                )
            else:
                window_properties = NodeWindowProperties(
                    **default_minimized_properties,
            )
        else:
            window_properties.position = "static"
            window_properties.top = None
            window_properties.left = None
            window_properties.drop_shadow = properties.drop_shadow

        window_properties.on_drag_end = self.update_saved_positions

        super().__init__(element_type=ELEMENT_ENUM_TYPE["window"], properties=window_properties)

        def on_minimize():
            global last_pos_map
            new_is_minimized = not self.is_minimized
            self.update_saved_positions()
            set_is_minimized(new_is_minimized)
            if new_is_minimized:
                self.prepare_minimized_ui()
                if properties.on_minimize:
                    properties.on_minimize()
            elif not new_is_minimized:
                self.prepare_non_minimized_ui()
                if properties.on_restore:
                    properties.on_restore()

        def on_close(e: WindowCloseEvent):
            if not self.destroying:
                self.destroying = True

                if properties.on_close:
                    if len(inspect.signature(properties.on_close).parameters) == 1:
                        properties.on_close(e)
                    else:
                        properties.on_close()

                if e.hide:
                    if self.tree and self.tree.id:
                        entity_manager.hide_tree(self.tree.id)
                    else:
                        entity_manager.hide_all_trees()

        def on_button_click_close():
            on_close(WindowCloseEvent(hide=True))

        self.on_minimize = on_minimize
        self.on_close = on_close

        title_bar_style = {
            "background_color": "272727"
        }

        title_style = {
            "padding": 8,
            "padding_left": 10,
        }
        icon_style = {
            "stroke_width": 1,
        }
        button_style = {}

        if properties.title_bar_style:
            for key, value in properties.title_bar_style.items():
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

        def title_bar():
            return div(title_bar_style, flex_direction="row", justify_content="space_between", align_items="center")[
                text(properties.title or "", **title_style),
                div(flex_direction="row")[
                    button(on_click=on_minimize, padding=8, padding_left=12, padding_right=12, **button_style)[
                        icon("minimize" if not self.is_minimized else "testing2", size=18, **icon_style),
                    ] if self.properties.show_minimize else None,
                    button(on_click=on_button_click_close, padding=8, padding_left=12, padding_right=12, **button_style)[
                        icon("close", size=20, **icon_style),
                    ] if self.properties.show_close else None,
                ],
            ],

        self.body = div()
        if properties.show_title_bar:
            self.add_child(title_bar())
        if properties.minimized_ui is not None and self.is_minimized:
            self.add_child(properties.minimized_ui())
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

    def prepare_minimized_ui(self):
        # Our tree meta state only keeps track of one drag offset
        # But window has two - minimized vs non-minimized
        # so we update the tree meta state to reflect our internal state
        if self.has_dock_behavior and last_pos_map[self.hash].get("last_docked_pos_drag_offset", None):
            try:
                self.tree.meta_state._draggable_offset[self.id] = \
                    last_pos_map[self.hash].get("last_docked_pos_drag_offset", None)
            except Exception as e:
                print(f"Error setting draggable offset: {e}")

    def prepare_non_minimized_ui(self):
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
