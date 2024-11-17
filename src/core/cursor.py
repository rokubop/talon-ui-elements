from talon.screen import Screen

class Cursor:
    def __init__(self, screen: Screen):
        self.screen = screen
        self.x = screen.x
        self.y = screen.y
        self.virtual_x = screen.x
        self.virtual_y = screen.y

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.virtual_x = x
        self.virtual_y = y

    def virtual_move_to(self, x, y):
        self.virtual_x = x
        self.virtual_y = y

    def reset(self):
        self.x = self.screen.x
        self.y = self.screen.y
        self.virtual_x = self.screen.x
        self.virtual_y = self.screen.y

    def __str__(self):
        return f"Cursor Position: ({self.x}, {self.y}, {self.virtual_x}, {self.virtual_y})"