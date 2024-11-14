from typing import Callable, List, Optional, TypedDict, Any, Union
from abc import ABC, abstractmethod

class EffectType(TypedDict):
    name: str
    callback: Callable[[], Callable]
    dependencies: Optional[List[str]]
    component_node: Optional[object]

class ReactiveStateType(ABC):
    value: Any
    subscriber_root_nodes: List[object]
    next_state_queue: List[Any]

    @abstractmethod
    def set_value(self, value: Any):
        pass

    @abstractmethod
    def add_subscriber(self, root_node: object):
        pass

    @abstractmethod
    def activate_next_state_value(self):
        pass

class GlobalStoreType(ABC):
    root_nodes: dict[str, dict]
    id_nodes: dict[str, dict]
    active_component: Optional[str]
    reactive_global_state: dict[str, ReactiveStateType]
    staged_effects: List[EffectType]

class NodeRootStateStoreType(ABC):
    effects: List[EffectType]
    state_to_effects: dict[str, List[EffectType]]
    state_to_components: dict[str, List[object]]

    @abstractmethod
    def add_effect(self, effect: EffectType):
        pass

    @abstractmethod
    def clear(self):
        pass

class NodeRootStoreType(ABC):
    components: List[object]
    buttons: List[object]
    inputs: List[object]
    dynamic_text: List[object]
    highlighted: List[object]
    scrollable_regions: List[object]

    @abstractmethod
    def clear(self):
        pass

class NodeType(ABC):
    options: object
    guid: str
    id: str
    key: str
    node_type: str
    element_type: str
    box_model: object
    children_nodes: List['NodeType']
    parent_node: Optional['NodeType']
    is_dirty: bool
    root_node: object
    depth: int
    component_node: object

    @abstractmethod
    def add_child(self, node: 'NodeType'):
        pass

    @abstractmethod
    def __getitem__(self, children_nodes: Union[List['NodeType'], 'NodeType']):
        pass

    @abstractmethod
    def invalidate(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

    @abstractmethod
    def check_invalid_child(self, c: 'NodeType'):
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def hide(self):
        pass

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def virtual_render(self):
        pass

    @abstractmethod
    def __init__(self, element_type: str, options: object):
        pass