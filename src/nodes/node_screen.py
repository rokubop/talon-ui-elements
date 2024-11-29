from talon import actions
from ..interfaces import NodeScreenType
from ..options import UIOptions
from .node_container import NodeContainer

def print_deprecated_show():
    print(
        f"\n\n.show() directly on a node is deprecated. Use actions.user.ui_elements_show instead:\n\n"
        f"def custom_ui():\n"
        f"    screen, div, text = actions.user.ui_elements([\"screen\", \"div\", \"text\"])\n"
        f"\n"
        f"    return screen()[\n"
        f"        div()[\n"
        f"            text(\"Hello, World!\")\n"
        f"        ]\n"
        f"    ]\n"
        f"\n"
        f"actions.user.ui_elements_show(custom_ui)\n"
    )

def print_deprecated_hide():
    print(
        f"\n\n.hide() directly on a node is deprecated. Use actions.user.ui_elements_hide or actions.user.ui_elements_hide_all instead:\n\n"
        f"def custom_ui():\n"
        f"    screen, div, text = actions.user.ui_elements([\"screen\", \"div\", \"text\"])\n"
        f"\n"
        f"    return screen()[\n"
        f"        div()[\n"
        f"            text(\"Hello, World!\")\n"
        f"        ]\n"
        f"    ]\n"
        f"\n"
        f"actions.user.ui_elements_hide(custom_ui)\n"
        f"or\n"
        f"actions.user.ui_elements_hide_all()\n"
    )

class NodeScreen(NodeContainer, NodeScreenType):
    def __init__(self, element_type, options: UIOptions = None):
        super().__init__(
            element_type=element_type,
            options=options
        )
        self.screen_index = 0

    def show(self):
        print_deprecated_show()
        actions.user.ui_elements_show(lambda: self)

    def hide(self):
        print_deprecated_hide()
        actions.user.ui_elements_hide(lambda: self)