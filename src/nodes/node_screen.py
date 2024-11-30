from talon import actions
from ..interfaces import NodeScreenType
from ..options import UIOptions
from .node_container import NodeContainer

def print_deprecated_show():
    print(
        f"\n\nWARNING: .show() directly on ui_elements is deprecated. Instead create a function that returns the ui_elements, and pass the function to actions.user.ui_elements_show(...)."
    )

def print_deprecated_hide():
    print(
        f"\n\nWARNING: .hide() directly on ui_elements is deprecated. Instead create a function that returns the ui_elements, and pass the function to actions.user.ui_elements_hide(...), or use actions.user.ui_elements_hide_all()."
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