from talon import actions, ui
from talon.screen import Screen
from ..interfaces import NodeRootType
from ..properties import NodeRootProperties
from ..constants import LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION, LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION
from .node_container import NodeContainer
from ..utils import get_screen

def print_deprecated_show():
    print(
        f"\n\nDeprecationWarning: .show() directly on `screen` ui_element is deprecated. {LOG_MESSAGE_UI_ELEMENTS_SHOW_SUGGESTION}"
    )

def print_deprecated_hide():
    print(
        f"\n\nDeprecationWarning: .hide() directly on `screen` ui_element is deprecated. {LOG_MESSAGE_UI_ELEMENTS_HIDE_SUGGESTION}"
    )

class DeprecatedRenderer:
    """
    Previously, `screen` was the main interface for .show(), .hide(),
    and highlighting UI elements. Now, it is wrapped in a function
    and passed to actions.user.ui_elements_show(...). A higher-level
    "tree" now manages these interactions.
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

class NodeRoot(NodeContainer, NodeRootType):
    def __init__(self, element_type, properties: NodeRootProperties = None):
        super().__init__(
            element_type=element_type,
            properties=properties
        )
        self.boundary_rect = None

        if element_type == "screen":
            ref_screen: Screen = get_screen(None if properties.screen is None else properties.screen)
            self.boundary_rect = ref_screen.rect
        elif element_type == "active_window":
            active_window = ui.active_window()
            self.boundary_rect = active_window.rect

        self.properties.width = int(self.boundary_rect.width)
        self.properties.height = int(self.boundary_rect.height)

        self.screen_index = self.properties.screen or 0
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