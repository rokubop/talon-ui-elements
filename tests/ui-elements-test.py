from talon import Module, actions
from ..src.actions import ui_elements_new
from ..src.node_manager import node_manager
from ..src.state_manager import state_manager

mod = Module()

test_cases = []

def test_module(fn):
    test_cases.append(fn)
    def wrapper():
        print(f"Test: {fn.__name__}")
        fn()
    return wrapper

def test(test_name, expect, actual):
    if expect == actual:
        print(f"✅ {test_name}")
    else:
        print(f"❌ {test_name}")
        print(f"Expected {expect} but got actual {actual}")

def test_truthy(test_name, actual):
    if actual:
        print(f"✅ {test_name}")
    else:
        print(f"❌ {test_name}")
        print(f"Expected True but got False")

@test_module
def test_component():
    el = ["div", "text", "screen", "component", "use_effect"]
    (div, text, screen, component, use_effect) = ui_elements_new(el)

    @component
    def hello_world():
        def on_mount():
            root_nodes = node_manager.get_root_nodes()
            all_nodes = node_manager.get_all_nodes()
            root_node = all_nodes[0]
            component_node = all_nodes[1]
            div_node = all_nodes[2]
            text_node = all_nodes[2]

            test("Global global_store should have 1 root node", 1, len(root_nodes))
            test("Root node should have 4 nodes", 4, len(all_nodes))
            test("div should have reference to component node", component_node, div_node.component_node)
            test("div should have reference to root node", root_node, div_node.root_node)
            test("active component should not be active outside of render cycle", state_manager.get_active_component_node(), None)
            test("root node should have 1 effect", 1, len(root_node.state_store.effects))
            test("root node should have named effects", "on_mount", root_node.state_store.effects[0]["name"])

        use_effect(on_mount, [])

        return div(background_color="green", padding=16, border_radius=16, border_width=1)[
            text("Component", color="red", font_size=24)
        ]

    ui = screen(justify_content="center", align_items="center")[
        hello_world()
    ]

    actions.user.ui_elements_show(ui)

@test_module
def test_hello_world():
    (div, text, screen) = ui_elements_new(["div", "text", "screen"])

    def on_mount():
        root_nodes = node_manager.get_root_nodes()
        all_nodes = node_manager.get_all_nodes()
        root_node = all_nodes[0]
        div_node = all_nodes[1]
        text_node = all_nodes[2]

        test("Global global_store should have 1 root node", 1, len(root_nodes))
        test("Root node should have 3 nodes", 3, len(all_nodes))
        test("div should have correct padding", 16, div_node.box_model.padding_spacing.top)
        test("div should have div element type", "div", div_node.element_type)
        test("div should have node type", "node", div_node.node_type)
        test("text should have text element type", "text", text_node.element_type)
        test("text should have leaf node type", "leaf", text_node.node_type)
        test("screen should have screen element type", "screen", root_node.element_type)
        test("screen should have root node type", "root", root_node.node_type)
        test("div should have 1 children node", 1, len(div_node.children_nodes))
        test_truthy("div should have 1 parent node", div_node.parent_node)
        test("divs parent and screen should be the same", div_node.parent_node, root_node)
        test("root should have depth 0", 0, root_node.depth)
        test("div should have depth 1", 1, div_node.depth)
        test("text should have depth 2", 2, text_node.depth)
        test("div should have reference to root_node", root_node, div_node.root_node)
        test("text should have reference to root_node", root_node, text_node.root_node)

    # use_effect(on_mount, [])

    ui = screen(justify_content="center", align_items="center")[
        div(background_color="white", padding=16, border_radius=16, border_width=1)[
            text("Hello world", color="red", font_size=24),
        ]
    ]
    # actions.user.ui_elements_show(ui)
    ui.show(on_mount)

@test_module
def test_button():
    (div, button, screen) = ui_elements_new(["div", "button", "screen"])

    def on_mount():
        root_nodes = node_manager.get_root_nodes()
        test("Global global_store should have 1 root node", 1, len(root_nodes))

        all_nodes = node_manager.get_all_nodes()
        root_node = root_nodes[0]
        buttons = node_manager.get_button_nodes(root_node)
        test("State should have 3 nodes", 3, len(all_nodes))
        test("State should have 1 button", 1, len(buttons))

        test("button should have element type button", "button", buttons[0].element_type)
        test("button should have node type leaf", "leaf", buttons[0].node_type)

    ui = screen(justify_content="center", align_items="center")[
        div(background_color="white", padding=16, border_radius=16, border_width=1)[
            button("Click me", on_click=lambda: print("hello"), background_color="blue", font_size=24),
        ]
    ]
    ui.show(on_mount)

