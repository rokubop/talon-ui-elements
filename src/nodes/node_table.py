import weakref
from talon import actions
from talon.skia.canvas import Canvas as SkiaCanvas
from typing import Optional
from .node_container import NodeContainer
from ..box_model import BoxModelV2
from ..interfaces import Size2d
from ..properties import Properties

class NodeTable(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(element_type="table", properties=properties)
        self.rows = []
        self.columns = []
        self.column_layout_children_nodes = []
        self.row_heights = []
        self.col_widths = []

    def __getitem__(self, children_nodes=None):
        super().__getitem__(children_nodes)
        self._process_children()
        return self

    def _process_children(self):
        """Process child nodes to extract rows and their contents."""
        self.rows = []
        for tr_node in self.children_nodes:
            if tr_node.element_type == "tr":
                row = []
                for td_node in tr_node.children_nodes:
                    if td_node.element_type in ["td", "th"]:
                        td_node.properties.inherit_explicit_properties(tr_node.properties)
                        row.append(td_node)
                self.rows.append(row)

        # Check if rows have different lengths
        if len(set(len(row) for row in self.rows)) > 1:
            self.add_missing_cells()

        for r, row in enumerate(self.rows):
            for i, td_node in enumerate(row):
                td_node._table_node = weakref.ref(self)
                td_node.row_index = r
                td_node.column_index = i

        self.create_column_layout()

    def add_missing_cells(self):
        """Add missing cells to the rows to make them uniform."""
        total_cols = max(len(row) for row in self.rows)

        for row, tr_node in zip(self.rows, self.children_nodes):
            if len(row) < total_cols:
                # Add missing cells to the current row
                missing_cells = total_cols - len(row)
                for _ in range(missing_cells):
                    empty_cell = actions.user.ui_elements("td")()
                    empty_cell.properties.inherit_explicit_properties(tr_node.properties)
                    tr_node.add_child(empty_cell)
                    row.append(empty_cell)

    def get_children_nodes(self):
        return self.column_layout_children_nodes

    def create_column_layout(self):
        if self.rows:
            self.columns = list(map(list, zip(*self.rows)))
        else:
            self.columns = []

        div = actions.user.ui_elements(["div"])
        self.column_layout_children_nodes = [
            div(flex=1)[
                *column
            ]
            for column in self.columns
        ]

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        self.row_heights = [0] * len(self.rows) if self.rows else []
        col_count = max(len(row) for row in self.rows) if self.rows else 0
        self.col_widths = [0] * col_count if col_count else []

        measured_sizes = {}

        for row_index, row in enumerate(self.rows):
            for col_index, td_node in enumerate(row):
                if td_node not in measured_sizes:
                    measured_sizes[td_node] = td_node.v2_measure_children_intrinsic_size(c)

                size = measured_sizes[td_node]
                content_width = size.width
                content_height = size.height

                # Factor in explicit width/min_width (these are border-level sizes)
                props = td_node.properties
                explicit_width = props.width or props.min_width
                if explicit_width and isinstance(explicit_width, (int, float)):
                    pad_h = props.padding.left + props.padding.right
                    bdr_h = props.border.left + props.border.right
                    content_from_explicit = explicit_width - pad_h - bdr_h
                    content_width = max(content_width, content_from_explicit)

                explicit_height = props.height or props.min_height
                if explicit_height and isinstance(explicit_height, (int, float)):
                    pad_v = props.padding.top + props.padding.bottom
                    bdr_v = props.border.top + props.border.bottom
                    content_from_explicit = explicit_height - pad_v - bdr_v
                    content_height = max(content_height, content_from_explicit)

                self.col_widths[col_index] = max(self.col_widths[col_index], content_width)
                self.row_heights[row_index] = max(self.row_heights[row_index], content_height)

        # Factor in explicit tr height
        for row_index, tr_node in enumerate(self.children_nodes):
            if tr_node.element_type == "tr":
                tr_height = tr_node.properties.height
                if tr_height and isinstance(tr_height, (int, float)):
                    pad_v = tr_node.properties.padding.top + tr_node.properties.padding.bottom
                    bdr_v = tr_node.properties.border.top + tr_node.properties.border.bottom
                    content_from_tr = tr_height - pad_v - bdr_v
                    self.row_heights[row_index] = max(self.row_heights[row_index], content_from_tr)

        return super().v2_measure_intrinsic_size(c)

    def check_invalid_child(self, c):
        super().check_invalid_child(c)
        if c.element_type != "tr":
            raise ValueError(f"Invalid child element type '{c.element_type}' for table. Expected 'tr'.")

    def destroy(self):
        self.rows.clear()
        self.columns.clear()
        self.column_layout_children_nodes.clear()
        super().destroy()

class NodeTableRow(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(element_type="tr", properties=properties)

    def check_invalid_child(self, c):
        super().check_invalid_child(c)
        if c.element_type not in ["td", "th"]:
            raise ValueError(f"Invalid child element type '{c.element_type}' for tr. Expected 'td' or 'th'.")

class NodeTableHeader(NodeContainer):
    def __init__(self, properties: Properties = None):
        self._table_node: Optional[weakref.ReferenceType[NodeTable]] = None
        self.column_index = None
        self.row_index = None
        super().__init__(element_type="th", properties=properties)

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        table_node = self._table_node()
        width = table_node.col_widths[self.column_index] if table_node else 0
        height = table_node.row_heights[self.row_index] if table_node else 0

        self.box_model = BoxModelV2(
            self.properties,
            Size2d(width, height),
            self.clip_nodes,
            self.relative_positional_node
        )

        return self.box_model.intrinsic_margin_size_with_bounding_constraints

    def destroy(self):
        if self._table_node is not None:
            self._table_node = None
        super().destroy()

class NodeTableData(NodeContainer):
    def __init__(self, properties: Properties = None):
        self._table_node: Optional[weakref.ReferenceType[NodeTable]] = None
        self.column_index = None
        self.row_index = None
        super().__init__(element_type="td", properties=properties)

    def v2_measure_intrinsic_size(self, c: SkiaCanvas):
        table_node = self._table_node()
        width = table_node.col_widths[self.column_index] if table_node else 0
        height = table_node.row_heights[self.row_index] if table_node else 0

        self.box_model = BoxModelV2(
            self.properties,
            Size2d(width, height),
            self.clip_nodes,
            self.relative_positional_node
        )

        return self.box_model.intrinsic_margin_size_with_bounding_constraints

    def destroy(self):
        if self._table_node is not None:
            self._table_node = None
        super().destroy()
