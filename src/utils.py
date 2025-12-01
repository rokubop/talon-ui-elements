import hashlib
import inspect
import re
from talon import ui
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.skia.paint import Paint
from talon.screen import Screen
from talon.types import Rect
from typing import Union, Callable, TypeVar
from .constants import NAMED_COLORS_TO_HEX
from .fonts import get_typeface

def draw_text_simple(c: SkiaCanvas, text, color, properties, x, y):
    paint = Paint()
    paint.textsize = properties.font_size
    c.paint.antialias = True
    if properties.font_family:
        typeface = get_typeface(properties.font_family, properties.font_weight)
        if typeface:
            paint.typeface = typeface
    if properties.font_weight == "bold":
        paint.font.embolden = True

    if properties.stroke_color:
        paint.style = paint.Style.STROKE
        paint.color = properties.stroke_color
        paint.stroke_width = properties.stroke_width or 1
        c.draw_text(str(text), x, y, paint)

    paint.style = paint.Style.FILL
    paint.color = color
    c.draw_text(str(text), x, y, paint)

def get_screen(index: int = None) -> Screen:
    return ui.main_screen() if index is None else ui.screens()[index]

def generate_hash(obj: Union[Callable, dict]) -> str:
    hasher = hashlib.sha256()

    if callable(obj):
        func_name = f"{obj.__module__}.{obj.__qualname__}"
        hasher.update(func_name.encode())
    elif isinstance(obj, str):
        return obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, str):
                hasher.update(f"{key}:{value}".encode())
            elif callable(value):
                # Handle function objects
                func_name = f"{value.__module__}.{value.__qualname__}"
                hasher.update(f"{key}:{func_name}".encode())
            else:
                # For other types, use string representation
                hasher.update(f"{key}:{str(value)}".encode())
    else:
        raise TypeError("Object must be a callable or a dictionary.")

    return hasher.hexdigest()

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

def adjust_color_brightness(color: str, adjustment: int = 5) -> str:
    """Adjust the brightness of a hex color by a specified amount.

    Args:
        color: Hex color string (e.g., "222222" or "#222222")
        adjustment: Amount to add/subtract from each RGB component (-255 to 255)
                   Positive values brighten, negative values darken

    Returns:
        Adjusted hex color string
    """
    color = color.lstrip('#')

    if len(color) == 3:
        color = ''.join([c*2 for c in color])

    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)

    r = max(0, min(255, r + adjustment))
    g = max(0, min(255, g + adjustment))
    b = max(0, min(255, b + adjustment))

    # Convert back to hex
    return f"{r:02X}{g:02X}{b:02X}"

def hex_color(color: str, property_name: str = None) -> str:
    """Resolve color to hex if it's a named color or validate hex format."""

    if not color:
        return color

    # Strip leading # if present
    if color.startswith('#'):
        color = color[1:]

    if all(c in "0123456789ABCDEFabcdef" for c in color):
        # already hex - validate length
        if len(color) not in [3, 4, 6, 8]:
            prop_msg = f" for property '{property_name}'" if property_name else ""
            raise ValueError(
                f"\nInvalid color{prop_msg}: '{color}'\n"
                f"Hex colors must be 3, 4, 6, or 8 characters (got {len(color)}).\n"
                f"Valid formats: 'FFF', 'FFFF', 'FFFFFF', 'FFFFFF66' (last 2 digits = opacity)\n"
            )
        return color

    # Check for common CSS values that aren't supported
    common_css_values = ['transparent', 'inherit', 'currentcolor', 'initial', 'unset']
    if color.lower() in common_css_values:
        prop_msg = f" for property '{property_name}'" if property_name else ""
        raise ValueError(
            f"\nInvalid color{prop_msg}: '{color}'\n"
            f"CSS value '{color}' is not supported.\n"
            f"For transparency, use:\n"
            f"  - 8-character hex with alpha: 'FFFFFF66' (last 2 digits control opacity)\n"
            f"  - opacity property: opacity=0.5\n"
            f"  - Don't set background_color (buttons default to transparent background)\n"
        )

    # Try to resolve as named color
    resolved = NAMED_COLORS_TO_HEX.get(color.lower())
    if resolved:
        return resolved.lstrip('#')

    # Unknown color value
    prop_msg = f" for property '{property_name}'" if property_name else ""
    raise ValueError(
        f"\nInvalid color{prop_msg}: '{color}'\n"
        f"Use hex colors (e.g., 'FF0000', 'FFFFFF66') or named colors:\n"
        f"  {', '.join(list(NAMED_COLORS_TO_HEX.keys())[:10])}...\n"
    )

def get_combined_screens_rect() -> Rect:
    screens = ui.screens()
    x = min(screen.x for screen in screens)
    y = min(screen.y for screen in screens)
    max_right = max(screen.x + screen.width for screen in screens)
    max_bottom = max(screen.y + screen.height for screen in screens)
    width = max_right - x
    height = max_bottom - y
    return Rect(x, y, width, height)

def subtract_rect(outer: Rect, inner: Rect) -> list[Rect]:
    rects = []

    if inner.top > outer.top:
        rects.append(Rect(outer.left, outer.top, outer.width, inner.top - outer.top))

    if inner.bot < outer.bot:
        rects.append(Rect(outer.left, inner.bot, outer.width, outer.bot - inner.bot))

    if inner.left > outer.left:
        rects.append(Rect(outer.left, inner.top, inner.left - outer.left, inner.height))

    if inner.right < outer.right:
        rects.append(Rect(inner.right, inner.top, outer.right - inner.right, inner.height))

    return rects

def find_closest_parent_with_id(node):
    """Find the closest parent node that has an ID."""
    current_node = node
    while current_node:
        if current_node.id:
            return current_node
        current_node = current_node.parent_node
    return None