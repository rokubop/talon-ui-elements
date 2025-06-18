
from dataclasses import dataclass, field
from typing import Any

@dataclass
class StateEvent:
    not_implemented: Any = field(default=None)

@dataclass
class DragEndEvent:
    not_implemented: Any = field(default=None)

@dataclass
class WindowCloseEvent:
    hide: bool = field(default=True)