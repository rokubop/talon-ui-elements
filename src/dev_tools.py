from talon import actions
from .core.state_manager import state_manager
from .core.store import store

accent_color = "1bd0f5"

def key_val_state(key, value = "", level=0):
    div, text = actions.user.ui_elements(["div", "text"])

    if isinstance(value, dict):
        return div(flex_direction="column", gap=8)[
            text("  " * level + str(key), font_size=14, color=accent_color),
            div(flex_direction="column", gap=8)[
                *[key_val_state(k, v, level + 1) for k, v in value.items()]
            ]
        ]
    elif isinstance(value, list):
        return div(flex_direction="column", gap=8)[
            text("  " * level + str(key), font_size=14, color=accent_color),
            div(flex_direction="column", gap=8)[
                *[key_val_state(k, v, level + 1) for k, v in enumerate(value)]
            ]
        ]
    else:
        return div(flex_direction="row", align_items="flex_start", gap=8)[
            text("  " * level + str(key), font_size=14, color=accent_color),
            text(str(value), font_size=14)
        ]

def components_breakdown():
    results = []

    for tree in store.trees:
        if tree.name == "DevTools":
            continue
        results.append(key_val_state("Tree", tree.name))
        for id, component in tree.meta_state.components.items():
            results.append(key_val_state("Component", component.name, 1))
            results.append(key_val_state("node_index_path", id[1], 2))
            results.append(key_val_state("states", " ".join(component.states) if component.states else "None", 2))

    return results

def Accordion(props):
    div, text, icon, button, state = actions.user.ui_elements(["div", "text", "icon", "button", "state"])
    expanded, set_expanded = state.use_local("expanded", True)

    return div(font_family="consolas")[
        button(on_click=lambda: set_expanded(not expanded), padding=8, flex_direction="row", align_items="center", gap=8)[
            icon("chevron_down" if expanded else "chevron_right", size=16, color="FFFFFF"),
            text(props["title"], color="FFFFFF"),
        ],
        expanded and div(margin_left=8, padding=8)[
            props["content"] if props["content"] else text("None", font_size=14, color="666666"),
        ]
    ]

def component_accordion():
    div, component = actions.user.ui_elements(["div", "component"])

    return component(Accordion, {
        "title": "Components",
        "content": div(flex_direction="column", gap=8)[
            *components_breakdown(),
        ]
    })

def state_accordion():
    div, component = actions.user.ui_elements(["div", "component"])

    if store.reactive_state:
        reactive_states = {
            key: state.value for key, state in store.reactive_state.items()
            if "DevTools" not in key and "is_minimized" not in key
        }
        content = div(flex_direction="column", gap=8)[
            *[key_val_state(key, val) for key, val in reactive_states.items()]
        ]
    else:
        content = None

    return component(Accordion, {
        "title": "State",
        "content": content
    })

def DevTools():
    screen, window, div = actions.user.ui_elements(["screen", "window", "div"])

    return screen()[
        # top left not working
        window(title="Dev Tools", min_width=600, min_height=400, margin=100)[
            div(padding_bottom=8)[
                component_accordion(),
                state_accordion(),
            ]
        ]
    ]