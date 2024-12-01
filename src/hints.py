from talon import Module
from .state_manager import state_manager

mod = Module()
mod.tag("ui_elements_hints_active", desc="tag for ui elements")

@mod.capture(rule="<user.letter> <user.letter>")
def ui_elements_hint_target(m) -> list[str]:
    return "".join(m.letter_list)

@mod.action_class
class Actions:
    def ui_elements_hint_action(ui_elements_hint_target: str):
        """Trigger hint action"""
        state_manager.trigger_hint_action(ui_elements_hint_target)
