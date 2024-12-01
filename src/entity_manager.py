from .interfaces import NodeType, TreeType
from .store import store
from .utils import generate_hash

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

    def get_tree_with_hash_for_renderer(self, renderer: callable) -> TreeType:
        # to hash or not not to hash...
        # - pro: hash ensures if the user accidentally creates new references for their
        #   renderer every time (e.g. defined inside of a talon action), it will treat
        #   it as the same reference.
        # - pro: hash ensures during development and saving files which changes references
        #   of the renderer, it will treat it as the same reference.
        # - pro: if you accidentally get into a state where the UI is visible but you
        #   lost the reference to the renderer, you can still hide it.
        # - con: if two renderers are the same, it can't distinguish between them
        # - con: minimally slower to hash
        hash = generate_hash(renderer)
        tree = None
        for t in store.trees:
            if t.hashed_renderer == hash:
                tree = t
                break

        return {
            "tree": tree,
            "hash": hash
        }

    def hide_tree(self, renderer: callable):
        t = self.get_tree_with_hash_for_renderer(renderer)
        tree = t["tree"]
        if tree:
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

entity_manager = EntityManager()