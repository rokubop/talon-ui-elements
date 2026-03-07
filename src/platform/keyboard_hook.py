"""
Platform-specific low-level keyboard hook for capturing keystrokes.
Used by the custom canvas-rendered text input (when ui_elements_custom_input is enabled).
"""

from talon import app
from dataclasses import dataclass
from typing import Callable, Optional

@dataclass
class KeyEvent:
    key: str
    vk: int
    scan: int
    down: bool
    shift: bool = False
    ctrl: bool = False
    alt: bool = False

    @property
    def up(self):
        return not self.down

    @property
    def char(self) -> Optional[str]:
        """Return the printable character for this key, or None."""
        if self.ctrl or self.alt:
            return None
        if len(self.key) == 1:
            return self.key.upper() if self.shift else self.key
        return None

KeyCallback = Callable[[KeyEvent], Optional[bool]]
