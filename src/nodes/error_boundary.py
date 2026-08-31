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


# Fractions of the screen the default error card is allowed to occupy, and
# the absolute pixel ceilings it prefers when the screen is large.
ERROR_CARD_MAX_WIDTH_RATIO = 0.7
ERROR_CARD_MAX_HEIGHT_RATIO = 0.6
ERROR_CARD_MAX_WIDTH = 900
ERROR_CARD_MAX_HEIGHT = 560
ERROR_CARD_FALLBACK_SIZE = (800, 500)


def error_card_max_size():
    """Upper bound for the default error card, in pixels.

    A traceback is arbitrarily long and arbitrarily wide, and the card has no
    intrinsic size of its own, so without a cap it grows to the full content
    size and drags its container with it. Inside a `window` that pushes the
    title bar - and the close button on it - off screen, leaving no way to
    dismiss the error.
    """
    try:
        from ..utils import get_screen

        screen_index = None
        processing_tree = state_manager.get_processing_tree()
        if processing_tree and processing_tree.root_node:
            screen_index = getattr(processing_tree.root_node.properties, "screen", None)
        rect = get_screen(screen_index).rect
        return (
            min(ERROR_CARD_MAX_WIDTH, int(rect.width * ERROR_CARD_MAX_WIDTH_RATIO)),
            min(ERROR_CARD_MAX_HEIGHT, int(rect.height * ERROR_CARD_MAX_HEIGHT_RATIO)),
        )
    except Exception:
        # Screen lookup must never be the reason an error card fails to render.
        return ERROR_CARD_FALLBACK_SIZE


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

    max_width, max_height = error_card_max_size()

    card_defaults = {
        "flex": 1,
        "flex_direction": "column",
        "padding": 24,
        "gap": 14,
        "background_color": "1a0e0e",
        "overflow_y": "scroll",
        "max_width": max_width,
        "max_height": max_height,
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
