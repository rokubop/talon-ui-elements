from talon import Context, cron
from typing import Callable, Optional
from ..interfaces import (
    Effect,
    NodeType,
    ReactiveStateType,
    StyleType,
    TreeType,
)
from .store import store
import gc

class StateCoordinator:
    PHASE_FREE = "free"
    PHASE_BATCH = "batch"
    PHASE_REQUEST_RENDER = "request_render"
    PHASE_RENDERING = "rendering"

    def __init__(self):
        self.locked = False
        self.phase = self.PHASE_FREE
        self.current_state_keys = set()
        self.next_state_keys = set()
        self.pending_tree_renders = set()
        self.batch_job = None

    def finish_cycle(self, tree: TreeType):
        if self.locked:
            self.current_state_keys.clear()
            self.locked = False
            self.phase = self.PHASE_FREE

            if self.next_state_keys:
                self.current_state_keys.update(self.next_state_keys)
                self.next_state_keys.clear()

            if self.current_state_keys:
                for key in self.current_state_keys:
                    self.request_state_change(key)

    def flush_state(self):
        for key in self.current_state_keys:
            store.reactive_state[key].activate_next_state_value()

    def on_tree_render_start(self):
        def on_start(tree: TreeType, *args):
            if not self.locked:
                self.locked = True
                self.phase = self.PHASE_RENDERING
                self.flush_state()

            tree.render(*args)

        return on_start

    def on_tree_render_end(self):
        def on_end(e):
            self.pending_tree_renders.remove(e.tree.guid)

            if not self.pending_tree_renders:
                self.finish_cycle(e.tree)

        return on_end

    def request_tree_renders(self):
        if self.locked:
            return

        if self.phase == self.PHASE_BATCH:
            self.phase = self.PHASE_REQUEST_RENDER
            if self.batch_job:
                cron.cancel(self.batch_job)
            self.batch_job = None

        if self.phase == self.PHASE_REQUEST_RENDER:
            trees = state_manager.get_trees_for_state_keys(self.current_state_keys)

            for tree in trees:
                if tree.guid not in self.pending_tree_renders:
                    self.pending_tree_renders.add(tree.guid)
                    tree.render_manager.schedule_state_change(
                        on_start=self.on_tree_render_start(),
                        on_end=self.on_tree_render_end()
                    )

            if not self.pending_tree_renders:
                self.finish_cycle(None)

    def request_state_change(self, state_key: str):
        if self.locked:
            self.next_state_keys.add(state_key)
            return

        self.current_state_keys.add(state_key)

        if self.phase == self.PHASE_FREE:
            self.phase = self.PHASE_BATCH

        if self.phase == self.PHASE_BATCH:
            if self.batch_job:
                cron.cancel(self.batch_job)
            self.batch_job = cron.after("1ms", self.request_tree_renders)

    def reset(self):
        self.locked = False
        self.phase = self.PHASE_FREE
        self.current_state_keys.clear()
        self.next_state_keys.clear()
        self.pending_tree_renders.clear()
        if self.batch_job:
            cron.cancel(self.batch_job)
            self.batch_job = None

state_coordinator = StateCoordinator()

class ReactiveState(ReactiveStateType):
    def __init__(self):
        self._initial_value = None
        self._value = None
        self.next_state_queue = []

    @property
    def initial_value(self):
        return self._initial_value

    @property
    def value(self):
        return self._value

    def resolve_value(self, value_or_callable):
        if callable(value_or_callable):
            return value_or_callable(self._value)
        return value_or_callable

    def set_initial_value(self, value):
        if self._initial_value is None:
            self._initial_value = value
            self._value = value

    def set_value(self, value_or_callable):
        self.next_state_queue.append(value_or_callable)

    def activate_next_state_value(self):
        for new_state in self.next_state_queue:
            self._value = self.resolve_value(new_state)

        self.next_state_queue.clear()

class DeprecatedLifecycleEvent:
    def __init__(self, event_type: str, tree: TreeType):
        self.type = event_type
        self.builder_id = getattr(tree.root_node, 'id') or tree.root_node.guid
        self.children_ids = tree.meta_state.id_to_node.keys()

