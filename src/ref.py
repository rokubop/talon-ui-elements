from typing import Any
from talon.experimental.textarea import Span
from .entity_manager import entity_manager
from .state_manager import state_manager
# from .nodes.node_input_text import NodeInputText

class Ref:
    def __init__(self, id: str):
        self._set("id", id)
        self._set("element_type", None)

    def _get(self, name):
        """get self.something without triggering __getattr__"""
        return object.__getattribute__(self, name)

    def _set(self, name, value):
        """set self.something without triggering __setattr__"""
        object.__setattr__(self, name, value)

    def __getattr__(self, name):
        return self.get(name)

    def __setattr__(self, name, value):
        self.set(name, value)

    def get_element_type(self):
        element_type = self._get("element_type")
        if not element_type:
            node = self.get_node()
            self._set("element_type", node.element_type)
            return node.element_type
        return element_type

    def get_node(self):
        return entity_manager.get_node(self._get("id"))

    def clear(self):
        input_data = entity_manager.get_input_data(self._get("id"))
        input_data.input.erase(Span(0, len(input_data.input.value)))

    def focus(self):
        input_data = entity_manager.get_input_data(self._get("id"))
        input_data.input.hide()
        input_data.input.show()

    def set_text(self, new_value: Any):
        state_manager.set_text_mutation(self._get("id"), new_value)

    def set_value(self, new_value: Any):
        node = self.get_node()
        if node.element_type == "input_text":
            input_data = entity_manager.get_input_data(self._get("id"))
            input_data.input.value = new_value
        else:
            raise ValueError(f"Element type '{node.element_type}' does not support 'value' property")

    def set(self, name: str, new_value: Any):
        element_type = self.get_element_type()
        if name == "text":
            if element_type == "text":
                self.set_text(new_value)
            else:
                raise ValueError(f"Element type '{element_type}' does not support 'text' property")
        elif name == "value":
            if element_type == "input_text":
                self.set_value(new_value)
            else:
                raise ValueError(f"Element type '{element_type}' does not support 'value' property")
        else:
            state_manager.set_ref_option_override(self._get("id"), name, new_value)

    def get(self, name: str):
        element_type = self.get_element_type()
        if name == "text":
            if element_type == "text":
                return state_manager.get_text_mutation(self._get("id"))
            else:
                raise ValueError(f"Element type '{element_type}' does not support 'text' property")
        elif name == "value":
            if element_type == "input_text":
                input_data = entity_manager.get_input_data(self._get("id"))
                return input_data.input.value
            else:
                raise ValueError(f"Element type '{element_type}' does not support 'value' property")
        else:
            if node := self.get_node():
                if overrides := node.tree.meta_state.get_ref_option_overrides(self._get("id")):
                    return overrides.get(name)
                return getattr(node.options, name, None)

    def highlight(self, color=None):
        state_manager.highlight(self._get("id"), color)

    def unhighlight(self):
        state_manager.unhighlight(self._get("id"))

    def highlight_briefly(self, color=None):
        state_manager.highlight_briefly(self._get("id"), color)
