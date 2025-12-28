"""
Border radius utilities for per-corner rounded rectangles.
"""
from dataclasses import dataclass
from typing import Union
from talon.types import Rect
from talon.skia import Path, RoundRect
from talon.skia.canvas import Canvas as SkiaCanvas


@dataclass
class BorderRadius:
    """
    Represents border radius values for each corner of a rectangle.
    
    Can be initialized with:
    - Single value (int/float): uniform radius for all corners
    - Tuple of 4 values: (top_left, top_right, bottom_right, bottom_left)
    - Another BorderRadius instance: copy constructor
    """
    top_left: float = 0
    top_right: float = 0
    bottom_right: float = 0
    bottom_left: float = 0
    
    def __init__(self, value=0):
        if isinstance(value, (int, float)):
            # Uniform radius
            self.top_left = self.top_right = self.bottom_right = self.bottom_left = float(value)
        elif isinstance(value, (tuple, list)) and len(value) == 4:
            # Per-corner: (top_left, top_right, bottom_right, bottom_left)
            self.top_left = float(value[0])
            self.top_right = float(value[1])
            self.bottom_right = float(value[2])
            self.bottom_left = float(value[3])
        elif isinstance(value, BorderRadius):
            # Copy constructor
            self.top_left = value.top_left
            self.top_right = value.top_right
            self.bottom_right = value.bottom_right
            self.bottom_left = value.bottom_left
        else:
            # Default to 0
            self.top_left = self.top_right = self.bottom_right = self.bottom_left = 0.0
    
    def is_uniform(self) -> bool:
        """Check if all corners have the same radius."""
        return (self.top_left == self.top_right == 
                self.bottom_right == self.bottom_left)
    
    def has_radius(self) -> bool:
        """Check if any corner has a non-zero radius."""
        return any([self.top_left, self.top_right, self.bottom_right, self.bottom_left])
    
    def scale(self, factor: float) -> 'BorderRadius':
        """Return a new BorderRadius with all values scaled by factor."""
        return BorderRadius((
            self.top_left * factor,
            self.top_right * factor,
            self.bottom_right * factor,
            self.bottom_left * factor
        ))


def create_rounded_rect_path(rect: Rect, border_radius: BorderRadius) -> Path:
    """
    Manually construct a rounded rectangle path with per-corner radii.
    Uses cubic bezier curves to approximate circular arcs.
    
    Args:
        rect: Rectangle bounds
        border_radius: BorderRadius object with per-corner radii
        
    Returns:
        Path object representing the rounded rectangle
    """
    path = Path()
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    
    # Clamp radii to prevent overlaps
    # Each corner radius cannot exceed half the width or height
    max_radius_x = w / 2
    max_radius_y = h / 2
    
    tl = min(border_radius.top_left, max_radius_x, max_radius_y)
    tr = min(border_radius.top_right, max_radius_x, max_radius_y)
    br = min(border_radius.bottom_right, max_radius_x, max_radius_y)
    bl = min(border_radius.bottom_left, max_radius_x, max_radius_y)
    
    # Magic number for circular arc approximation with cubic bezier
    # This value creates a smooth 90-degree arc that closely approximates a quarter circle
    kappa = 0.5522847498
    
    # Start from top-left corner (after the arc)
    path.move_to(x + tl, y)
    
    # Top edge
    path.line_to(x + w - tr, y)
    
    # Top-right corner
    if tr > 0:
        path.cubic_to(
            x + w - tr + (tr * kappa), y,
            x + w, y + tr - (tr * kappa),
            x + w, y + tr
        )
    
    # Right edge
    path.line_to(x + w, y + h - br)
    
    # Bottom-right corner
    if br > 0:
        path.cubic_to(
            x + w, y + h - br + (br * kappa),
            x + w - br + (br * kappa), y + h,
            x + w - br, y + h
        )
    
    # Bottom edge
    path.line_to(x + bl, y + h)
    
    # Bottom-left corner
    if bl > 0:
        path.cubic_to(
            x + bl - (bl * kappa), y + h,
            x, y + h - bl + (bl * kappa),
            x, y + h - bl
        )
    
    # Left edge
    path.line_to(x, y + tl)
    
    # Top-left corner
    if tl > 0:
        path.cubic_to(
            x, y + tl - (tl * kappa),
            x + tl - (tl * kappa), y,
            x + tl, y
        )
    
    path.close()
    return path


def draw_rounded_rect(canvas: SkiaCanvas, rect: Rect, border_radius: Union[int, float, tuple, BorderRadius, None]):
    """
    Draw a rounded rectangle, using the most efficient method available.
    
    For uniform radius (all corners the same), uses the native draw_rrect for performance.
    For per-corner radius, constructs a path manually.
    
    Args:
        canvas: Skia canvas to draw on
        rect: Rectangle to draw
        border_radius: int, float, tuple of 4 values, or BorderRadius object
    """
    # Normalize to BorderRadius object
    if isinstance(border_radius, (int, float)):
        br = BorderRadius(border_radius)
    elif isinstance(border_radius, (tuple, list)):
        br = BorderRadius(border_radius)
    elif isinstance(border_radius, BorderRadius):
        br = border_radius
    elif not border_radius:
        # No radius, just draw a regular rectangle
        canvas.draw_rect(rect)
        return
    else:
        # Unknown type, default to no radius
        canvas.draw_rect(rect)
        return
    
    if not br.has_radius():
        # No radius, draw regular rectangle
        canvas.draw_rect(rect)
    elif br.is_uniform():
        # Fast path: use native round rect
        canvas.draw_rrect(RoundRect.from_rect(rect, x=br.top_left, y=br.top_left))
    else:
        # Slow path: manually construct shape with per-corner radii
        path = create_rounded_rect_path(rect, br)
        canvas.draw_path(path)