def create_test_runner():
    return (test_fn for test_fn in test_cases)
test_gen = create_test_runner()

@mod.action_class
class Actions:
    def private_ui_elements_test():
        """Test the UI elements"""
        global test_gen

        try:
            actions.user.ui_elements_new_hide_all()
            next_test = next(test_gen)
            next_test()
        except StopIteration:
            actions.user.ui_elements_new_hide_all()
            print("All tests have been run.")
            test_gen = create_test_runner()

# active_tab_body = [div("Tab 1"), div("Tab 2"), div("Tab 3")]

# @component
# def container():
#     (div, state) = ui_elements_new(["div", "state"])

#     active_tab, set_active_tab = state("active_tab", 0)

#     return div(flex_direction="column")[
#         tabs(active_tab, set_active_tab),
#         body(active_tab)
#     ]

# @component
# def body(active_tab):
#     (div) = ui_elements_new(["div", "state"])

#     return div(width=500, height=500)[
#         active_tab_body[active_tab]
#     ]

# @component
# def tabs(active_tab, set_active_tab):
#     (div, text) = ui_elements_new(["div", "text", "set_state"])

#     return div(flex_direction="column")[
#         div(background_color=("00FF00" if active_tab == 0 else "FF0000"), on_click=lambda: set_active_tab(0))[text("Tab 1")],
#         div(background_color=("00FF00" if active_tab == 1 else "FF0000"), on_click=lambda: set_active_tab(1))[text("Tab 2")],
#         div(background_color=("00FF00" if active_tab == 2 else "FF0000"), on_click=lambda: set_active_tab(2))[text("Tab 3")]
#     ]

# def show_ui():
#     # example 1
#     elements = ui_elements_new(["div", "text", "button", "screen", "component", "effect", "state"])
#     (div, text, button, screen, component, effect, state) = elements

#     @component
#     def hello_world():
#         color, set_color = state("color", "red")

#         def on_mount():
#             test("State should have 3 nodes", 3, len(global_store.nodes))
#             test("State should have 1 root", 1, len(global_store.root_nodes))
#             nodes = list(global_store.nodes.values())
#             div_node = nodes[1]
#             text_node = nodes[2]
#             test("Div should have correct padding", 16, div_node.box_model.padding_spacing.top)

#         effect(lambda color: print(f"Color changed to {color}"), ["color"])
#         effect(on_mount, [])

#         return screen(justify_content="center", align_items="center")[
#             div(background_color=color, padding=16, border_radius=16, border_width=1)[
#                 text("Hello world", color="red", font_size=24),
#                 button("Change color", on_click=lambda: set_color("blue"))
#             ]
#         ]

#     actions.user.ui_elements_render(hello_world)

# elements = ui_elements_new(["div", "text", "button", "screen", "component", "effect", "state"])
# (div, text, button, screen, component, effect, state) = elements

# # example 2
# ui = screen(justify_content="center", align_items="center")[
#     div(background_color="red", padding=16, border_radius=16, border_width=1)[
#         text("Hello world", color="red", font_size=24),
#         button("Change color", on_click=lambda: print("hello"))
#     ]
# ]

# actions.user.ui_elements_render(ui)

# # other code
# actions.user.ui_elements_set_state("color", "blue")


# def col():
#     return div(flex_direction="column")

# @component
# def body():
#     state = use_state("active_tab", 0)
#     active_body = state_body_map[state]
#     return div(background_color="white", padding=16, border_radius=16, border_width=1)[
#         active_body()
#     ]

# class HelloWorld(Component):
#     def on_mount(self):
#         test("State should have 3 nodes", 3, len(state.nodes))
#         test("State should have 1 root", 1, len(state.root_nodes))
#         nodes = list(state.nodes.values())
#         div_node = nodes[1]
#         text_node = nodes[2]
#         test("Div should have correct padding", 16, div_node.box_model.padding_spacing.top)

