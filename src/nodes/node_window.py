from talon import actions, cron
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..events import WindowCloseEvent
from ..icons import VALID_ICON_NAMES
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
        if minimized_style is None:
            minimized_style = {"position": "absolute", "top": 100, "right": 100}

        self.has_dock_behavior = minimized_style is not None and any(
            minimized_style.get(dir) is not None
            for dir in ["top", "left", "right", "bottom"]
        )

        # Cap at 18 because title bar has finite height and larger radii don't render well
        border_radius = min(window_properties.get("border_radius", 4), 18)

        if isinstance(border_radius, tuple):
            title_bar_border_radius = (border_radius[0], border_radius[1], 0, 0)
        else:
            title_bar_border_radius = (border_radius, border_radius, 0, 0)

        resolved_window_props = {
            "draggable": True,
            "background_color": "222222",
            "drop_shadow": (0, 20, 25, 25, "000000CC"),
            "border_radius": 4,
            "border_width": 1,
            "overflow": "hidden",
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

        if resolved_window_props.get("resizable", False) and not self.is_minimized:
            saved_w = last_pos_map[self.hash].get("last_resize_width")
            saved_h = last_pos_map[self.hash].get("last_resize_height")
            if saved_w is not None:
                resolved_window_props["width"] = saved_w
            if saved_h is not None:
                resolved_window_props["height"] = saved_h

        # Resolve percentage width/height to pixels from screen
        from ..utils import get_screen
        from ..core.state_manager import state_manager
        screen_index = None
        processing_tree = state_manager.get_processing_tree()
        if processing_tree and processing_tree.root_node:
            screen_index = getattr(processing_tree.root_node.properties, 'screen', None)
        screen_rect = get_screen(screen_index).rect
        for dim, screen_size in [("width", screen_rect.width), ("height", screen_rect.height)]:
            max_dim = f"max_{dim}"
            for key in [dim, max_dim]:
                val = resolved_window_props.get(key)
                if isinstance(val, str) and "%" in val:
                    pct = float(val.replace("%", "")) / 100
                    resolved_window_props[key] = int(screen_size * pct)

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
                            elif self.tree and self.tree._tree_constructor:
                                entity_manager.hide_tree(self.tree._tree_constructor)
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
        window_icon = window_properties.get("icon", None)

        if isinstance(window_icon, str):
            if window_icon in VALID_ICON_NAMES:
                window_icon = icon(window_icon)
            else:
                raise ValueError(
                    f"Invalid window icon name: '{window_icon}'. "
                    f"Valid icon names are: {VALID_ICON_NAMES}"
                )
        elif window_icon is not None:
            svg_types = {"svg", "svg_path", "svg_rect", "svg_circle", "svg_line", "svg_polyline", "svg_polygon"}
            element_type = getattr(window_icon, "element_type", None)
            if element_type == "div":
                pass  # div wrapping an svg (e.g. from icon()) is fine
            elif element_type not in svg_types:
                raise ValueError(
                    f"window icon expects an SVG element or icon name string, "
                    f"got element type '{element_type}'"
                )

        def _find_svg_node(node):
            """Find the SVG node in an element tree for auto-scaling."""
            if getattr(node, "element_type", None) == "svg":
                return node
            for child in getattr(node, "children_nodes", []):
                result = _find_svg_node(child)
                if result:
                    return result
            return None

        def _auto_scale_icon(icon_element, target_size):
            """Auto-scale the icon's SVG to match the title font size."""
            svg_node = _find_svg_node(icon_element)
            if svg_node:
                svg_node.properties.size = target_size

        def title_bar():
            title_bar_props = {"drag_handle": True} if drag_title_bar_only else {}
            if window_icon:
                icon_size = int(title_style.get("font_size", 16))
                _auto_scale_icon(window_icon, icon_size)
                icon_title_style = {**title_style}
                container_padding = {
                    "padding_left": icon_title_style.pop("padding_left", 10),
                    "padding": icon_title_style.pop("padding", 0),
                }
                title_left = div(flex_direction="row", align_items="center", gap=6, **container_padding)[
                    window_icon,
                    text(window_properties.get("title", ""), **icon_title_style),
                ]
            else:
                title_left = text(window_properties.get("title", ""), **title_style)
            return div(title_bar_style, **title_bar_props, flex_direction="row", justify_content="space_between", align_items="stretch")[
                div(flex_direction="row", align_items="center")[title_left],
                div(flex_direction="row", align_items="stretch")[
                    button(on_click=on_minimize, padding=8, padding_left=12, padding_right=12, align_items="center", justify_content="center", **button_style)[
                        icon("minimize" if not self.is_minimized else "testing2", size=18, **icon_style),
                    ] if window_properties.get("show_minimize", True) else None,
                    button(on_click=on_button_click_close, padding=8, padding_left=12, padding_right=12, align_items="center", justify_content="center", **button_style)[
                        icon("close", size=20, **icon_style),
                    ] if window_properties.get("show_close", True) else None,
                ],
            ],

        self.body = div(flex=1, **body_properties)
        if window_properties.get("show_title_bar", True):
            self.add_child(title_bar())
        if self.is_minimized:
            minimized_body_fn = window_properties.get("minimized_body", None) or (
                lambda: div(height=24, width=200)
            )
            self.add_child(minimized_body_fn())
        else:
            self.add_child(self.body)

    def init_position(self):
        if not last_pos_map.get(self.hash):
            last_pos_map[self.hash] = {
                "last_pos": None,
                "last_docked_pos": None,
                "last_pos_drag_offset": None,
                "last_docked_pos_drag_offset": None,
                "last_resize_width": None,
                "last_resize_height": None,
            }

    @property
    def last_pos(self):
        return last_pos_map.get(self.hash, {}).get("last_pos", None)

    @property
    def last_docked_pos(self):
        return last_pos_map.get(self.hash, {}).get("last_docked_pos", None)

    def save_resize_dimensions(self, width, height):
        last_pos_map[self.hash]["last_resize_width"] = width
        last_pos_map[self.hash]["last_resize_height"] = height

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
