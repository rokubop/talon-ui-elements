from typing import List, Dict
from .ui_elements_collection import (
    div,
    text,
    screen,
    button,
    input_text,
    effect,
    state,
    ref,
)

def ui_elements(elements: List[str]) -> tuple[callable]:
    element_mapping: Dict[str, callable] = {
        'button': button,
        'div': div,
        'input_text': input_text,
        'screen': screen,
        'text': text,
        'state': state,
        'ref': ref,
        'effect': effect,
    }
    if not all(element in element_mapping for element in elements):
        raise ValueError(
            f"\nInvalid elements {elements} provided to ui_elements"
            f"\nValid elements are {list(element_mapping.keys())}"
        )
    return tuple(element_mapping[element] for element in elements) if len(elements) > 1 else element_mapping[elements[0]]