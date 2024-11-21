from talon import Module, actions
from ..src.actions import ui_elements_new
from ..src.store import store
from ..src.entity_manager import entity_manager
from ..examples.counter import counter_ui
from ..examples.hello_world import hello_world_ui
from ..examples.todo_list import todo_list_ui
import traceback

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

def test_cases_todo_list_ui():
    trees = entity_manager.get_all_trees()
    nodes = entity_manager.get_all_nodes()
    test("There should be 1 tree", 1, len(trees))
    test("Tree should have 8 nodes", 8, len(nodes))
    test("Tree should have one button ref", 1, len(trees[0].meta_state.buttons))

@test_module
def test_cases_todo_list_ui():
    actions.user.ui_elements_new_show(todo_list_ui, on_mount=test_cases_todo_list_ui)

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

@test_module
def test_hello_world_ui():
    actions.user.ui_elements_new_show(hello_world_ui, on_mount=test_cases_hello_world_ui)

def test_cases_counter_ui():
    trees = entity_manager.get_all_trees()
    nodes = entity_manager.get_all_nodes()
    test("There should be 1 tree", 1, len(trees))
    test("Tree should have 6 nodes", 6, len(nodes))
    test("Tree should have one button ref", 1, len(trees[0].meta_state.buttons))

@test_module
def test_counter_ui():
    actions.user.ui_elements_new_show(counter_ui, on_mount=test_cases_counter_ui)

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

    def private_ui_elements_trigger():
        """Trigger the next test"""
        actions.user.ui_elements_new_set_state("count", lambda c: c + 1)