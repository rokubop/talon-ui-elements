from talon.experimental.textarea import DarkThemeLabels, TextArea
from dataclasses import dataclass
from talon.skia.typeface import Typeface
from typing import Union
from .interfaces import NodeType, TreeType
from .store import store
from .utils import generate_hash
import time

@dataclass
class ChangeEvent:
    value: str
    id: str = None
    previous_value: str = None

class EntityManager:
    def add_tree(self, tree: TreeType):
        # print("add_tree", time.perf_counter())
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
            args = {
                "title_size": 0,
                "padding": 0,
                "text_size": node.properties.font_size,
                "title_bg": node.properties.background_color,
                "line_spacing": -8,
                "bg": node.properties.background_color,
                "fg": node.properties.color,
            }
            if node.properties.font_family:
                args["typeface"] = Typeface.from_name(node.properties.font_family)

            text_area_input.theme = DarkThemeLabels(**args)
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

            node.tree.meta_state.add_input(node.id, text_area_input, node.properties.value, on_change)

    def update_input_rect(self, id, rect, top_offset=0):
        input_data = self.get_input_data(id)
        if input_data:
            input_data.input.rect = rect
            input_data.input.scroll = top_offset

    def does_tree_exist(self, renderer: callable) -> bool:
        """Check if a tree exists based on the renderer"""
        hash = generate_hash(renderer)
        for t in store.trees:
            if t.hashed_renderer == hash:
                return True
        return False

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

    def hide_tree(self, renderer: Union[str, callable]):
        """Hide based on the renderer or an id on the root node (screen)"""
        if isinstance(renderer, str):
            for tree in store.trees:
                if tree.root_node.id == renderer:
                    tree.destroy()
                    store.trees.remove(tree)
                    break
        else:
            t = self.get_tree_with_hash_for_renderer(renderer)
            tree = t["tree"]
            if tree:
                # print("hide_tree tree.destroy", time.perf_counter())
                tree.destroy()
                # print("hide_tree store.trees.remove", time.perf_counter())
                store.trees.remove(tree)
            # else:
            #     print("Tree not found for renderer hash", t["hash"])

        if not store.trees:
            # print("hide_tree store.clear", time.perf_counter())
            store.clear()

    def hide_all_trees(self):
        for tree in list(store.trees):
            # print("destroying tree", tree)
            # print(f"hide_all_trees there are {len(store.trees)} trees to hide")
            # print(f"hide_all_trees current tree is {tree.hashed_renderer}")
            # print("hide_all_trees tree.destroy", time.perf_counter())
            tree.destroy()
            # print("hide_all_trees store.trees.remove", time.perf_counter())
            store.trees.remove(tree)
        if not store.trees:
            # print("clearing store")
            # print("hide_all_trees store.clear", time.perf_counter())
            store.clear()
        # else:
        #     print("wtf another tree exists")

    def get_node_tree_flattened(self, node) -> list[NodeType]:
        flattened = [node]

        if node.children_nodes:
            for child in node.children_nodes:
                flattened.extend(self.get_node_tree_flattened(child))

        return flattened

    def debug(self):
        print("store.trees", store.trees)
        print("store.processing_tree", store.processing_tree)
        print("store.processing_states", store.processing_states)
        print("store.root_nodes", store.root_nodes)
        print("store.id_to_node", store.id_to_node)
        print("store.id_to_hint", store.id_to_hint)
        print("store.reactive_state", store.reactive_state)
        print("store.staged_effects", store.staged_effects)
        print("store.mouse_state", store.mouse_state)

        for index, tree in enumerate(store.trees):
            print(f"\n------------\nTree #{index}")
            print("tree.meta_state._buttons", tree.meta_state._buttons)
            print("tree.meta_state._highlighted", tree.meta_state._highlighted)
            print("tree.meta_state._id_to_node", tree.meta_state._id_to_node)
            print("tree.meta_state._inputs", tree.meta_state._inputs)
            print("tree.meta_state._scroll_regions", tree.meta_state._scroll_regions)
            print("tree.meta_state._style_mutations", tree.meta_state._style_mutations)
            print("tree.meta_state._text_mutations", tree.meta_state._text_mutations)
            print("tree.meta_state.ref_property_overrides", tree.meta_state.ref_property_overrides)
            print("tree.meta_state.focused_id", tree.meta_state.focused_id)
            print("tree.meta_state.unhighlight_jobs", tree.meta_state.unhighlight_jobs)

entity_manager = EntityManager()