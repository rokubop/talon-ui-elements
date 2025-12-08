from talon import Module, Context, actions

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
        from .src.core.store import store
        from .src.core.entity_manager import entity_manager
        # Browser-like zoom increments: 10% steps
        new_scale = round(store.scale + 0.1, 1)
        # Clamp between 0.5 and 3.0
        new_scale = max(0.5, min(3.0, new_scale))
        store.scale = new_scale
        # Re-render all active trees with new scale
        for tree in entity_manager.get_all_trees():
            tree.render()
        _show_scale_notification(new_scale)

    def ui_elements_scale_decrease():
        """Decrease UI scale by browser-like increments"""
        from .src.core.store import store
        from .src.core.entity_manager import entity_manager
        # Browser-like zoom increments: 10% steps
        new_scale = round(store.scale - 0.1, 1)
        # Clamp between 0.5 and 3.0
        new_scale = max(0.5, min(3.0, new_scale))
        store.scale = new_scale
        # Re-render all active trees with new scale
        for tree in entity_manager.get_all_trees():
            tree.render()
        _show_scale_notification(new_scale)

    def ui_elements_scale_reset():
        """Reset UI scale to default (1.0)"""
        from .src.core.store import store
        from .src.core.entity_manager import entity_manager
        store.scale = 1.0
        # Re-render all active trees with new scale
        for tree in entity_manager.get_all_trees():
            tree.render()
        _show_scale_notification(1.0)

def _show_scale_notification(scale: float):
    """Show a brief notification displaying the current scale percentage"""
    try:
        def scale_notification_ui():
            screen, div, text = actions.user.ui_elements(["screen", "div", "text"])
            percent = int(scale * 100)
            return screen(justify_content="center", align_items="center")[
                div(
                    padding=20,
                    background_color="#000000cc",
                    border_radius=8
                )[
                    text(f"{percent}%", font_size=32, color="ffffff", font_weight="bold")
                ]
            ]

        actions.user.ui_elements_show(scale_notification_ui, duration="1500ms")
    except (AttributeError, ImportError):
        # ui_elements not available, silently skip
        pass
