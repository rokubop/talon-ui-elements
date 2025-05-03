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
        for child in self.children_nodes:
            if child.element_type == "tr":
                row = []
                for cell in child.children_nodes:
                    if cell.element_type in ["td", "th"]:
                        row.append(cell)
                self.rows.append(row)
        self.create_column_layout()

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
