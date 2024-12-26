from talon import ui
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.typeface import Typeface
from talon.canvas import Canvas
from talon.screen import Screen
from talon.types import Rect
from typing import Union, Callable, TypeVar
import json
import inspect
import re
import os
import hashlib

def draw_text_simple(c: SkiaCanvas, text, properties, x, y):
    c.paint.color = properties.color
    c.paint.textsize = properties.font_size
    c.paint.typeface = Typeface.from_name(properties.font_family)
    c.paint.font.embolden = True if properties.font_weight == "bold" else False
    c.draw_text(str(text), x, y)

def get_screen(index: int = None) -> Screen:
    window = ui.active_window()
    if window:
        return window.rect
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

def get_version() -> str:
    manifest = os.path.join(os.path.dirname(__file__), '..', 'manifest.json')

    with open(manifest, 'r') as file:
        data = json.load(file)

    return data['version']

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
