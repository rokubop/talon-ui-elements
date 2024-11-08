from talon import Module, actions
from ..src.state import state
from ..src.actions import ui_elements_new

mod = Module()

@mod.action_class
class Actions:
    def private_ui_elements_test():
        """Test the UI elements"""
        (div, text, screen) = ui_elements_new(["div", "text", "screen"])

        ui = screen(justify_content="center", align_items="center")[
            div(background_color="white", padding=16, border_radius=16, border_width=1)[
                text("Hello world", color="red", font_size=24)
            ]
        ]

        # print(f"UI: {ui}")
        # print(f"State: {vars(state)}")

        print(f"Expected nodes: 3.  Actual state: {len(state.nodes)}")

        # self.assertEqual(len(state.nodes), 3)