_deprecated_event_subscribers = []

class StateManager:
    def __init__(self):
        self.debounce_render_job = None
        self.ctx = Context()

    def get_hovered_id(self):
        return store.mouse_state['hovered_id']

    def set_hovered_id(self, id):
        store.mouse_state['hovered_id'] = id

    def get_mousedown_start_id(self):
        return store.mouse_state['mousedown_start_id']

    def get_drag_relative_offset(self):
        return store.mouse_state['drag_relative_offset']

    def get_mousedown_start_pos(self):
        return store.mouse_state['mousedown_start_pos']

    def get_mousedown_start_offset(self):
        return store.mouse_state['mousedown_start_offset']

    def is_drag_active(self):
        return store.mouse_state['is_drag_active']

    def set_mousedown_start_id(self, id):
        store.mouse_state['mousedown_start_id'] = id

    def set_mousedown_start_pos(self, gpos):
        store.mouse_state['mousedown_start_pos'] = gpos

    def set_mousedown_start_offset(self, offset):
        store.mouse_state['mousedown_start_offset'] = offset

    def set_drag_relative_offset(self, offset):
        store.mouse_state['drag_relative_offset'] = offset

    def set_drag_active(self, is_active):
        store.mouse_state['is_drag_active'] = is_active

    def set_processing_tree(self, tree: TreeType):
        store.processing_tree = tree

    def get_processing_style(self) -> StyleType:
        context = state_manager.get_processing_component() \
            or state_manager.get_processing_tree()
        if context and getattr(context, 'style', None):
            return context.style

    def get_processing_tree(self) -> TreeType:
        return store.processing_tree

    def set_processing_component(self, component):
        store.processing_components.append(component)

    def get_processing_components(self):
        return store.processing_components

    def get_processing_component(self):
        if store.processing_components:
            return store.processing_components[-1]
        return None

    def get_processing_states(self):
        return state_coordinator.current_state_keys

    def remove_processing_component(self, component):
        store.processing_components.remove(component)

    def get_trees_for_state(self, state_key):
        try:
            return [tree for tree in store.trees if state_key in tree.meta_state.state_keys]
        except Exception as e:
            return []

    def get_trees_for_state_keys(self, state_keys):
        try:
            return [tree for tree in store.trees if \
                any(key in state_keys for key in tree.meta_state.states)
            ]
        except Exception as e:
            return []

    def init_states(self, states):
        if states is not None:
            for key, value in states.items():
                self.init_state(key, value)

    def init_state(self, key, initial_value):
        if type(key) is not str:
            raise ValueError("state must include a string key like this: state.use('my_state', initial_value) or state.get('my_state')")

        if key not in store.reactive_state:
            store.reactive_state[key] = ReactiveState()

        store.reactive_state[key].set_initial_value(initial_value)

    # def rerender_state(self):
    #     for state in store.reactive_state.values():
    #         state.activate_next_state_value()

    #     for tree in store.trees:
    #         tree.processing_states.update(store.processing_states)
    #         # tree.queue_render(RenderTask(
    #         #     cause=RenderCause.STATE_CHANGE,
    #         #     before_render=lambda: tree.processing_states.clear()
    #         #     after_render=lambda: tree.processing_states.clear()
    #         # )),
    #         tree.render_manager.render_state_change()

    #     # TODO: queue into render manager
    #     cron.after("30ms", store.processing_states.clear)
    #     # store.processing_states.clear()
    #     self.debounce_render_job = None

    def get_state_value(self, key):
        if key in store.reactive_state:
            return store.reactive_state[key].value
        return None

    def get_all_states(self):
        return {key: store.reactive_state[key].value for key in store.reactive_state.keys()}

    def set_state_value(self, key, new_value):
        if key in store.reactive_state:
            if store.reactive_state[key].value == store.reactive_state[key].resolve_value(new_value):
                return

        self.init_state(key, new_value)
        store.reactive_state[key].set_value(new_value)
        store.processing_states.add(key)
        state_coordinator.request_state_change(key)

    def get_text_mutation(self, id):
        node = store.id_to_node.get(id)
        if node:
            return node.tree.meta_state.get_text_mutation(id)
        return ""

    def set_text_mutation(self, id, text_or_callable):
        node = store.id_to_node.get(id)
        if node:
            if isinstance(text_or_callable, Callable):
                node.tree.meta_state.text_mutations[id] = text_or_callable(node.tree.meta_state.text_mutations.get(id, ""))
            else:
                node.tree.meta_state.text_mutations[id] = text_or_callable
            node.tree.render_manager.render_text_mutation()
        else:
            print(f"Node with ID '{id}' not found.")

    def use_text_mutation(self, node: NodeType):
        if node.tree.meta_state.text_mutations.get(node.id):
            return node.tree.meta_state.text_mutations[node.id]
        node.tree.meta_state.text_mutations[id] = node.text
        return node.text

    def get_input_value(self, id):
        node = store.id_to_node.get(id)
        if node:
            input_data = node.tree.meta_state.inputs.get(id)
            if input_data:
                return input_data.value
        return ""

    def is_focused(self, id):
        return store.focused_id == id

    def is_focus_visible(self):
        return store.focused_visible

    def get_focused_node(self):
        if store.focused_id:
            return store.id_to_node.get(store.focused_id)
        return None

    def get_focused_tree(self):
        return store.focused_tree

    def autofocus_node(self, node: NodeType):
        if node.interactive and node.properties.autofocus:
            store.focused_id = node.id
            store.focused_tree = node.tree

    def set_ref_property_override(self, id, property_name, new_value):
        node = store.id_to_node.get(id)
        if node:
            node.tree.meta_state.set_ref_property_override(id, property_name, new_value)
            node.tree.render_manager.render_ref_change()

    def use_state(self, key, initial_value):
        self.init_state(key, initial_value)
        return store.reactive_state[key].value, lambda new_value: self.set_state_value(key, new_value)

    def register_effect(self, effect: Effect):
        store.staged_effects.append(effect)

    def highlight(self, id, color=None):
        node = store.id_to_node.get(id)
        if node:
            node.tree.highlight(id, color)

    def unhighlight(self, id):
        node = store.id_to_node.get(id)
        if node:
            node.tree.unhighlight(id)

    def highlight_briefly(self, id, color=None):
        node = store.id_to_node.get(id)
        if node:
            node.tree.highlight_briefly(id, color)

    def blur(self):
        store.focused_id = None

        if store.focused_tree:
            store.focused_tree.canvas_decorator.focused = True
            store.focused_tree.render_decorator_canvas()

    def blur_all(self):
        store.focused_id = None

        if store.focused_tree:
            store.focused_tree.canvas_decorator.focused = False
            store.focused_tree.render_decorator_canvas()
        store.focused_tree = None

    def focus_input(self, id):
        node = store.id_to_node.get(id)
        if node and node.input:
            # workaround for focus
            node.input.hide()
            node.input.show()

    def focus_node(self, node: NodeType, visible=True):
        blur_tree = None
        if node.tree != store.focused_tree:
            blur_tree = store.focused_tree

        store.focused_id = node.id
        store.focused_tree = node.tree
        store.focused_visible = visible

        if node.element_type == "input_text":
            self.focus_input(node.id)
        elif node.tree.canvas_decorator and not node.tree.canvas_decorator.focused:
            node.tree.canvas_decorator.focused = True

        if blur_tree:
            blur_tree.render_decorator_canvas()
        node.tree.render_decorator_canvas()

    def focus_next(self):
        interactive_nodes = []

        for tree in store.trees:
            interactive_nodes.extend(tree.interactive_node_list)

        if store.focused_id:
            current_node = store.id_to_node.get(store.focused_id)
            current_index = interactive_nodes.index(current_node)
            next_index = current_index + 1 if current_index < len(interactive_nodes) - 1 else 0
            next_node = interactive_nodes[next_index]
        elif store.focused_tree:
            next_node = store.focused_tree.interactive_node_list[0]
        else:
            next_node = interactive_nodes[0]

        self.focus_node(next_node)

    def focus_previous(self):
        interactive_nodes = []

        for tree in store.trees:
            interactive_nodes.extend(tree.interactive_node_list)

        if store.focused_id:
            current_node = store.id_to_node.get(store.focused_id)
            if current_node is None:
                return
            current_index = interactive_nodes.index(current_node)
            previous_index = current_index - 1 if current_index > 0 else len(interactive_nodes) - 1
            previous_node = interactive_nodes[previous_index]
        elif store.focused_tree:
            previous_node = store.focused_tree.interactive_node_list[-1]
        else:
            previous_node = interactive_nodes[-1]

        self.focus_node(previous_node)

    def scroll_to(self, id: str, x: int, y: int):
        node = store.id_to_node.get(id)
        if node:
            scroll_data = node.tree.meta_state.scrollable.get(id)
            if scroll_data and (scroll_data.offset_x != x or scroll_data.offset_y != y):
                scroll_data.offset_y = y
                scroll_data.offset_x = x
                node.tree.render()

    def increment_ref_count_nodes(self):
        store.ref_count_nodes += 1

    def decrement_ref_count_nodes(self):
        store.ref_count_nodes -= 1

    def get_ref_count_nodes(self):
        return store.ref_count_nodes

    def increment_ref_count_trees(self):
        store.ref_count_trees += 1

    def decrement_ref_count_trees(self):
        store.ref_count_trees -= 1

    def get_ref_count_trees(self):
        return store.ref_count_trees

    def get_components(self):
        components = {}
        for tree in store.trees:
            components[tree.guid] = tree.meta_state.components
        return components

    def toggle_hints(self, enabled: bool):
        if isinstance(enabled, bool):
            for tree in store.trees:
                tree.show_hints = enabled
        else:
            for tree in store.trees:
                tree.show_hints = not tree.show_hints

    def clear_state(self):
        store.reactive_state.clear()
        store.processing_states.clear()
        store.reset_mouse_state()
        state_coordinator.reset()

    def clear_state_for_tree(self, tree: TreeType):
        for state_key in tree.meta_state.states:
            if state_key in store.reactive_state:
                del store.reactive_state[state_key]
            if state_key in store.processing_states:
                store.processing_states.remove(state_key)
        if not store.processing_states or not store.trees:
            state_coordinator.reset()

    def clear_tree(self, tree: TreeType):
        if tree in store.trees:
            store.root_nodes = [node for node in store.root_nodes if node.tree != tree]
            store.trees.remove(tree)
            self.clear_state_for_tree(tree)
            store.synchronize_ids()

    def clear_all(self):
        store.clear()
        state_coordinator.reset()

    def deprecated_event_register_on_lifecycle(self, callback):
        if callback not in _deprecated_event_subscribers:
            _deprecated_event_subscribers.append(callback)

    def deprecated_event_unregister_on_lifecycle(self, callback):
        if callback in _deprecated_event_subscribers:
            _deprecated_event_subscribers.remove(callback)

    def deprecated_event_fire_on_lifecycle(self, event: DeprecatedLifecycleEvent):
        for callback in _deprecated_event_subscribers:
            callback(event)

    def deprecated_event_fire_on_mount(self, tree):
        self.deprecated_event_fire_on_lifecycle(DeprecatedLifecycleEvent("mount", tree))

    def deprecated_event_fire_on_unmount(self, tree):
        self.deprecated_event_fire_on_lifecycle(DeprecatedLifecycleEvent("unmount", tree))

state_manager = StateManager()

def debug_gc():
    gc.collect()
    print("gc actual nodes:", state_manager.get_ref_count_nodes())
    print("gc actual trees:", state_manager.get_ref_count_trees())
    print("Store nodes with ids:", len(store.id_to_node.keys()))
    print("Store trees:", len(store.trees))
    print("Store focused_tree", store.focused_tree)
    print("Store processing_tree", store.processing_tree)
    print("Store processing_states", store.processing_states)
    print("Store root_nodes", store.root_nodes)
    print("Store id_to_node", store.id_to_node)
    print("Store reactive_state", store.reactive_state)
    print("Store staged_effects", store.staged_effects)