# import uuid
# from talon.skia.canvas import Canvas as SkiaCanvas
# from ..cursor import Cursor
# from ..interfaces import NodeComponentType
# from ..state_manager import state_manager
# from ..options import UIOptions

# class NodeComponent(NodeComponentType):
#     def __init__(self, func):
#         self.root_node = None
#         self.node_type = "component"
#         self.element_type = "component"

#         self.guid: str = uuid.uuid4().hex
#         self.func = func
#         self.options: UIOptions = UIOptions()
#         self.inner_node = None
#         self.is_initialized = False

#         self.children_nodes  = []
#         self.parent_node = None
#         self.is_dirty: bool = False

#         self.depth: int = None
#         self.setup_children()

#     def adopt_inner_node_attributes(self, node):
#         self.inner_node = node
#         self.box_model = node.box_model
#         self.options = node.options
#         self.root_node = node.root_node

#     def with_active_component(func):
#         def wrapper(self, *args, **kwargs):
#             state_manager.set_active_component_node(self)
#             result = func(self, *args, **kwargs)
#             self.adopt_inner_node_attributes(self.inner_node)
#             state_manager.set_active_component_node(None)
#             return result
#         return wrapper

#     @with_active_component
#     def setup_children(self):
#         self.inner_node = self.func()
#         self.children_nodes.append(self.inner_node)
#         self.inner_node.parent_node = self
#         self.is_initialized = True

#     @with_active_component
#     def virtual_render(self, c: SkiaCanvas, cursor: Cursor):
#         return self.children_nodes[0].virtual_render(c, cursor)

#     @with_active_component
#     def render(self, c: SkiaCanvas, cursor: Cursor, scroll_region_key: int = None):
#         return self.children_nodes[0].render(c, cursor, scroll_region_key)

#     def __getitem__(self):
#         raise Exception("""
#             Components cannot have children using [] syntax.
#             Instead use the return statement in the component function.
#         """)