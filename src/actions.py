from typing import List, Dict, Any
from .elements.index import (
    div,
    text,
    screen,
    button,
)

def ui_elements_new(elements: List[str]) -> tuple[callable]:
    element_mapping: Dict[str, callable] = {
        'div': div,
        'text': text,
        'screen': screen,
        'button': button,
    }
    return tuple(element_mapping[element] for element in elements)