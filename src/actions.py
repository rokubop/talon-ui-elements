from typing import List, Dict, Any
from .ui_elements_collection import (
    div,
    text,
    screen,
    button,
    component,
    use_effect,
    use_state,
)

def ui_elements_new(elements: List[str]) -> tuple[callable]:
    element_mapping: Dict[str, callable] = {
        'div': div,
        'text': text,
        'screen': screen,
        'button': button,
        'component': component,
        'use_effect': use_effect,
        'use_state': use_state,
    }
    if not all(element in element_mapping for element in elements):
        raise ValueError(
            f"\nInvalid elements {elements} provided to ui_elements_new"
            f"\nValid elements are {list(element_mapping.keys())}"
        )
    return tuple(element_mapping[element] for element in elements) if len(elements) > 1 else element_mapping[elements[0]]