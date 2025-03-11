from talon.types import Rect
from .interfaces import Point2d

class Cursor:
    def __init__(self, boundary: Rect):
        self.boundary = boundary
        self.x = boundary.x
        self.y = boundary.y
        self.virtual_x = boundary.x
        self.virtual_y = boundary.y

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.virtual_x = x
        self.virtual_y = y

    def virtual_move_to(self, x, y):
        self.virtual_x = x
        self.virtual_y = y

    def reset(self):
        self.x = self.boundary.x
        self.y = self.boundary.y
        self.virtual_x = self.boundary.x
        self.virtual_y = self.boundary.y

    def __str__(self):
        return f"Cursor Position: ({self.x}, {self.y}, {self.virtual_x}, {self.virtual_y})"

class CursorV2:
    def __init__(self, init_pos: Point2d):
        self.init_pos = init_pos
        self.x = init_pos.x
        self.y = init_pos.y

    def move_to(self, x, y):
        self.x = x
        self.y = y

    def reset(self):
        self.x = self.init_pos.x
        self.y = self.init_pos.y

    def to_point2d(self):
        return Point2d(self.x, self.y)

    def offset(self, x, y):
        self.x += x
        self.y += y

    def __str__(self):
        return f"Cursor Position: ({self.x}, {self.y})"