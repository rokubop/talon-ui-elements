from talon import Context, actions, cron
from talon.experimental.textarea import TextArea
from typing import Callable
from .interfaces import NodeType, ReactiveStateType, TreeType, Effect, ClickEvent
from .store import store
from .utils import safe_callback, get_center

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
        self.builder_id = tree.root_node.id or tree.root_node.guid
        self.children_ids = tree.meta_state.id_to_node.keys()

_deprecated_event_subscribers = {}

class HintGenerator:
    def __init__(self):
        c_char = 99
        d_char = 100
        z_char = 123

        # Arbitrary decisions:
        # - Start buttons with 'b' and input_text with 'i'
        # - Second character start is based on personal
        #   preference for better recognition
        self.char_map = {
            "button": ("b", [chr(i) for i in range(c_char, z_char)]),
            "input_text": ("i", [chr(i) for i in range(d_char, z_char)])
        }

        # rather than using a generator, we increment char index
        self.state = {
            "button": 0,
            "input_text": 0
        }

    def generate_hint(self, node: NodeType):
        if node.id in store.id_to_hint:
            return store.id_to_hint[node.id]

        if node.element_type in self.char_map:
            first_char, second_char_list = self.char_map[node.element_type]
            index = self.state[node.element_type]
            if index < len(second_char_list):
                hint = f"{first_char}{second_char_list[index]}"
                self.state[node.element_type] += 1
                store.id_to_hint[node.id] = hint
                return hint
            else:
                print("Ran out of hint values while generating hints.")
                return ""

class StateManager:
    def __init__(self):
        self.hint_generator = HintGenerator()
        self.debounce_render_job = None
        self.ctx = Context()

    def get_hovered_id(self):
        return store.mouse_state['hovered_id']

    def set_hovered_id(self, id):
        store.mouse_state['hovered_id'] = id

    def get_mousedown_start_id(self):
        return store.mouse_state['mousedown_start_id']

    def set_mousedown_start_id(self, id):
        store.mouse_state['mousedown_start_id'] = id

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
            raise ValueError("use_state must include a string name like this: use_state('my_state', initial_value)")

        if key not in store.reactive_state:
            store.reactive_state[key] = ReactiveState()

        store.reactive_state[key].set_initial_value(initial_value)

    def rerender_state(self):
        for state in store.reactive_state.values():
            state.activate_next_state_value()

        for tree in store.trees:
            tree.processing_states.extend(store.processing_states)
            tree.render()

        store.processing_states.clear()
        self.debounce_render_job = None

    def set_state_value(self, key, value):
        self.init_state(key, value)
        store.reactive_state[key].set_value(value)
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
            node.tree.render_text_mutation()
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
            return node.tree.meta_state.inputs.get(id)
        return ""

    def use_input_value(self, node: NodeType):
        if node.tree.meta_state.inputs.get(node.id):
            return node.tree.meta_state.inputs[node.id]
        node.tree.meta_state.inputs[node.id] = node.options.value or ""
        return node.options.value

    def use_state(self, key, initial_value):
        self.init_state(key, initial_value)
        return store.reactive_state[key].value, lambda new_value: self.set_state_value(key, new_value)

    def register_effect(self, effect: Effect):
        store.staged_effects.append(effect)

    def clear_state(self):
        store.reactive_state.clear()
        store.processing_states.clear()
        store.reset_mouse_state()
        store.id_to_hint.clear()
        self.reset_hint_generator()
        self.hint_tag_disable()

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

    def reset_hint_generator(self):
        self.hint_generator = HintGenerator()

    def get_hint_generator(self):
        return self.hint_generator.generate_hint

    def hint_tag_enable(self):
        self.ctx.tags = ["user.ui_elements_hints_active"]

    def hint_tag_disable(self):
        self.ctx.tags = []

    def trigger_hint_action(self, hint_trigger: str):
        for id, hint in store.id_to_hint.items():
            if hint == hint_trigger:
                node = store.id_to_node.get(id)
                if node:
                    if node.element_type == "button":
                        self.highlight_briefly(id)
                        safe_callback(node.on_click, ClickEvent(id=id, cause="hint"))
                    elif node.element_type == "input_text":
                        # probably prefer TextArea focus if it becomes available
                        x, y = get_center(node.box_model.padding_rect)
                        actions.mouse_move(x, y)
                        actions.mouse_click()
                break

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