#     def render(self):
#         return screen(justify_content="center", align_items="center")[
#             div(background_color="white", padding=16, border_radius=16, border_width=1)[
#                 text("Hello world", color="red", font_size=24),
#             ]
#         ]

# actions.user.ui_elements_render(ui)

# actions.sleep("100ms")

# test("Div should have correct padding", 885.0, div_node.box_model.margin_rect.x)
# test("Div should have correct padding", 516.0, div_node.box_model.margin_rect.y)

# active_tab_body = [div("Tab 1"), div("Tab 2"), div("Tab 3")]

# @component
# def container():
#     (div, state) = ui_elements_new(["div", "state"])

#     active_tab, set_active_tab = state("active_tab", 0)

#     return div(flex_direction="column")[
#         tabs(active_tab, set_active_tab),
#         body(active_tab)
#     ]

# @component
# def body(active_tab):
#     (div) = ui_elements_new(["div", "state"])

#     return div(width=500, height=500)[
#         active_tab_body[active_tab]
#     ]

# @component
# def tabs(active_tab, set_active_tab):
#     (div, text) = ui_elements_new(["div", "text", "set_state"])

#     return div(flex_direction="column")[
#         div(background_color=("00FF00" if active_tab == 0 else "FF0000"), on_click=lambda: set_active_tab(0))[text("Tab 1")],
#         div(background_color=("00FF00" if active_tab == 1 else "FF0000"), on_click=lambda: set_active_tab(1))[text("Tab 2")],
#         div(background_color=("00FF00" if active_tab == 2 else "FF0000"), on_click=lambda: set_active_tab(2))[text("Tab 3")]
#     ]

# def show_ui():
#     # example 1
#     elements = ui_elements_new(["div", "text", "button", "screen", "component", "effect", "state"])
#     (div, text, button, screen, component, effect, state) = elements

#     @component
#     def hello_world():
#         color, set_color = state("color", "red")

#         def on_mount():
#             test("State should have 3 nodes", 3, len(global_store.nodes))
#             test("State should have 1 root", 1, len(global_store.root_nodes))
#             nodes = list(global_store.nodes.values())
#             div_node = nodes[1]
#             text_node = nodes[2]
#             test("Div should have correct padding", 16, div_node.box_model.padding_spacing.top)

#         effect(lambda color: print(f"Color changed to {color}"), ["color"])
#         effect(on_mount, [])

#         return screen(justify_content="center", align_items="center")[
#             div(background_color=color, padding=16, border_radius=16, border_width=1)[
#                 text("Hello world", color="red", font_size=24),
#                 button("Change color", on_click=lambda: set_color("blue"))
#             ]
#         ]

#     actions.user.ui_elements_render(hello_world)

# elements = ui_elements_new(["div", "text", "button", "screen", "component", "effect", "state"])
# (div, text, button, screen, component, effect, state) = elements

# # example 2
# ui = screen(justify_content="center", align_items="center")[
#     div(background_color="red", padding=16, border_radius=16, border_width=1)[
#         text("Hello world", color="red", font_size=24),
#         button("Change color", on_click=lambda: print("hello"))
#     ]
# ]

# actions.user.ui_elements_render(ui)

# # other code
# actions.user.ui_elements_set_state("color", "blue")


# def col():
#     return div(flex_direction="column")

# @component
# def body():
#     state = use_state("active_tab", 0)
#     active_body = state_body_map[state]
#     return div(background_color="white", padding=16, border_radius=16, border_width=1)[
#         active_body()
#     ]

# class HelloWorld(Component):
#     def on_mount(self):
#         test("State should have 3 nodes", 3, len(state.nodes))
#         test("State should have 1 root", 1, len(state.root_nodes))
#         nodes = list(state.nodes.values())
#         div_node = nodes[1]
#         text_node = nodes[2]
#         test("Div should have correct padding", 16, div_node.box_model.padding_spacing.top)

#     def render(self):
#         return screen(justify_content="center", align_items="center")[
#             div(background_color="white", padding=16, border_radius=16, border_width=1)[
#                 text("Hello world", color="red", font_size=24),
#             ]
#         ]

# actions.user.ui_elements_render(ui)

# actions.sleep("100ms")

# test("Div should have correct padding", 885.0, div_node.box_model.margin_rect.x)
# test("Div should have correct padding", 516.0, div_node.box_model.margin_rect.y)
