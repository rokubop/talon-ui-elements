from talon import actions
from .node_container import NodeContainer
from ..properties import Properties

class NodeTable(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(element_type="table", properties=properties)
        self.rows = []
        self.columns = []
        self.column_layout_children_nodes = []

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

        # print("len(self.rows)", len(self.rows))
        # print("len(self.rows[0])", len(self.rows[0]))
        # print("len(self.rows[1])", len(self.rows[1]))
        # print("len(self.rows[2])", len(self.rows[2]))
        # print("len(self.children_nodes)", len(self.children_nodes))

    def get_children_nodes(self):
        return self.column_layout_children_nodes

    def create_column_layout(self):
        if self.rows:
            columns = list(map(list, zip(*self.rows)))
        else:
            columns = []

        div = actions.user.ui_elements(["div"])
        self.column_layout_children_nodes = [
            div()[
                *column
            ]
            for column in columns
        ]

    def check_invalid_child(self, c):
        super().check_invalid_child(c)
        if c.element_type != "tr":
            raise ValueError(f"Invalid child element type '{c.element_type}' for table. Expected 'tr'.")

    def destroy(self):
        super().destroy()
        self.rows = []
        self.columns = []
        self.column_layout_children_nodes = []

class NodeTableRow(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(element_type="tr", properties=properties)

    def check_invalid_child(self, c):
        super().check_invalid_child(c)
        if c.element_type not in ["td", "th"]:
            raise ValueError(f"Invalid child element type '{c.element_type}' for tr. Expected 'td' or 'th'.")

class NodeTableHeader(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(element_type="th", properties=properties)

class NodeTableData(NodeContainer):
    def __init__(self, properties: Properties = None):
        super().__init__(element_type="td", properties=properties)
