from talon import Module, Context

mod = Module()
ctx = Context()
ctx_hints_active_browser = Context()

# Import after creating ctx so src/hints can access it
from .src.hints import (
    trigger_hint_click,
    trigger_hint_focus,
    focus_next,
    focus_previous,
    set_hint_context,
    show_scale_notification,
)
from .src.core.entity_manager import entity_manager

# Pass ctx to src/hints so it can enable/disable tags. Context objects must stay here (not src/)
# because user reloads trigger import chain reloading of src files, but this file isn't imported
# by Python (only loaded by Talon), so Module/Context objects survive and .talon bindings stay intact.
set_hint_context(ctx, ctx_hints_active_browser)

mod.tag("ui_elements_hints_active", desc="tag for ui elements")

ctx_hints_active_browser.matches = """
tag: user.ui_elements_hints_active
and tag: browser
"""

@mod.capture(rule="<user.letter> <user.letter>")
def ui_elements_hint_target(m) -> list[str]:
    return "".join(m.letter_list)

@mod.action_class
class Actions:
    def ui_elements_hint_action(action: str, ui_elements_hint_target: str = None):
        """Trigger ui_elements specific hint action"""
        if action == "click":
            if ui_elements_hint_target:
                trigger_hint_click(ui_elements_hint_target)
        elif action == "focus":
            if ui_elements_hint_target:
                trigger_hint_focus(ui_elements_hint_target)

    def ui_elements_key_action(action: str, key_down: bool = None):
        """Trigger ui_elements specific key action"""
        if action == "focus_next":
            focus_next.execute(key_down)
        elif action == "focus_previous":
            focus_previous.execute(key_down)
        elif action == "close":
            entity_manager.hide_all_trees()

    def ui_elements_scale_increase():
        """Increase UI scale by browser-like increments"""
        new_scale = entity_manager.increase_scale()
        show_scale_notification(new_scale)

    def ui_elements_scale_decrease():
        """Decrease UI scale by browser-like increments"""
        new_scale = entity_manager.decrease_scale()
        show_scale_notification(new_scale)

    def ui_elements_scale_reset():
        """Reset UI scale to default (1.0)"""
        new_scale = entity_manager.reset_scale()
        show_scale_notification(new_scale)
