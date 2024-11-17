# from .global_store import global_store
# from .interfaces import EffectType, TreeType

# class StateManager:
#     def set_processing_tree(self, tree: TreeType):
#         global_store.processing_tree = tree

#     def get_processing_tree(self) -> TreeType:
#         return global_store.processing_tree

#     def get_active_component_node(self):
#         return global_store.active_component

#     def set_active_component_node(self, component):
#         global_store.active_component = component

#     # def get_state_value(self, key):
#     #     return global_store.reactive_global_state.get(key)

#     # def set_state_value(self, key, value):
#     #     global_store.reactive_global_state[key] = value

#     def register_effect(self, tree, callback, dependencies):
#         effect: EffectType = {
#             'name': callback.__name__,
#             'callback': callback,
#             'dependencies': dependencies,
#             'tree': tree
#         }
#         global_store.staged_effects.append(effect)

#     # def run_all_effects(self):
#     #     for effect in global_store.effects:
#     #         effect['callback']()

#     # def run_effects_for_state(self, state_name):
#     #     for effect in self.effects_by_state[state_name]:
#     #         current_deps_values = [self.get_state_value(dep) for dep in effect['deps']]

#     #         if current_deps_values != effect['prev_deps']:
#     #             effect['callback']()
#     #             effect['prev_deps'] = current_deps_values

# state_manager = StateManager()