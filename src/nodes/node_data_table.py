from dataclasses import dataclass, field
from typing import List, Set
from talon import actions
from .node_container import NodeContainer
from ..constants import ELEMENT_ENUM_TYPE
from ..properties import NodeDataTableProperties


@dataclass
class DataTableSelectEvent:
    row: dict
    index: int
    id: str = None


@dataclass
class DataTableChangeEvent:
    selected_rows: list
    id: str = None


def _row_id(row, row_key, index):
    if row_key and row_key in row:
        return row[row_key]
    return index


class NodeDataTable(NodeContainer):
    def __init__(self, properties: NodeDataTableProperties = None):
        self._dt_properties = properties

        properties.padding = properties.padding.__class__(0, 0, 0, 0)
        if not properties.overflow.is_boundary:
            from ..box_model import Overflow
            properties.overflow = Overflow(overflow="hidden")

        # Auto-fill parent when body_height is percentage so flex works on body
        if properties.body_height and isinstance(properties.body_height, str) and "%" in properties.body_height:
            if not properties.flex and not properties.height:
                properties.flex = 1

        super().__init__(
            element_type=ELEMENT_ENUM_TYPE["data_table"],
            properties=properties,
        )

        div, text, button, icon, input_text, state = actions.user.ui_elements(
            ["div", "text", "button", "icon", "input_text", "state"]
        )

        table_id = properties.id
        sort_key_k = f"__dt_sort_key_{table_id}"
        sort_dir_k = f"__dt_sort_dir_{table_id}"
        search_k = f"__dt_search_{table_id}"
        selected_k = f"__dt_selected_{table_id}"

        sort_key, set_sort_key = state.use(sort_key_k, properties.sort_key or None)
        sort_dir, set_sort_dir = state.use(sort_dir_k, properties.sort_direction or "asc")
        search_text, set_search_text = state.use(search_k, "")
        selected_set, set_selected_set = state.use(selected_k, set())

        self._sort_key = sort_key
        self._sort_dir = sort_dir
        self._search_text = search_text
        self._selected_set = selected_set
        self._set_sort_key = set_sort_key
        self._set_sort_dir = set_sort_dir
        self._set_search_text = set_search_text
        self._set_selected_set = set_selected_set

        self._build_children(div, text, button, icon, input_text)

    def _get_processed_data(self):
        props = self._dt_properties
        data = list(props.data or [])

        if self._search_text:
            query = self._search_text.lower()
            columns = props.columns or []
            keys = [col["key"] for col in columns]
            data = [
                row for row in data
                if any(query in str(row.get(k, "")).lower() for k in keys)
            ]

        if self._sort_key:
            reverse = self._sort_dir == "desc"
            if props.sort_fn:
                data = props.sort_fn(data, self._sort_key, self._sort_dir)
            else:
                col_sort = None
                for col in (props.columns or []):
                    if col["key"] == self._sort_key:
                        col_sort = col.get("sort")
                        break
                if col_sort:
                    data = sorted(data, key=lambda row: col_sort(row.get(self._sort_key, "")), reverse=reverse)
                else:
                    data = sorted(data, key=lambda row: str(row.get(self._sort_key, "")).lower(), reverse=reverse)

        return data

    def _on_header_click(self, col_key):
        if self._sort_key == col_key:
            self._set_sort_dir("desc" if self._sort_dir == "asc" else "asc")
        else:
            self._set_sort_key(col_key)
            self._set_sort_dir("asc")

    def _toggle_row_selected(self, rid, row, data):
        props = self._dt_properties
        new_set = set(self._selected_set)
        if rid in new_set:
            new_set.discard(rid)
        else:
            new_set.add(rid)
        self._set_selected_set(new_set)

        if props.on_change:
            row_key = props.row_key
            selected_rows = [
                r for i, r in enumerate(data)
                if _row_id(r, row_key, i) in new_set
            ]
            props.on_change(DataTableChangeEvent(
                selected_rows=selected_rows,
                id=props.id,
            ))

    def _toggle_all(self, data):
        props = self._dt_properties
        row_key = props.row_key
        all_rids = {_row_id(r, row_key, i) for i, r in enumerate(data)}

        if all_rids and all_rids.issubset(self._selected_set):
            new_set = self._selected_set - all_rids
        else:
            new_set = self._selected_set | all_rids
        self._set_selected_set(new_set)

        if props.on_change:
            selected_rows = [
                r for i, r in enumerate(data)
                if _row_id(r, row_key, i) in new_set
            ]
            props.on_change(DataTableChangeEvent(
                selected_rows=selected_rows,
                id=props.id,
            ))

    def _build_children(self, div, text, button, icon, input_text):
        props = self._dt_properties
        columns = props.columns or []
        data = self._get_processed_data()
        multi = props.multi_select
        row_key = props.row_key

        header_bg = props.header_background_color or "222222"
        row_bg = props.row_background_color or "00000000"
        stripe_bg = props.stripe_background_color or "FFFFFF08"
        border_color = props.border_color or "444444"
        header_color = props.header_color or "BBBBBB"
        selected_bg = props.selected_background_color or "67A4FF22"

        # Search input
        if props.searchable:
            search_row = div(
                padding=8,
                border_bottom=1,
                border_color=border_color,
            )[
                input_text(
                    id=f"__dt_search_input_{props.id}",
                    value=self._search_text,
                    placeholder=props.search_placeholder or "Search...",
                    on_change=lambda e: self._set_search_text(e.value),
                    background_color="333333",
                    border_radius=4,
                    border_width=1,
                    border_color=border_color,
                    font_size=int(props.font_size),
                    padding=6,
                    padding_left=10,
                    padding_right=10,
                ),
            ]
            self.add_child(search_row)

        # Header row
        header_cells = []

        if multi:
            all_rids = {_row_id(r, row_key, i) for i, r in enumerate(data)}
            all_checked = bool(all_rids) and all_rids.issubset(self._selected_set)
            check_icon = "check" if all_checked else "minus" if (self._selected_set & all_rids) else None

            checkbox_header = button(
                on_click=lambda e: self._toggle_all(data),
                highlight_color="FFFFFF11",
                width=44,
                align_items="center",
                justify_content="center",
                padding=8,
            )[
                icon(check_icon, size=14, color=header_color, stroke_width=2) if check_icon else
                div(width=14, height=14, border_width=1, border_color="666666", border_radius=2),
            ]
            checkbox_header.focusable = False
            header_cells.append(checkbox_header)

        for col in columns:
            is_sortable = col.get("sortable", False)
            col_key = col["key"]
            col_label = col.get("label", col_key)
            col_width = col.get("width")
            col_align = col.get("align", "left")

            cell_props = {
                "flex_direction": "row",
                "align_items": "center",
                "gap": 4,
                "padding": 8,
                "padding_left": 12,
                "padding_right": 12,
            }
            if col_width:
                cell_props["width"] = col_width
            else:
                cell_props["flex"] = 1

            if col_align == "center":
                cell_props["justify_content"] = "center"
            elif col_align == "right":
                cell_props["justify_content"] = "flex_end"

            if is_sortable:
                is_active_sort = self._sort_key == col_key
                sort_icon = None
                if is_active_sort:
                    sort_icon = icon(
                        "chevron_up" if self._sort_dir == "asc" else "chevron_down",
                        size=round(props.font_size * 0.75),
                        color=header_color,
                        stroke_width=2,
                    )

                cell = button(
                    on_click=lambda e, k=col_key: self._on_header_click(k),
                    highlight_color="FFFFFF11",
                    **cell_props,
                )[
                    text(col_label, font_size=props.font_size, font_weight="bold", color=header_color),
                    sort_icon,
                ]
                cell.focusable = False
            else:
                cell = div(**cell_props)[
                    text(col_label, font_size=props.font_size, font_weight="bold", color=header_color),
                ]

            header_cells.append(cell)

        header_row = div(
            flex_direction="row",
            background_color=header_bg,
            border_bottom=1,
            border_color=border_color,
        )[*header_cells]
        self.add_child(header_row)

        # Body (scrollable)
        body_props = {
            "overflow_y": "scroll",
        }
        if props.max_height:
            body_props["max_height"] = props.max_height
        if props.body_height:
            if props.body_height == "100%":
                body_props["flex"] = 1
            else:
                body_props["height"] = props.body_height

        body = div(**body_props)
        self._body_node = body
        self._key_to_row_node = {}

        if not data:
            empty_msg = div(
                padding=24,
                align_items="center",
                justify_content="center",
            )[
                text(
                    "No results" if self._search_text else "No data",
                    color="666666",
                    font_size=props.font_size,
                ),
            ]
            body.add_child(empty_msg)
        else:
            for i, row in enumerate(data):
                rid = _row_id(row, row_key, i)
                is_selected = rid in self._selected_set
                row_cells = []

                if multi:
                    check_cell = div(
                        width=44,
                        align_items="center",
                        justify_content="center",
                        padding=8,
                    )[
                        icon("check", size=14, color="#67A4FF", stroke_width=2) if is_selected else
                        div(width=14, height=14, border_width=1, border_color="666666", border_radius=2),
                    ]
                    row_cells.append(check_cell)

                for col in columns:
                    col_key = col["key"]
                    col_width = col.get("width")
                    col_align = col.get("align", "left")
                    render_fn = col.get("render")

                    raw_value = row.get(col_key, "")

                    cell_props = {
                        "padding": 8,
                        "padding_left": 12,
                        "padding_right": 12,
                    }
                    if col_width:
                        cell_props["width"] = col_width
                    else:
                        cell_props["flex"] = 1

                    if col_align == "center":
                        cell_props["align_items"] = "center"
                    elif col_align == "right":
                        cell_props["align_items"] = "flex_end"

                    if render_fn:
                        cell_content = render_fn(raw_value, row)
                        if isinstance(cell_content, str):
                            cell_content = text(cell_content, font_size=props.font_size, color=props.color)
                        cell = div(**cell_props)[cell_content]
                    else:
                        cell = div(**cell_props)[
                            text(str(raw_value), font_size=props.font_size, color=props.color),
                        ]
                    row_cells.append(cell)

                bg = selected_bg if is_selected else (stripe_bg if i % 2 == 1 else row_bg)

                row_hint_offset = props.row_hint_offset or (-5, -5)

                if multi:
                    row_div = button(
                        on_click=lambda e, r=row, rid_=rid: self._toggle_row_selected(rid_, r, data),
                        flex_direction="row",
                        background_color=bg,
                        highlight_color="FFFFFF11",
                        border_bottom=1,
                        border_color=border_color,
                        hint_offset=row_hint_offset,
                    )[*row_cells]
                    row_div.focusable = False
                elif props.on_select:
                    row_div = button(
                        on_click=lambda e, r=row, idx=i: props.on_select(
                            DataTableSelectEvent(row=r, index=idx, id=props.id)
                        ),
                        flex_direction="row",
                        background_color=bg,
                        highlight_color="FFFFFF11",
                        border_bottom=1,
                        border_color=border_color,
                        hint_offset=row_hint_offset,
                    )[*row_cells]
                    row_div.focusable = False
                else:
                    row_div = div(
                        flex_direction="row",
                        background_color=bg,
                        border_bottom=1,
                        border_color=border_color,
                    )[*row_cells]

                self._key_to_row_node[rid] = row_div
                body.add_child(row_div)

        self.add_child(body)

    def scroll_to_key(self, key):
        """Scroll so the row with the given key is visible.
        Sets scroll offset but does not queue a render - caller is responsible."""
        row_node = self._key_to_row_node.get(key)
        if not row_node:
            return False
        body = self._body_node
        if not row_node.box_model or not body or not body.box_model or not body.id:
            return False

        scroll_data = self.tree.meta_state.scrollable.get(body.id)
        if not scroll_data:
            return False

        # Use rendered_offset_y (the offset applied during last layout)
        # not offset_y (which may have changed by a pending scroll not yet rendered)
        child_y = row_node.box_model.margin_pos.y - body.box_model.padding_pos.y - scroll_data.rendered_offset_y
        child_height = row_node.box_model.margin_size.height

        visible_top = -scroll_data.rendered_offset_y
        visible_bottom = visible_top + scroll_data.view_height
        already_visible = child_y >= visible_top and child_y + child_height <= visible_bottom

        if not already_visible:
            new_offset_y = -child_y + 8
            min_offset_y = min(0, scroll_data.view_height - scroll_data.max_height)
            new_offset_y = max(min_offset_y, min(0, new_offset_y))

            if scroll_data.offset_y != new_offset_y:
                scroll_data.offset_y = new_offset_y
                scroll_data.target_offset_y = new_offset_y
                self.tree._scrollbar_show(body.id)
                return True
        return False

    def destroy(self):
        self._set_sort_key = None
        self._set_sort_dir = None
        self._set_search_text = None
        self._set_selected_set = None
        self._key_to_row_node = None
        self._body_node = None
        super().destroy()
