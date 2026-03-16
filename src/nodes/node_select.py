from talon import actions
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE, DEFAULT_INPUT_BACKGROUND_COLOR
from ..core.entity_manager import ChangeEvent
from ..interfaces import Padding
from ..properties import NodeSelectProperties


def _normalize_options(options):
    normalized = []
    for opt in options:
        if isinstance(opt, dict):
            normalized.append({
                "label": str(opt.get("label", opt.get("value", ""))),
                "value": opt.get("value", opt.get("label", "")),
            })
        else:
            normalized.append({"label": str(opt), "value": opt})
    return normalized


def _get_selected_label(normalized_options, value):
    for opt in normalized_options:
        if opt["value"] == value:
            return opt["label"]
    return None


class NodeSelect(NodeContainer):
    def __init__(self, properties: NodeSelectProperties = None):
        self._select_properties = properties
        self._normalized_options = _normalize_options(properties.options or [])

        properties.width = properties.width or round(properties.font_size * 15)

        # Save user padding for trigger/options, zero out container padding
        self._user_padding = Padding(properties.padding.top, properties.padding.right, properties.padding.bottom, properties.padding.left) if properties.padding else Padding(0, 0, 0, 0)
        self._has_user_padding = any(
            k in properties._explicitly_set
            for k in ('padding', 'padding_left', 'padding_right', 'padding_top', 'padding_bottom')
        )
        properties.padding = Padding(0, 0, 0, 0)

        if not properties.height:
            if self._has_user_padding:
                text_height = round(properties.font_size * 1.4)
                properties.height = text_height + self._user_padding.top + self._user_padding.bottom
            else:
                properties.height = round(properties.font_size * 2.2)
        properties.background_color = properties.background_color or DEFAULT_INPUT_BACKGROUND_COLOR
        properties.color = properties.color or "FFFFFF"

        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["select"],
            properties=properties
        )
        self.interactive = True

        # Use state for open/highlight - same pattern as NodeWindow
        div, button, text, icon, state = actions.user.ui_elements(["div", "button", "text", "icon", "state"])
        open_key = f"__select_open_{properties.id}"
        hl_key = f"__select_hl_{properties.id}"
        flip_key = f"__select_flip_{properties.id}"

        is_open, set_is_open = state.use(open_key, False)
        highlighted_index, set_highlighted_index = state.use(hl_key, -1)
        flip_up, set_flip_up = state.use(flip_key, False)

        self._is_open = is_open
        self._highlighted_index = highlighted_index
        self._set_is_open = set_is_open
        self._set_highlighted_index = set_highlighted_index
        self._flip_up = flip_up
        self._set_flip_up = set_flip_up

        self._build_children(div, button, text, icon)

    def _build_children(self, div, button, text, icon):
        props = self._select_properties

        selected_label = _get_selected_label(self._normalized_options, props.value)
        trigger_text = selected_label or props.placeholder or "Select..."
        trigger_color = props.color if selected_label else props.placeholder_color

        has_pad = self._has_user_padding
        pad = self._user_padding
        if has_pad:
            pad_left = pad.left
            pad_right = pad.right
            pad_top = pad.top
            pad_bottom = pad.bottom
        else:
            pad_left = 10
            pad_right = 6
            pad_top = 0
            pad_bottom = 0

        trigger = button(
            on_click=lambda e: self._toggle_open(),
            background_color=props.background_color,
            highlight_color="FFFFFF11",
            border_width=props.border.left if props.border else 1,
            border_color=props.border_color,
            border_radius=props.get_border_radius(),
            width=props.width,
            height=props.height,
            flex_direction="row",
            justify_content="space_between",
            align_items="center",
            padding_left=pad_left,
            padding_right=pad_right,
            padding_top=pad_top,
            padding_bottom=pad_bottom,
        )[
            text(trigger_text, color=trigger_color, font_size=props.font_size,
                 font_family=props.font_family),
            icon("chevron_down", color=trigger_color, size=round(props.font_size * 0.9),
                 stroke_width=2),
        ]
        trigger.interactive = False
        self.add_child(trigger)

        if self._is_open:
            # Dropdown container
            option_height = round(props.font_size * 2.2)
            dropdown_bg = props.background_color or DEFAULT_INPUT_BACKGROUND_COLOR
            dropdown_max_height = round(option_height * 6.5)

            dropdown_pos = {"bottom": props.height} if self._flip_up else {"top": props.height}

            dropdown = div(
                position="absolute",
                **dropdown_pos,
                left=0,
                width=props.width,
                max_height=dropdown_max_height,
                overflow_y="auto",
                background_color=dropdown_bg,
                border_width=1,
                border_color=props.border_color,
                border_radius=4,
                z_index=10,
            )

            for i, opt in enumerate(self._normalized_options):
                is_selected = opt["value"] == props.value
                is_highlighted = i == self._highlighted_index

                opt_bg = "FFFFFF22" if is_highlighted else ("FFFFFF11" if is_selected else "00000000")

                opt_value = opt["value"]
                option_btn = button(
                    on_click=lambda e, v=opt_value: self._select_option(v),
                    background_color=opt_bg,
                    highlight_color="FFFFFF22",
                    padding_top=pad_top if has_pad else 8,
                    padding_bottom=pad_bottom if has_pad else 8,
                    padding_left=pad_left if has_pad else 10,
                    padding_right=pad_right if has_pad else 10,
                    border_radius=0,
                )[
                    text(opt["label"],
                         color=props.color,
                         font_size=props.font_size,
                         font_family=props.font_family),
                ]
                option_btn.interactive = False
                dropdown.add_child(option_btn)

            self.add_child(dropdown)

    def _toggle_open(self):
        new_open = not self._is_open
        self._set_is_open(new_open)
        if new_open:
            # Determine if dropdown should flip upward
            flip_up = False
            if self.box_model and self.tree and self.tree.root_node and self.tree.root_node.box_model:
                option_height = round(self._select_properties.font_size * 2.2)
                dropdown_max_height = round(option_height * 6.5)
                trigger_bottom = self.box_model.border_rect.y + self.box_model.border_rect.height
                ui_bottom = self.tree.root_node.box_model.border_rect.y + self.tree.root_node.box_model.border_rect.height
                flip_up = (trigger_bottom + dropdown_max_height) > ui_bottom
            self._set_flip_up(flip_up)

            for i, opt in enumerate(self._normalized_options):
                if opt["value"] == self._select_properties.value:
                    self._set_highlighted_index(i)
                    return
            self._set_highlighted_index(0)
        else:
            self._set_highlighted_index(-1)

    def _close(self):
        self._set_is_open(False)
        self._set_highlighted_index(-1)

    def _select_option(self, value):
        previous_value = self._select_properties.value
        self._set_is_open(False)
        self._set_highlighted_index(-1)

        if self._select_properties.on_change and value != previous_value:
            change_event = ChangeEvent(
                value=value,
                id=self._select_properties.id,
                previous_value=previous_value,
            )
            self._select_properties.on_change(change_event)

    def on_key(self, key_string, is_down):
        if not is_down:
            return False

        num_options = len(self._normalized_options)
        if not num_options:
            return False

        # When closed: up/down/space/enter opens the dropdown
        if not self._is_open:
            if key_string in ("down", "up", "space", "enter", "return"):
                self._toggle_open()
                return True
            return False

        # When open
        if key_string == "down":
            new_idx = (self._highlighted_index + 1) % num_options
            self._set_highlighted_index(new_idx)
            return True
        elif key_string == "up":
            new_idx = (self._highlighted_index - 1) % num_options
            self._set_highlighted_index(new_idx)
            return True
        elif key_string == "home":
            self._set_highlighted_index(0)
            return True
        elif key_string == "end":
            self._set_highlighted_index(num_options - 1)
            return True
        elif key_string in ("enter", "return", "space"):
            if 0 <= self._highlighted_index < num_options:
                self._select_option(self._normalized_options[self._highlighted_index]["value"])
            return True
        elif key_string == "escape":
            self._close()
            return True

        return False

    @property
    def is_open(self):
        return self._is_open

    def destroy(self):
        self._set_is_open = None
        self._set_highlighted_index = None
        super().destroy()
