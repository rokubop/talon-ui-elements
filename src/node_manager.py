from .global_store import global_store
from .interfaces import NodeType
# from .nodes.node import Node

class NodeManager:
    def get_all_nodes(self):
        flattened = []

        for node in global_store.root_nodes:
            flattened.extend(self.get_node_tree_flattened(node))

        return flattened

    def get_root_nodes(self):
        return global_store.root_nodes

    def get_button_nodes(self, root_node = None):
        if root_node:
            return root_node.node_store.buttons
        else:
            buttons = []

            for node in global_store.root_nodes:
                buttons.extend(node.node_store.buttons)

    def get_node_tree_flattened(self, node):
        flattened = [node]

        if node.children_nodes:
            for child in node.children_nodes:
                flattened.extend(self.get_node_tree_flattened(child))

        return flattened

    def add_button_node(self, node):
        pass
        # print(node)
        # print(node.root_node)
        # print(node.root_node.node_store)
        # print(node.root_node.node_store.buttons)
        # node.root_node.node_store.buttons.append(node)

    def add_root_node(self, node):
        global_store.root_nodes.append(node)

    def remove_node(self, node):
        if node.node_type == 'root':
            global_store.root_nodes.remove(node)

    def hide_all(self):
        for node in list(global_store.root_nodes):
            node.hide()

        global_store.root_nodes.clear()

    # def link_root_node_to_state(self, node, root_node):
    #     if node.state_key:
    #         if node.state_key not in global_store.reactive_global_state:
    #             global_store.reactive_global_state[node.state_key] = []

    #         global_store.reactive_global_state[node.state_key].append(root_node

    def init_node_hierarchy(self, root_node: NodeType, current_node: NodeType, depth = 0):
        for child_node in current_node.children_nodes:
            child_node.root_node = root_node
            child_node.depth = depth + 1

            if child_node.element_type == 'button':
                root_node.node_store.buttons.append(child_node)
            elif child_node.element_type == 'text' and child_node.id:
                root_node.node_store.dynamic_text.append(child_node)
            elif child_node.element_type == 'component':
                root_node.node_store.components.append(child_node)

                for effect in list(global_store.staged_effects):
                    if effect['component_node'] == child_node:
                        root_node.state_store.add_effect(effect)
                        global_store.staged_effects.remove(effect)

            self.init_node_hierarchy(root_node, child_node, depth + 1)

    # def set_text(self, node_id, text):
    #     node = global_store.get_node(node_id)  # Retrieve node from the global_store by ID
    #     if node:
    #         node.root_node.set_text(text)  # Assuming nodes have a set_text method
    #     else:
    #         print(f"Node with ID '{node_id}' not found.")

node_manager = NodeManager()