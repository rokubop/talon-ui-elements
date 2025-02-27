from talon import Context, cron
from typing import Callable
from .interfaces import NodeType, ReactiveStateType, TreeType, Effect
from .store import store
import gc

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
        next_state = self._value

        for new_state in self.next_state_queue:
            next_state = self.resolve_value(new_state)

        self.next_state_queue.clear()

        self._value = next_state

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

    def is_drag_active(self):
        return store.mouse_state['is_drag_active']

    def set_mousedown_start_id(self, id):
        store.mouse_state['mousedown_start_id'] = id

    def set_mousedown_start_pos(self, gpos):
        store.mouse_state['mousedown_start_pos'] = gpos

    def set_drag_relative_offset(self, offset):
        store.mouse_state['drag_relative_offset'] = offset

    def set_drag_active(self, is_active):
        store.mouse_state['is_drag_active'] = is_active

    def set_processing_tree(self, tree: TreeType):
        store.processing_tree = tree

    def get_processing_tree(self) -> TreeType:
        return store.processing_tree

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

    def rerender_state(self):
        for state in store.reactive_state.values():
            state.activate_next_state_value()

        for tree in store.trees:
            tree.processing_states.extend(store.processing_states)
            # tree.queue_render(RenderTask(
            #     cause=RenderCause.STATE_CHANGE,
            #     before_render=lambda: tree.processing_states.clear()
            #     after_render=lambda: tree.processing_states.clear()
            # )),
            tree.render_manager.render_state_change()

        # TODO: queue into render manager
        cron.after("30ms", store.processing_states.clear)
        # store.processing_states.clear()
        self.debounce_render_job = None

    def get_state_value(self, key):
        if key in store.reactive_state:
            return store.reactive_state[key].value
        return None

    def set_state_value(self, key, new_value):
        if key in store.reactive_state:
            if store.reactive_state[key].value == store.reactive_state[key].resolve_value(new_value):
                return

        self.init_state(key, new_value)
        store.reactive_state[key].set_value(new_value)
        store.processing_states.append(key)

        if not self.debounce_render_job:
            # Let the current event loop finish before rendering
            self.debounce_render_job = cron.after("1ms", self.rerender_state)

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

    def focus_node(self, node: NodeType):
        blur_tree = None
        if node.tree != store.focused_tree:
            blur_tree = store.focused_tree

        store.focused_id = node.id
        store.focused_tree = node.tree

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

    def clear_state(self):
        store.reactive_state.clear()
        store.processing_states.clear()
        store.reset_mouse_state()

    def clear_all(self):
        store.clear()

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