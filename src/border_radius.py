from dataclasses import dataclass
from talon.types import Rect
from talon.skia import Path

try:
    from skia import PathBuilder
except ImportError:
    PathBuilder = None


@dataclass
class BorderRadius:
    """
    Can be:
    - Single value (int/float): uniform radius for all corners
    - Tuple of 4 values: (top_left, top_right, bottom_right, bottom_left)
    - Copy constructor
    """
    top_left: float = 0
    top_right: float = 0
    bottom_right: float = 0
    bottom_left: float = 0

    def __init__(self, value=0):
        if isinstance(value, (int, float)):
            self.top_left = self.top_right = self.bottom_right = self.bottom_left = float(value)
        elif isinstance(value, tuple) and len(value) == 4:
            self.top_left = float(value[0])
            self.top_right = float(value[1])
            self.bottom_right = float(value[2])
            self.bottom_left = float(value[3])
        elif isinstance(value, BorderRadius):
            self.top_left = value.top_left
            self.top_right = value.top_right
            self.bottom_right = value.bottom_right
            self.bottom_left = value.bottom_left
        else:
            self.top_left = self.top_right = self.bottom_right = self.bottom_left = 0.0

        self._has_radius = bool(self.top_left or self.top_right or self.bottom_right or self.bottom_left)
        self._is_uniform = (self.top_left == self.top_right == self.bottom_right == self.bottom_left)

    def is_uniform(self) -> bool:
        return self._is_uniform

    def has_radius(self) -> bool:
        return self._has_radius

    def scale(self, factor: float) -> 'BorderRadius':
        return BorderRadius((
            self.top_left * factor,
            self.top_right * factor,
            self.bottom_right * factor,
            self.bottom_left * factor
        ))


def _build_rounded_rect(builder, rect: Rect, border_radius: BorderRadius):
    """Build rounded rect path commands on a Path or PathBuilder."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height

    max_radius_x = w / 2
    max_radius_y = h / 2

    tl = min(border_radius.top_left, max_radius_x, max_radius_y)
    tr = min(border_radius.top_right, max_radius_x, max_radius_y)
    br = min(border_radius.bottom_right, max_radius_x, max_radius_y)
    bl = min(border_radius.bottom_left, max_radius_x, max_radius_y)

    kappa = 0.5522847498

    builder.move_to(x + tl, y)
    builder.line_to(x + w - tr, y)

    if tr > 0:
        builder.cubic_to(
            x + w - tr + (tr * kappa), y,
            x + w, y + tr - (tr * kappa),
            x + w, y + tr
        )

    builder.line_to(x + w, y + h - br)

    if br > 0:
        builder.cubic_to(
            x + w, y + h - br + (br * kappa),
            x + w - br + (br * kappa), y + h,
            x + w - br, y + h
        )

    builder.line_to(x + bl, y + h)

    if bl > 0:
        builder.cubic_to(
            x + bl - (bl * kappa), y + h,
            x, y + h - bl + (bl * kappa),
            x, y + h - bl
        )

    builder.line_to(x, y + tl)

    if tl > 0:
        builder.cubic_to(
            x, y + tl - (tl * kappa),
            x + tl - (tl * kappa), y,
            x + tl, y
        )

    builder.close()


def draw_manual_rounded_rect_path(rect: Rect, border_radius: BorderRadius) -> Path:
    """Special helper in absence of native per-corner rounded rect support."""
    if PathBuilder:
        builder = PathBuilder()
        _build_rounded_rect(builder, rect, border_radius)
        return builder.detach()
    else:
        path = Path()
        _build_rounded_rect(path, rect, border_radius)
        return path
