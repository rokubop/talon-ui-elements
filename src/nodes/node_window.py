from talon import actions
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..properties import Properties

last_pos = None

class NodeWindow(NodeContainer):
    def __init__(self, properties: Properties = None):
        global last_pos
        div, icon, button, text, state = actions.user.ui_elements(["div", "icon", "button", "text", "state"])
        is_minimized, set_is_minimized = state.use(f"is_minimized", False)
        window_properties = properties

        self.is_minimized = is_minimized

        if self.is_minimized:
            window_properties = Properties(
                position="absolute",
                top=last_pos.top,
                left=last_pos.left,
                min_width=200,
                draggable=True,
                background_color=properties.background_color,
                border_radius=properties.border_radius,
                border_width=properties.border_width,
                border_color=properties.border_color,
            )
        else:
            window_properties.position = "static"
            window_properties.top = None
            window_properties.left = None
            window_properties.drop_shadow = properties.drop_shadow

        super().__init__(element_type=ELEMENT_ENUM_TYPE["window"], properties=window_properties)

        def on_minimize():
            global last_pos
            new_is_minimized = not is_minimized
            last_pos = actions.user.ui_elements_get_node(self.id).box_model.border_rect
            set_is_minimized(new_is_minimized)

        def on_close():
            if window_properties.on_close:
                window_properties.on_close()
            actions.user.ui_elements_hide_all()

        def top_bar():
            return div(background_color="272727", flex_direction="row", justify_content="space_between", align_items="center")[
                text(properties.title or "", padding=8, padding_left=10),
                div(flex_direction="row")[
                    button(on_click=on_minimize, padding=8)[
                        icon("minimize", stroke_width=1, size=20),
                    ],
                    button(on_click=on_close, padding=8)[
                        icon("close", stroke_width=1, size=20),
                    ],
                ],
            ],

        self.body = div()
        self.add_child(top_bar())
        self.add_child(self.body)

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
