from talon import Module, actions
from ..src.core.entity_manager import entity_manager
from .hello_world_ui import hello_world_ui
from .todo_list_ui import todo_list_ui
from .alignment_ui import alignment_ui
from .state_vs_refs_ui import state_vs_refs_ui
from .cheatsheet_ui import cheatsheet_ui
from .inputs_ui import inputs_ui
from .dashboard_ui import show_dashboard_ui
from .examples_ui import examples_ui

mod = Module()

test_cases = []

def test_module(fn):
    test_cases.append(fn)
    def wrapper():
        print(f"Test: {fn.__name__}")
        fn()
    return wrapper

# Tests disabled for now

# @test_module
def examples_ui():
    actions.user.ui_elements_show(examples_ui)

# @test_module
def test_dashboard_ui():
    show_dashboard_ui()

# @test_module
def test_cheatsheet_ui():
    actions.user.ui_elements_show(cheatsheet_ui)

# @test_module
def test_inputs_ui():
    actions.user.ui_elements_show(inputs_ui)

# @test_module
def test_updating_content_ui():
    actions.user.ui_elements_show(state_vs_refs_ui)

# @test_module
def test_alignment_ui():
    actions.user.ui_elements_show(alignment_ui, on_mount=test_cases_alignment_ui)

# @test_module
def test_todo_list_ui():
    actions.user.ui_elements_show(todo_list_ui, on_mount=test_cases_todo_list_ui)

# @test_module
def test_hello_world_ui():
    actions.user.ui_elements_show(hello_world_ui, on_mount=test_cases_hello_world_ui)

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

def test_cases_alignment_ui():
    trees = entity_manager.get_all_trees()
    nodes = entity_manager.get_all_nodes()
    test("There should be 1 tree", 1, len(trees))
    test("Tree should have 3 nodes", 3, len(nodes))
    test("Tree should have one button ref", 1, len(trees[0].meta_state.buttons))

def test_cases_todo_list_ui():
    trees = entity_manager.get_all_trees()
    nodes = entity_manager.get_all_nodes()
    test("There should be 1 tree", 1, len(trees))
    test("Tree should have 8 nodes", 8, len(nodes))
    test("Tree should have one button ref", 1, len(trees[0].meta_state.buttons))

def test_cases_hello_world_ui():
    trees = entity_manager.get_all_trees()
    nodes = entity_manager.get_all_nodes()
    screen_node = nodes[0]
    div_node = nodes[1]
    text_node = nodes[2]

    # --- Tree Structure Tests ---
    test("Global store should have 1 tree", 1, len(trees))
    tree = trees[0]
    test_truthy("Tree should have a root nodes", tree.root_node)
    test("Tree's root node should be screen", screen_node, tree.root_node)
    test("Tree should have 3 nodes", 3, len(nodes))

    # --- Node Attributes Tests ---
    test("screen should have screen element type", "screen", screen_node.element_type)
    test("screen should have root node type", "root", screen_node.node_type)
    test("div should have div element type", "div", div_node.element_type)
    test("div should have node type", "node", div_node.node_type)
    test("text should have text element type", "text", text_node.element_type)
    test("text should have leaf node type", "leaf", text_node.node_type)

    # --- Node Hierarchy Tests ---
    test("div should have 1 children node", 1, len(div_node.children_nodes))
    test_truthy("div should have 1 parent node", div_node.parent_node)
    test("divs parent and screen should be the same", div_node.parent_node, screen_node)
    test("root should have depth 0", 0, screen_node.depth)
    test("div should have depth 1", 1, div_node.depth)
    test("text should have depth 2", 2, text_node.depth)

    # --- Styling Tests ---
    test("div should have correct padding", 16, div_node.box_model.padding_spacing.top)
    test("div should have reference to tree", tree, div_node.tree)

    # --- Node and Tree References Tests ---
    test("screen should have reference to tree", tree, screen_node.tree)
    test("div should have reference to tree", tree, div_node.tree)
    test("text should have reference to tree", tree, text_node.tree)

def create_test_runner():
    return (test_fn for test_fn in test_cases)
test_gen = create_test_runner()

# def ui_elements_test():
#     if not actions.user.ui_elements_get_trees():
#         actions.user.ui_elements_show(examples_ui)
#     else:
#         actions.user.ui_elements_hide_all()

    # Tests disabled for now

    # global test_gen

    # try:
    #     actions.user.ui_elements_hide_all()
    #     next_test = next(test_gen)
    #     next_test()
    # except StopIteration:
    #     actions.user.ui_elements_hide_all()
    #     print("All tests have been run.")
    #     test_gen = create_test_runner()