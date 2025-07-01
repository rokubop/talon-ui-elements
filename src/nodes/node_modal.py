from talon import actions
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..properties import Properties

# Experimental - WIP
class NodeModal(NodeContainer):
    def __init__(self, modal_properties: Properties = None, contents_properties: dict = None):
        # self.children_nodes = []
        div, icon, button, text = actions.user.ui_elements(["div", "icon", "button", "text"])

        # Use the open property to determine visibility
        self.is_open = modal_properties.open if hasattr(modal_properties, 'open') else False
        self.on_close = modal_properties.on_close if hasattr(modal_properties, 'on_close') else None
        self.show_title_bar = modal_properties.show_title_bar if hasattr(modal_properties, 'show_title_bar') else True

        # Initialize with provided properties
        super().__init__(element_type=ELEMENT_ENUM_TYPE["modal"], properties=modal_properties)

        if not self.is_open:
            return None

        def on_close_modal():
            if self.on_close:
                self.on_close()

        def create_backdrop():
            if hasattr(modal_properties, 'backdrop') and modal_properties.backdrop is False:
                return div()

            backdrop_color = modal_properties.backdrop_color if hasattr(modal_properties, 'backdrop_color') else "00000080"
            backdrop_click_close = modal_properties.backdrop_click_close if hasattr(modal_properties, 'backdrop_click_close') else True

            return button(
                position="fixed",
                top=0,
                left=0,
                width="100%",
                height="100%",
                highlight_color="00000000",
                background_color=backdrop_color,
                z_index=1,
                on_click=on_close_modal if backdrop_click_close else None
            )

        def title_bar():
            if not self.show_title_bar:
                return None

            return div(background_color="272727", flex_direction="row", justify_content="space_between", align_items="center")[
                text(modal_properties.title or "", padding=8, padding_left=10),
                div(flex_direction="row")[
                    button(on_click=on_close_modal, padding=8, padding_left=12, padding_right=12)[
                        icon("close", stroke_width=1, size=20),
                    ],
                ],
            ]

        self.body = div(contents_properties)

        # Add backdrop if needed
        # backdrop_element = create_backdrop()
        # if backdrop_element:
        #     self.add_child(backdrop_element)

        # # Add title bar if needed
        # if self.show_title_bar:
        #     title_bar_element = title_bar()
        #     if title_bar_element:
        #         self.add_child(title_bar_element)

        # Add content container
        self.add_child(self.body)

    def __getitem__(self, children_nodes=None):
        if not self.is_open:
            self.children_nodes = []
            return self

        if children_nodes is None:
            children_nodes = []

        if not isinstance(children_nodes, list):
            children_nodes = [children_nodes]

        for node in children_nodes:
            print(f"Adding child node: {node}")
            self.body.add_child(node)

        return self
