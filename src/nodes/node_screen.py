from talon import actions
from ..interfaces import NodeScreenType
from ..options import UIOptions
from ..constants import LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION, LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION
from .node_container import NodeContainer

def print_deprecated_show():
    print(
        f"\n\nWARNING: .show() directly on ui_elements is deprecated. {LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION}"
    )

def print_deprecated_hide():
    print(
        f"\n\nWARNING: .hide() directly on ui_elements is deprecated. {LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION}"
    )

class DeprecatedRenderer:
    """
    `screen` used to be the primary thing you interact with for
    .show(), .hide(), and highlighting ui_elements,
    but now we wrap it in a function and pass it to
    actions.user.ui_elements_show(...), and have a higher level
    "tree" which manages everything now.
    """
    def __init__(self, obj):
        self.obj = obj
        self._unique_id = id(self)
        self.__qualname__ = f"DeprecatedRenderer_{self._unique_id}"

    def __call__(self):
        return self.obj

    def __hash__(self):
        return self._unique_id

    def __eq__(self, other):
        return self is other

class NodeScreen(NodeContainer, NodeScreenType):
    def __init__(self, element_type, options: UIOptions = None):
        super().__init__(
            element_type=element_type,
            options=options
        )
        self.screen_index = 0
        self.deprecated_ui = None

    def show(self):
        """DEPRECATED: Use `actions.user.ui_elements_show(...)` instead"""
        print_deprecated_show()
        if not self.deprecated_ui:
            self.deprecated_ui = DeprecatedRenderer(self)
        actions.user.ui_elements_show(self.deprecated_ui)

    def hide(self):
        """DEPRECATED: Use `actions.user.ui_elements_hide(...)` or `actions.user.ui_elements_hide_all()` instead"""
        print_deprecated_hide()
        if not self.deprecated_ui:
            self.deprecated_ui = DeprecatedRenderer(self)
        actions.user.ui_elements_hide(self.deprecated_ui)

    def highlight(self, key):
        """DEPRECATED: Use `actions.user.ui_elements_highlight(...)` instead"""
        actions.user.ui_elements_highlight(key)

    def highlight_briefly(self, key):
        """DEPRECATED: Use `actions.user.ui_elements_highlight_briefly(...)` instead"""
        actions.user.ui_elements_highlight_briefly(key)

    def unhighlight(self, key):
        """DEPRECATED: Use `actions.user.ui_elements_unhighlight(...)` instead"""
        actions.user.ui_elements_unhighlight(key)