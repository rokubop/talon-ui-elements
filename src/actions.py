from typing import List, Dict, Any
from .ui_elements_collection import (
    div,
    text,
    screen,
    button,
    component,
    use_effect,
)

def ui_elements_new(elements: List[str]) -> tuple[callable]:
    element_mapping: Dict[str, callable] = {
        'div': div,
        'text': text,
        'screen': screen,
        'button': button,
        'component': component,
        'use_effect': use_effect,
    }
    return tuple(element_mapping[element] for element in elements)