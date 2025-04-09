from talon import actions
from ..constants import ELEMENT_ENUM_TYPE
from ..properties import Properties
from .node_container import NodeContainer

last_pos = None

class NodeWindow(NodeContainer):
    def __init__(self, properties: Properties = None):
        global last_pos
        # if last_pos:
        #     properties.position = "absolute"
        #     properties.top = last_pos.top
        #     properties.right = last_pos.right


        div, icon, button, text, state = actions.user.ui_elements(["div", "icon", "button", "text", "state"])
        is_minimized, set_is_minimized = state.use(f"is_minimized", False)

        self.is_minimized = is_minimized

        if self.is_minimized:
            properties.position = "absolute"
            properties.top = last_pos.top
            # properties.left = last_pos.right - last_pos.width
            properties.right = 1920 - last_pos.right
        else:
            properties.position = "static"
            properties.top = None
            properties.right = None

        super().__init__(element_type=ELEMENT_ENUM_TYPE["window"], properties=properties)

        print("my guid is ", self.guid)

        def on_minimize():
            global last_pos
            new_is_minimized = not is_minimized
            last_pos = actions.user.ui_elements_get_node(f"title_bar_{self.guid}").box_model.border_rect
            if new_is_minimized:
                print("on_minimize last_pos", last_pos)
                print("top", last_pos.top)
                print("expect right to be 180", last_pos.right)
            set_is_minimized(new_is_minimized)

        # def on_maximize():
        #     print("Maximize window")

        def on_close():
            actions.user.ui_elements_hide_all()

        def top_bar():
            return div(id=f"title_bar_{self.guid}", background_color="272727", flex_direction="row", justify_content="space_between", align_items="center")[
                text(properties.title or "", padding=8, padding_left=10),
                div(flex_direction="row")[
                    button(on_click=on_minimize, padding=8)[
                        icon("minimize", stroke_width=1, size=20),
                    ],
                    # button(on_click=on_maximize)[
                    #     icon("maximize", padding=8, stroke_width=1, size=20),
                    # ],
                    button(on_click=on_close, padding=8)[
                        icon("close", stroke_width=1, size=20),
                    ],
                ],
            ],

        self.body = div(padding=4)
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
