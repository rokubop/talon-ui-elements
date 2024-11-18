from .interfaces import NodeType, TreeType, EffectType
from .store import store

class EntityManager:
    def add_tree(self, tree: TreeType):
        store.trees.append(tree)

    def get_all_trees(self) -> TreeType:
        return store.trees

    def get_all_nodes(self) -> NodeType:
        flattened = []

        for tree in store.trees:
            flattened.extend(self.get_node_tree_flattened(tree.root_node))

        return flattened

    def hide_all_trees(self):
        for tree in list(store.trees):
            tree.destroy()
            store.trees.remove(tree)

    def get_node_tree_flattened(self, node) -> list[NodeType]:
        flattened = [node]

        if node.children_nodes:
            for child in node.children_nodes:
                flattened.extend(self.get_node_tree_flattened(child))

        return flattened

    def get_tree_with_hash(self, hash: str):
        pass

    def set_processing_tree(self, tree: TreeType):
        pass

    def destroy_all(self):
        pass

    def get_button_nodes(self, root_node = None):
        if root_node:
            return root_node.node_store.buttons
        else:
            buttons = []

            for node in store.root_nodes:
                buttons.extend(node.node_store.buttons)

    def add_button_node(self, node):
        pass
        # print(node)
        # print(node.root_node)
        # print(node.root_node.node_store)
        # print(node.root_node.node_store.buttons)
        # node.root_node.node_store.buttons.append(node)

    # def link_root_node_to_state(self, node, root_node):
    #     if node.state_key:
    #         if node.state_key not in store.reactive_global_state:
    #             store.reactive_global_state[node.state_key] = []

    #         store.reactive_global_state[node.state_key].append(root_node

    # def set_text(self, node_id, text):
    #     node = store.get_node(node_id)  # Retrieve node from the store by ID
    #     if node:
    #         node.root_node.set_text(text)  # Assuming nodes have a set_text method
    #     else:
    #         print(f"Node with ID '{node_id}' not found.")

# class StateManager:
#     def set_processing_tree(self, tree: TreeType):
#         store.processing_tree = tree

#     def get_processing_tree(self) -> TreeType:
#         return store.processing_tree

#     def get_active_component_node(self):
#         return store.active_component

#     def set_active_component_node(self, component):
#         store.active_component = component

#     # def get_state_value(self, key):
#     #     return store.reactive_global_state.get(key)

#     # def set_state_value(self, key, value):
#     #     store.reactive_global_state[key] = value

#     def register_effect(self, tree, callback, dependencies):
#         effect: EffectType = {
#             'name': callback.__name__,
#             'callback': callback,
#             'dependencies': dependencies,
#             'tree': tree
#         }
#         store.staged_effects.append(effect)

#     # def run_all_effects(self):
#     #     for effect in store.effects:
#     #         effect['callback']()

#     # def run_effects_for_state(self, state_name):
#     #     for effect in self.effects_by_state[state_name]:
#     #         current_deps_values = [self.get_state_value(dep) for dep in effect['deps']]

#     #         if current_deps_values != effect['prev_deps']:
#     #             effect['callback']()
#     #             effect['prev_deps'] = current_deps_values

class TreeManager():
    def add_tree(self, tree: TreeType):
        store.trees.append(tree)

entity_manager = EntityManager()
# state_manager = StateManager()