from typing import Any
from talon.experimental.textarea import Span
from .entity_manager import entity_manager
from .state_manager import state_manager
from .nodes.node_input_text import NodeInputText

class Ref:
    def __init__(self, id: str):
        self.id = id
        self.element_type = None

    @property
    def text(self):
        return state_manager.get_text_mutation(self.id)

    @property
    def value(self):
        return state_manager.get_input_value(self.id)

    def get_node(self):
        return entity_manager.get_node(self.id)

    def clear(self):
        input_data = entity_manager.get_input_data(self.id)
        input_data.input.erase(Span(0, len(input_data.input.value)))

    def focus(self):
        input_data = entity_manager.get_input_data(self.id)
        input_data.input.hide()
        input_data.input.show()

    def set_text(self, new_value: Any):
        state_manager.set_text_mutation(self.id, new_value)

    def set(self, prop: str, new_value: Any):
        if prop == "text":
            return self.set_text(new_value)

        raise ValueError(
            f"ref set does not support '{prop}' for element type '{self.element_type}'"
            f"\nSupported methods and properties are:"
            f"\n- text (for text elements) "
            f"\n- set_text(new_value) (for text elements)"
            f"\n- value (for input_text)"
        )

    def get(self, prop: str):
        if not self.element_type:
            node = self.get_node()
            self.element_type = node.element_type

        if prop == "text":
            if self.element_type == "text":
                return self.text
        if prop == "value":
            if self.element_type == "input_text":
                input_data = entity_manager.get_input_data(self.id)
                return input_data.input.value

        if node := self.get_node():
            return node.options.get(prop)

        raise ValueError(f"ref get does not support '{prop}' for element type '{self.element_type}'")

    def highlight(self, color=None):
        state_manager.highlight(self.id, color)

    def unhighlight(self):
        state_manager.unhighlight(self.id)

    def highlight_briefly(self, color=None):
        state_manager.highlight_briefly(self.id, color)
