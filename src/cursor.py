from talon.types import Rect

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