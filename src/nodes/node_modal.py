import traceback
from talon import actions
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..properties import NodeModalProperties


# Props that shape the user's content area (inner body div). Everything else
# is treated as panel-level (visual chrome, sizing, cascade-able color/font).
# Putting padding/gap/flex on the inner body keeps the title bar flush against
# the panel edges instead of being indented by the user's content padding.
_BODY_PROPS = {
    "padding", "padding_top", "padding_right", "padding_bottom", "padding_left",
    "padding_x", "padding_y",
    "gap",
    "flex_direction", "justify_content", "align_items",
    "flex_wrap",
}


class NodeModal(NodeContainer):
    """Full-viewport overlay layer. When `open=True` adds a backdrop and a
    centered content panel; when `open=False` collapses to a zero-footprint
    placeholder so reactive open=True re-renders work without leaving any
    invisible click target behind."""

    def __init__(self, modal_properties: NodeModalProperties, content_properties: dict):
        is_open = bool(modal_properties.open)

        if not is_open:
            # Closed: don't take up the viewport, don't hit-test, don't render.
            modal_properties.position = "static"
            modal_properties.width = 0
            modal_properties.height = 0
            super().__init__(
                element_type=ELEMENT_ENUM_TYPE["modal"],
                properties=modal_properties,
            )
            self.body = None
            return

        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["modal"],
            properties=modal_properties,
        )

        div, button, text, icon = actions.user.ui_elements(
            ["div", "button", "text", "icon"]
        )

        on_close_cb = modal_properties.on_close
        modal_z = modal_properties.z_index or 0

        def fire_close(*_):
            if on_close_cb:
                try:
                    on_close_cb()
                except Exception:
                    traceback.print_exc()

        if modal_properties.backdrop:
            # Use "fixed" (root-relative) rather than "absolute" (modal-relative)
            # so nonlayout_flow can lay it out without depending on the modal's
            # box_model already being computed (it's also a fixed node).
            backdrop_props = {
                "position": "fixed",
                "top": 0,
                "left": 0,
                "width": "100%",
                "height": "100%",
                "background_color": modal_properties.backdrop_color,
                "highlight_color": "00000000",
            }
            if modal_properties.backdrop_click_close and on_close_cb:
                backdrop_props["on_click"] = fire_close
                backdrop = button(**backdrop_props)
            else:
                backdrop = div(**backdrop_props)
            self.add_child(backdrop)

        panel_props = {k: v for k, v in content_properties.items() if k not in _BODY_PROPS}
        body_props = {k: v for k, v in content_properties.items() if k in _BODY_PROPS}

        # The +1 explicit z_index beats the backdrop's higher z_subindex (from
        # being a fixed-position node) so the panel always renders on top.
        panel = div(**panel_props, z_index=modal_z + 1)

        if modal_properties.show_title_bar:
            title_bar_children = [
                text(modal_properties.title or "", padding=8, padding_left=10),
            ]
            if on_close_cb:
                title_bar_children.append(
                    button(
                        on_click=fire_close,
                        padding=8,
                        padding_left=12,
                        padding_right=12,
                    )[icon("close", stroke_width=1, size=20)]
                )
            panel.add_child(
                div(
                    background_color="272727",
                    flex_direction="row",
                    justify_content="space_between",
                    align_items="center",
                )[title_bar_children]
            )

        self.body = div(**body_props)
        panel.add_child(self.body)
        self.add_child(panel)

    def __getitem__(self, children=None):
        if self.body is None:
            return self
        if children is None:
            children = []
        if not isinstance(children, list):
            children = [children]
        for child in children:
            self.body.add_child(child)
        return self
