# from .interfaces import TreeManagerType, TreeType
# from .global_store import global_store
# from .tree import Tree

# class TreeManager(TreeManagerType):
#     def get_all_trees(self) -> list:
#         return global_store.trees

#     def get_all_nodes(self) -> list:
#         flattened = []

#         for tree in global_store.trees:
#             flattened.extend(self.get_node_tree_flattened(tree.root_node))

#         return flattened

#     def get_node_tree_flattened(self, node):
#         flattened = [node]

#         if node.children_nodes:
#             for child in node.children_nodes:
#                 flattened.extend(self.get_node_tree_flattened(child))

#         return flattened

#     def render(self, update_tree: callable):
#         hash = self.generate_hash_for_updater(update_tree)
#         tree = None
#         for t in global_store.trees:
#           if t.hashed_update_tree == hash:
#             tree = t
#             break

#         if not tree:
#             tree = Tree(update_tree, hash)
#             global_store.trees.append(tree)

#         tree.render()

#     def get_tree_with_hash(self, hash: str):
#         pass

#     def generate_hash_for_updater(self, update_tree: callable):
#         return "asdf"

#     def set_processing_tree(self, tree: TreeType):
#         pass

#     def destroy_all(self):
#         pass

#     def hide_all(self):
#         for tree in list(global_store.trees):
#             tree.destroy()
#             global_store.trees.remove(tree)

# tree_manager = TreeManager()