from talon import ui
from talon.canvas import Canvas
from talon.screen import Screen
from typing import Union, Callable
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