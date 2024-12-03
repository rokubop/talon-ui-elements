from talon.experimental.textarea import DarkThemeLabels, TextArea
from dataclasses import dataclass
from .interfaces import NodeType, TreeType
from .store import store
from .utils import generate_hash

@dataclass
class ChangeEvent:
    value: str
    id: str = None
    previous_value: str = None

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

    def get_input_data(self, id: str):
        node = store.id_to_node.get(id)
        if node:
            return node.tree.meta_state.inputs.get(id)

    def create_input(self, node: NodeType):
        if not self.get_input_data(node.id):
            text_area_input = TextArea()
            text_area_input.theme = DarkThemeLabels(
                title_size=0,
                padding=0, # Keep this 0. Manage our own padding because this adds to the top hidden title as well
                text_size=node.properties.font_size,
                title_bg=node.properties.background_color,
                line_spacing=-8, # multiline text is too spaced out
                bg=node.properties.background_color,
                fg=node.properties.color
            )
            text_area_input.value = node.properties.value or ""

            def on_change(new_value):
                input_data = self.get_input_data(node.id)
                if not input_data or new_value == input_data.value:
                    return

                previous_value = input_data.value
                input_data.previous_value = input_data.value
                input_data.value = new_value
                if node.properties.on_change:
                    node.properties.on_change(
                        ChangeEvent(
                            value=new_value,
                            id=node.id,
                            previous_value=previous_value
                        )
                    )

            text_area_input.register("label", on_change)
            node.tree.meta_state.add_input(node.id, text_area_input, node.properties.value)

    def update_input_rect(self, id, rect):
        input_data = self.get_input_data(id)
        if input_data:
            input_data.input.rect = rect

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