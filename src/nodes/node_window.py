from talon import actions
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..properties import Properties, NodeWindowProperties
from ..utils import generate_hash

last_pos_map = {}

class NodeWindow(NodeContainer):
    def __init__(self, properties: Properties = None):
        global last_pos_map
        div, icon, button, text, state = actions.user.ui_elements(["div", "icon", "button", "text", "state"])
        # TODO: Allow multiple windows - is_minimized state
        is_minimized, set_is_minimized = state.use("is_minimized", properties.minimized)
        window_properties = properties

        self.init_position(properties)
        last_pos = self.last_pos
        last_docked_pos = self.last_docked_pos

        self.is_minimized = is_minimized
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
                    # TODO: fix close when minimized
                    # on_close=properties.on_close,
            )
        else:
            window_properties.position = "absolute" if last_pos is not None else "static"
            window_properties.top = last_pos.top if last_pos is not None else None
            window_properties.left = last_pos.left if last_pos is not None else None
            window_properties.drop_shadow = properties.drop_shadow

        super().__init__(element_type=ELEMENT_ENUM_TYPE["window"], properties=window_properties)

        def on_minimize():
            global last_pos_map
            new_is_minimized = not self.is_minimized
            if self.has_dock_behavior and self.is_minimized:
                self.set_last_docked_pos(
                    actions.user.ui_elements_get_node(self.id).box_model.border_rect
                )
            else:
                self.set_last_pos(
                    actions.user.ui_elements_get_node(self.id).box_model.border_rect
                )
            set_is_minimized(new_is_minimized)
            if new_is_minimized and window_properties.on_minimize:
                window_properties.on_minimize()
            elif not new_is_minimized and window_properties.on_restore:
                window_properties.on_restore()

        def on_close():
            if window_properties.on_close:
                window_properties.on_close()
            actions.user.ui_elements_hide_all()

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
                    button(on_click=on_close, padding=8, padding_left=12, padding_right=12, **button_style)[
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

    def init_position(self, properties: Properties):
        global last_pos_map
        self.hash = properties.hash()

        if not last_pos_map.get(self.hash):
            last_pos_map[self.hash] = {
                "last_pos": None,
                "last_docked_pos": None,
            }

    @property
    def last_pos(self):
        global last_pos_map
        return last_pos_map.get(self.hash, {}).get("last_pos", None)

    @property
    def last_docked_pos(self):
        global last_pos_map
        return last_pos_map.get(self.hash, {}).get("last_docked_pos", None)

    def set_last_pos(self, pos):
        global last_pos_map
        if self.hash not in last_pos_map:
            last_pos_map[self.hash] = {
                "last_pos": None,
                "last_docked_pos": None,
            }
        last_pos_map[self.hash]["last_pos"] = pos

    def set_last_docked_pos(self, pos):
        global last_pos_map
        if self.hash not in last_pos_map:
            last_pos_map[self.hash] = {
                "last_pos": None,
                "last_docked_pos": None,
            }
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
