from typing import List, Dict
from .ui_elements_collection import (
    div,
    text,
    screen,
    button,
    input_text,
    use_effect,
    state,
    use_state,
    get_state,
    set_state,
)

def ui_elements(elements: List[str]) -> tuple[callable]:
    element_mapping: Dict[str, callable] = {
        'button': button,
        'div': div,
        'input_text': input_text,
        'screen': screen,
        'text': text,
        'state': state,
        'use_effect': use_effect,
        'use_state': use_state, # value, set_value
        'get_state': get_state, # value
        'set_state': set_state, # set_value
    }
    if not all(element in element_mapping for element in elements):
        raise ValueError(
            f"\nInvalid elements {elements} provided to ui_elements"
            f"\nValid elements are {list(element_mapping.keys())}"
        )
    return tuple(element_mapping[element] for element in elements) if len(elements) > 1 else element_mapping[elements[0]]