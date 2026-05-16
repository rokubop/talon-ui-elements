import traceback
import weakref

from ..core.state_manager import state_manager
from .component import Component


class ErrorBoundary(Component):
    """Component that renders a fallback error card instead of propagating
    exceptions raised by its renderer. The rest of the tree continues to
    render normally."""

    def __init__(
        self,
        renderer: callable,
        props: dict = None,
        *,
        label: str = None,
        fallback: callable = None,
        title_color: str = None,
        message_color: str = None,
        code_props: dict = None,
        **additional_props,
    ):
        super().__init__(renderer, props)
        self.label = label or getattr(renderer, "__qualname__", None) or self.name
        self.fallback = fallback
        self.title_color = title_color
        self.message_color = message_color
        self.code_props = code_props
        self.card_style = additional_props

    def initialize(self, node_index_path):
        try:
            return super().initialize(node_index_path)
        except Exception as e:
            state_manager.remove_processing_component(self)
            tb_str = traceback.format_exc()
            print(f"ui_elements: error_boundary '{self.label}' raised:\n{tb_str}")
            if self.fallback:
                error_node = self.fallback(type(e).__name__, str(e), tb_str)
            else:
                error_node = build_error_card(
                    self.label, type(e).__name__, str(e), tb_str,
                    title_color=self.title_color,
                    message_color=self.message_color,
                    code_props=self.code_props,
                    card_style=self.card_style,
                )
            self.id = (self.name, tuple(node_index_path))
            self._root_node = weakref.ref(error_node)
            self.replace_self_with_nodes(error_node)
            return error_node


def build_error_card(
    label: str,
    exc_kind: str,
    exc_msg: str,
    tb_str: str,
    *,
    title_color: str = None,
    message_color: str = None,
    code_props: dict = None,
    card_style: dict = None,
):
    # Lazy import to avoid circular dependency: elements.py imports Component
    # from this package, so importing div/text at module load would cycle.
    from ..elements import div, text
    from .code import code

    card_defaults = {
        "flex": 1,
        "flex_direction": "column",
        "padding": 24,
        "gap": 14,
        "background_color": "1a0e0e",
        "overflow_y": "scroll",
    }
    card_final = {**card_defaults, **(card_style or {})}

    code_defaults = {
        "language": "python",
        "font_size": 14,
        "copyable": True,
        "background_color": "120808",
        "border_radius": 6,
        "border_width": 1,
        "border_color": "aa3333",
        "padding": 12,
    }
    code_final = {**code_defaults, **(code_props or {})}

    return div(**card_final)[
        text(
            f"{label} render failed",
            font_size=20, font_weight="bold",
            color=title_color or "f08080",
        ),
        text(
            f"{exc_kind}: {exc_msg}",
            font_size=14, font_family="monospace",
            color=message_color or "ffaa66",
        ),
        text(
            "Full traceback:",
            font_size=14, color="888888", font_weight="bold",
        ),
        code(tb_str, **code_final),
    ]
