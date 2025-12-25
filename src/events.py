
from dataclasses import dataclass, field
from typing import Any

@dataclass
class StateEvent:
    not_implemented: Any = field(default=None)

@dataclass
class DragEndEvent:
    not_implemented: Any = field(default=None)

class WindowCloseEvent:
    def __init__(self, hide: bool = True):
        self.hide = hide
        self._default_prevented = False

    def prevent_default(self):
        """Prevent the window from closing"""
        self._default_prevented = True

    @property
    def default_prevented(self):
        return self._default_prevented