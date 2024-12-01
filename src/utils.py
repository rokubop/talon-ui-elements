from talon import ui
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.canvas import Canvas
from talon.screen import Screen
from talon.skia import RoundRect
from talon.types import Rect
from typing import Any, Union, Callable, TypeVar
from .interfaces import NodeType
import json
import inspect
import re
import os
import hashlib

def draw_text_simple(c, text, options, x, y):
    c.paint.color = options.color
    c.paint.textsize = options.font_size
    c.paint.font.embolden = True if options.font_weight == "bold" else False
    c.draw_text(str(text), x, y)

def get_screen(index: int = None) -> Screen:
    return ui.main_screen() if index is None else ui.screens()[index]

def canvas_from_screen(screen: Screen) -> Canvas:
    return Canvas.from_screen(screen)

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