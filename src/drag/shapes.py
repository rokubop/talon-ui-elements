"""What a drag draws while it is held.

A session emits shapes; the overlay draws them. The overlay never learns
which kind of drag it is, so a new drag mode is a new session file.
"""

from dataclasses import dataclass
from typing import Optional, Union

from talon.skia import RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.types import Rect

from ..border_radius import BorderRadius
from ..constants import (
    DRAG_DIM_COLOR,
    DRAG_GHOST_COLOR,
    DRAG_GHOST_FILL_COLOR,
    DRAG_GHOST_STROKE_WIDTH,
)
from ..utils import scale_value


@dataclass
class Outline:
    """Where the dragged thing will land."""
    rect: Rect
    radius: Optional[Union[BorderRadius, float]] = None
    color: str = DRAG_GHOST_COLOR
    fill_color: Optional[str] = DRAG_GHOST_FILL_COLOR
    stroke_width: float = DRAG_GHOST_STROKE_WIDTH


@dataclass
class Dim:
    """Where it still sits."""
    rect: Rect
    radius: Optional[Union[BorderRadius, float]] = None
    color: Optional[str] = DRAG_DIM_COLOR


@dataclass
class InsertLine:
    """Where an item would drop in a list. Nothing emits one yet."""
    rect: Rect
    color: str = DRAG_GHOST_COLOR
    thickness: float = DRAG_GHOST_STROKE_WIDTH


def _corner(radius) -> float:
    if radius is None:
        return 0.0
    if isinstance(radius, BorderRadius):
        return float(radius.top_left)
    return float(radius)


def _draw(canvas: SkiaCanvas, rect: Rect, radius) -> None:
    r = _corner(radius)
    if r > 0:
        canvas.draw_rrect(RoundRect.from_rect(rect, x=r, y=r))
    else:
        canvas.draw_rect(rect)


def draw_shapes(canvas: SkiaCanvas, shapes) -> None:
    for shape in shapes:
        if isinstance(shape, Dim):
            if not shape.color:
                continue
            canvas.paint.style = canvas.paint.Style.FILL
            canvas.paint.color = shape.color
            _draw(canvas, shape.rect, shape.radius)
        elif isinstance(shape, Outline):
            if shape.fill_color:
                canvas.paint.style = canvas.paint.Style.FILL
                canvas.paint.color = shape.fill_color
                _draw(canvas, shape.rect, shape.radius)
            canvas.paint.style = canvas.paint.Style.STROKE
            canvas.paint.color = shape.color
            canvas.paint.stroke_width = scale_value(shape.stroke_width)
            _draw(canvas, shape.rect, shape.radius)
        elif isinstance(shape, InsertLine):
            canvas.paint.style = canvas.paint.Style.FILL
            canvas.paint.color = shape.color
            canvas.draw_rect(shape.rect)
