from .interfaces import NodeType, TreeType
from .store import store

class EntityManager:
    def add_tree(self, tree: TreeType):
        store.trees.append(tree)

    def synchronize_global_ids(self):
        store.synchronize_ids()

    def get_node(self, id: str) -> NodeType:
        return store.id_to_node.get(id)

    def get_all_trees(self) -> list[TreeType]:
        return store.trees

    def get_all_nodes(self) -> list[NodeType]:
        flattened = []

        for tree in store.trees:
            flattened.extend(self.get_node_tree_flattened(tree.root_node))

        return flattened

    def hide_tree(self, renderer: callable):
        for tree in store.trees:
            if tree.renderer == renderer:
                tree.destroy()
                store.trees.remove(tree)

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

entity_manager = EntityManager()