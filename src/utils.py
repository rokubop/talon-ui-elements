from talon import ui
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.typeface import Typeface
from talon.screen import Screen
from talon.types import Rect
from typing import Union, Callable, TypeVar
from .constants import NAMED_COLORS_TO_HEX
from dataclasses import dataclass
import hashlib
import inspect
import json
import os
import re

def draw_text_simple(c: SkiaCanvas, text, properties, x, y):
    c.paint.color = properties.color
    c.paint.textsize = properties.font_size
    c.paint.typeface = Typeface.from_name(properties.font_family)
    c.paint.font.embolden = True if properties.font_weight == "bold" else False
    c.draw_text(str(text), x, y)

def get_screen(index: int = None) -> Screen:
    return ui.main_screen() if index is None else ui.screens()[index]

def generate_hash(obj: Union[Callable, dict]) -> str:
    hasher = hashlib.sha256()

    if callable(obj):
        func_name = f"{obj.__module__}.{obj.__qualname__}"
        hasher.update(func_name.encode())
    elif isinstance(obj, str):
        return obj
    else:
        raise TypeError("Object must be a callable or a dictionary.")

    return hasher.hexdigest()

@dataclass
class Version:
    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __lt__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) <= (other.major, other.minor, other.patch)

    def __eq__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __gt__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ge__(self, version: str) -> bool:
        other = Version.from_string(version) if isinstance(version, str) else version
        return (self.major, self.minor, self.patch) >= (other.major, other.minor, other.patch)

    @classmethod
    def from_string(cls, version: str) -> "Version":
        major, minor, patch = map(int, version.split("."))
        return cls(major, minor, patch)

    @classmethod
    def from_dict(cls, version: dict) -> "Version":
        return cls(version["major"], version["minor"], version["patch"])

    def to_dict(self) -> dict:
        return {"major": self.major, "minor": self.minor, "patch": self.patch}

def get_version() -> str:
    manifest = os.path.join(os.path.dirname(__file__), '..', 'manifest.json')

    with open(manifest, 'r') as file:
        data = json.load(file)

    return Version.from_string(data['version'])

def sanitize_string(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_]', '_', text)

E = TypeVar("E")

def safe_callback(callback: Callable[[E], None], event: E) -> None:
    """If the callback has no parameters, call it without any arguments"""
    sig = inspect.signature(callback)
    if len(sig.parameters) == 0:
        callback()
    else:
        callback(event)

def get_center(rect: Rect) -> tuple[int, int]:
    return rect.x + rect.width // 2, rect.y + rect.height // 2

def get_active_color_from_highlight_color(highlight_color: str) -> str:
    """If highlightcolor is "FFFFFF66", return "FFFFFF88"."""
    base_color = highlight_color[:-2]  # "FFFFFF"
    alpha = highlight_color[-2:]       # "66"

    new_alpha = max(0, min(255, int(alpha, 16) + 20))
    new_alpha_hex = f"{new_alpha:02X}"

    return base_color + new_alpha_hex

def hex_color(color: str) -> str:
    """Resolve color to hex if it's a named color or validate hex format."""

    if all(c in "0123456789ABCDEFabcdef" for c in color):
        # already hex
        return color

    return NAMED_COLORS_TO_HEX.get(color.lower(), color)

def get_combined_screens_rect() -> Rect:
    screens = ui.screens()
    x = min(screen.x for screen in screens)
    y = min(screen.y for screen in screens)
    max_right = max(screen.x + screen.width for screen in screens)
    max_bottom = max(screen.y + screen.height for screen in screens)
    width = max_right - x
    height = max_bottom - y
    return Rect(x, y, width, height)