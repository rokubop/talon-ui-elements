from talon import Context, cron
from typing import Callable, Optional
from ..interfaces import (
    Effect,
    NodeType,
    ReactiveStateType,
    StyleType,
    TreeType,
)
from .store import store
from .render_manager import RenderTaskScrolling, RenderTask, RenderCause, on_base_canvas_change
import gc

class StateCoordinator:
    PHASE_FREE = "free"
    PHASE_BATCH = "batch"
    PHASE_REQUEST_RENDER = "request_render"
    PHASE_RENDERING = "rendering"

    def __init__(self):
        self.locked = False
        self.phase = self.PHASE_FREE
        self.current_state_keys = set()
        self.next_state_keys = set()
        self.pending_tree_renders = set()
        self.batch_job = None

    def finish_cycle(self, tree: TreeType):
        if self.locked:
            self.current_state_keys.clear()
            self.locked = False
            self.phase = self.PHASE_FREE

            if self.next_state_keys:
                self.current_state_keys.update(self.next_state_keys)
                self.next_state_keys.clear()

            if self.current_state_keys:
                for key in self.current_state_keys:
                    self.request_state_change(key)
        store.mouse_state['disable_events'] = False

    def flush_state(self):
        for key in self.current_state_keys:
            store.reactive_state[key].activate_next_state_value()

    def on_tree_render_start(self):
        def on_start(tree: TreeType, *args):
            if not self.locked:
                self.locked = True
                self.phase = self.PHASE_RENDERING
                self.flush_state()

            tree.render(*args)

        return on_start

    def on_tree_render_end(self):
        def on_end(e):
            self.pending_tree_renders.remove(e.tree.guid)

            if not self.pending_tree_renders:
                self.finish_cycle(e.tree)

        return on_end

    def request_tree_renders(self):
        if self.locked:
            return

        if self.phase == self.PHASE_BATCH:
            self.phase = self.PHASE_REQUEST_RENDER
            if self.batch_job:
                cron.cancel(self.batch_job)
            self.batch_job = None

        if self.phase == self.PHASE_REQUEST_RENDER:
            trees = state_manager.get_trees_for_state_keys(self.current_state_keys)

            for tree in trees:
                if tree.guid not in self.pending_tree_renders:
                    self.pending_tree_renders.add(tree.guid)
                    tree.render_manager.schedule_state_change(
                        on_start=self.on_tree_render_start(),
                        on_end=self.on_tree_render_end()
                    )

            if not self.pending_tree_renders:
                self.finish_cycle(None)

    def request_state_change(self, state_key: str):
        store.mouse_state['disable_events'] = True
        if self.locked:
            self.next_state_keys.add(state_key)
            return

        self.current_state_keys.add(state_key)

        if self.phase == self.PHASE_FREE:
            self.phase = self.PHASE_BATCH

        if self.phase == self.PHASE_BATCH:
            if self.batch_job:
                cron.cancel(self.batch_job)
            self.batch_job = cron.after("1ms", self.request_tree_renders)
        elif self.phase == self.PHASE_REQUEST_RENDER:
            # If we're already in REQUEST_RENDER phase, directly request renders
            # This can happen if a state change occurs while we're processing another state change
            self.request_tree_renders()

    def reset(self):
        store.mouse_state['disable_events'] = False
        self.locked = False
        self.phase = self.PHASE_FREE
        self.current_state_keys.clear()
        self.next_state_keys.clear()
        self.pending_tree_renders.clear()
        if self.batch_job:
            cron.cancel(self.batch_job)
            self.batch_job = None

state_coordinator = StateCoordinator()

class ReactiveState(ReactiveStateType):
    def __init__(self):
        self._initial_value = None
        self._value = None
        self.next_state_queue = []

    @property
    def initial_value(self):
        return self._initial_value

    @property
    def value(self):
        return self._value

    def resolve_value(self, value_or_callable):
        if callable(value_or_callable):
            return value_or_callable(self._value)
        return value_or_callable

    def set_initial_value(self, value):
        if self._initial_value is None:
            self._initial_value = value
            self._value = value

    def set_value(self, value_or_callable):
        self.next_state_queue.append(value_or_callable)

    def activate_next_state_value(self):
        for new_state in self.next_state_queue:
            self._value = self.resolve_value(new_state)

        self.next_state_queue.clear()

class DeprecatedLifecycleEvent:
    def __init__(self, event_type: str, tree: TreeType):
        self.type = event_type
        self.builder_id = getattr(tree.root_node, 'id') or tree.root_node.guid
        self.children_ids = tree.meta_state.id_to_node.keys()

_deprecated_event_subscribers = []

class StateManager:
    def __init__(self):
        self.debounce_render_job = None
        self.ctx = Context()
        self._smooth_scroll_job = None
        self._smooth_scroll_state = None

    def get_hovered_id(self):
        return store.mouse_state['hovered_id']

    def set_hovered_id(self, id):
        store.mouse_state['hovered_id'] = id

    def get_mousedown_start_id(self):
        return store.mouse_state['mousedown_start_id']

    def get_drag_relative_offset(self):
        return store.mouse_state['drag_relative_offset']

    def get_mousedown_start_pos(self):
        return store.mouse_state['mousedown_start_pos']

    def get_mousedown_start_offset(self):
        return store.mouse_state['mousedown_start_offset']

    def set_last_clicked_pos(self, pos):
        store.mouse_state['last_clicked_pos'] = pos

    def get_last_clicked_pos(self):
        return store.mouse_state['last_clicked_pos']

    def is_drag_active(self):
        return store.mouse_state['is_drag_active']

    def set_mousedown_start_id(self, id):
        store.mouse_state['mousedown_start_id'] = id

    def set_mousedown_start_pos(self, gpos):
        store.mouse_state['mousedown_start_pos'] = gpos

    def set_mousedown_start_offset(self, offset):
        store.mouse_state['mousedown_start_offset'] = offset

    def set_drag_relative_offset(self, offset):
        store.mouse_state['drag_relative_offset'] = offset

    def set_drag_active(self, is_active):
        store.mouse_state['is_drag_active'] = is_active

    def set_processing_tree(self, tree: TreeType):
        if tree is None:
            if store.processing_tree_stack:
                store.processing_tree_stack.pop()
        else:
            store.processing_tree_stack.append(tree)

    def get_processing_style(self) -> StyleType:
        context = state_manager.get_processing_component() \
            or state_manager.get_processing_tree()
        if context and getattr(context, 'style', None):
            return context.style

    def get_processing_tree(self) -> TreeType:
        return store.processing_tree_stack[-1] if store.processing_tree_stack else None

    def set_processing_component(self, component):
        tree = self.get_processing_tree()
        if tree:
            if tree not in store.processing_components:
                store.processing_components[tree] = []
            store.processing_components[tree].append(component)

    def get_processing_components(self):
        tree = self.get_processing_tree()
        if tree and tree in store.processing_components:
            return store.processing_components[tree]
        return []

    def get_processing_component(self):
        tree = self.get_processing_tree()
        if tree and tree in store.processing_components:
            components = store.processing_components[tree]
            if components:
                return components[-1]
        return None

    def get_processing_states(self):
        return state_coordinator.current_state_keys

    def remove_processing_component(self, component):
        tree = self.get_processing_tree()
        if tree and tree in store.processing_components:
            try:
                store.processing_components[tree].remove(component)
            except ValueError:
                # Component not in list - shouldn't happen but handle gracefully
                pass

    def get_trees_for_state(self, state_key):
        try:
            return [tree for tree in store.trees if state_key in tree.meta_state.state_keys]
        except Exception as e:
            return []

    def get_trees_for_state_keys(self, state_keys):
        try:
            return [tree for tree in store.trees if \
                any(key in state_keys for key in tree.meta_state.states)
            ]
        except Exception as e:
            return []

    def disable_mouse_events(self):
        store.mouse_state['disable_events'] = True

    def enable_mouse_events(self):
        store.mouse_state['disable_events'] = False

    def are_mouse_events_disabled(self):
        return store.mouse_state['disable_events']

    def init_states(self, states):
        if states is not None:
            for key, value in states.items():
                self.init_state(key, value)

    def init_state(self, key, initial_value):
        if type(key) is not str:
            raise ValueError("state must include a string key like this: state.use('my_state', initial_value) or state.get('my_state')")

        if key not in store.reactive_state:
            store.reactive_state[key] = ReactiveState()

        store.reactive_state[key].set_initial_value(initial_value)

    def get_state_value(self, key, initial_value=None):
        if key in store.reactive_state:
            return store.reactive_state[key].value
        elif initial_value is not None:
            # State doesn't exist yet, initialize it with the default
            self.init_state(key, initial_value)
            return initial_value
        return None

    def get_all_states(self):
        return {key: store.reactive_state[key].value for key in store.reactive_state.keys()}

    def set_state_value(self, key, new_value):
        if not store.pause_renders:
            if key in store.reactive_state:
                if store.reactive_state[key].value == store.reactive_state[key].resolve_value(new_value):
                    return

            self.init_state(key, new_value)
            store.reactive_state[key].set_value(new_value)
            store.processing_states.add(key)
            state_coordinator.request_state_change(key)

    def get_text_mutation(self, id):
        node = store.id_to_node.get(id)
        if node:
            return node.tree.meta_state.get_text_mutation(id)
        return ""

    def set_text_mutation(self, id, text_or_callable):
        node = store.id_to_node.get(id)
        if node:
            text_mutations = node.tree.meta_state.text_mutations
            old_value = text_mutations.get(id)
            if isinstance(text_or_callable, Callable):
                new_value = str(text_or_callable(old_value if old_value is not None else ""))
            else:
                new_value = str(text_or_callable)
            if new_value == old_value:
                return
            text_mutations[id] = new_value
            node.tree.render_manager.render_text_mutation()
        else:
            print(f"Node with ID '{id}' not found.")

    def use_text_mutation(self, node: NodeType):
        if node.tree.meta_state.text_mutations.get(node.id):
            return node.tree.meta_state.text_mutations[node.id]
        node.tree.meta_state.text_mutations[node.id] = node.text
        return node.text

    def get_input_value(self, id):
        from ..platform.custom_input import custom_input_manager
        return custom_input_manager.get_value(id)

    def is_focused(self, id):
        return store.focused_id == id

    def is_focus_visible(self):
        return store.focused_visible

    def get_focused_node(self):
        if store.focused_id:
            return store.id_to_node.get(store.focused_id)
        return None

    def get_focused_tree(self):
        return store.focused_tree

    def autofocus_node(self, node: NodeType):
        if node.interactive and node.properties.autofocus:
            store.focused_id = node.id
            store.focused_tree = node.tree
            store.focused_visible = True
            if node.element_type in ("input_text", "textarea"):
                focus_method = self.focus_textarea if node.element_type == "textarea" else self.focus_input
                def delayed_focus():
                    # Tree may have been destroyed in the 100ms gap (eg.
                    # render error or window close). Bail before
                    # dereferencing node.tree.
                    if node.tree is None:
                        return
                    focus_method(node.id)
                    if node.tree.canvas_decorator:
                        node.tree.canvas_decorator.focused = True
                        node.tree.render_decorator_canvas()
                cron.after("100ms", delayed_focus)

    def set_ref_property_override(self, id, property_name, new_value):
        node = store.id_to_node.get(id)
        if node:
            node.tree.meta_state.set_ref_property_override(id, property_name, new_value)
            node.tree.render_manager.render_ref_change()

    def use_state(self, key, initial_value):
        self.init_state(key, initial_value)
        return store.reactive_state[key].value, lambda new_value: self.set_state_value(key, new_value)

    def register_effect(self, effect: Effect):
        store.staged_effects.append(effect)

    def highlight(self, id, color=None):
        node = store.id_to_node.get(id)
        if node:
            node.tree.highlight(id, color)

    def unhighlight(self, id):
        node = store.id_to_node.get(id)
        if node:
            node.tree.unhighlight(id)

    def highlight_briefly(self, id, color=None):
        node = store.id_to_node.get(id)
        if node:
            node.tree.highlight_briefly(id, color)

    def blur(self, pos=None):
        from ..platform.custom_input import custom_input_manager
        if custom_input_manager.has_focused_input:
            custom_input_manager.blur()
        store.focused_id = None
        store.blur_pos = pos

        if store.focused_tree and store.focused_tree.canvas_decorator:
            store.focused_tree.canvas_decorator.focused = True
            store.focused_tree.render_decorator_canvas()

    def blur_all(self, pos=None):
        from ..platform.custom_input import custom_input_manager
        if custom_input_manager.has_focused_input:
            custom_input_manager.blur()
        store.focused_id = None
        store.blur_pos = pos

        if store.focused_tree and store.focused_tree.canvas_decorator:
            store.focused_tree.canvas_decorator.focused = False
            store.focused_tree.render_decorator_canvas()
        store.focused_tree = None

    def focus_input(self, id):
        from ..platform.custom_input import custom_input_manager
        custom_input_manager.focus(id)

    def focus_textarea(self, id):
        from ..platform.custom_input import custom_input_manager
        custom_input_manager.focus(id)

    def focus_node(self, node: NodeType, visible=True):
        blur_tree = None
        if node.tree != store.focused_tree:
            blur_tree = store.focused_tree

        # Blur custom input when focus moves away from it
        is_custom_input_node = node.element_type in ("input_text", "textarea")
        from ..platform.custom_input import custom_input_manager
        if custom_input_manager.has_focused_input and \
                (not is_custom_input_node or custom_input_manager.focused_id != node.id):
            custom_input_manager.blur()

        store.focused_id = node.id
        store.focused_tree = node.tree
        store.focused_visible = visible
        store.blur_pos = None

        if node.element_type == "textarea":
            self.focus_textarea(node.id)
            if node.tree.canvas_decorator:
                node.tree.canvas_decorator.focused = True
        elif node.element_type == "input_text":
            self.focus_input(node.id)
            if node.tree.canvas_decorator:
                node.tree.canvas_decorator.focused = True
        elif node.tree.canvas_decorator and not node.tree.canvas_decorator.focused:
            node.tree.canvas_decorator.focused = True

        if blur_tree:
            blur_tree.render_decorator_canvas()
        node.tree.render_decorator_canvas()

    def _find_nearest_node(self, nodes, pos):
        """Find the nearest interactive node to a position based on distance to node center."""
        nearest = None
        nearest_dist = float('inf')
        for node in nodes:
            if not getattr(node, 'box_model', None) or not node.box_model.border_rect:
                continue
            rect = node.box_model.border_rect
            cx = rect.x + rect.width / 2
            cy = rect.y + rect.height / 2
            dist = (pos.x - cx) ** 2 + (pos.y - cy) ** 2
            if dist < nearest_dist:
                nearest_dist = dist
                nearest = node
        return nearest

    def focus_next(self):
        interactive_nodes = []

        for tree in store.trees:
            interactive_nodes.extend(n for n in tree.interactive_node_list if n.focusable)

        if store.focused_id:
            current_node = store.id_to_node.get(store.focused_id)

            if current_node is None:
                # The focused node was deleted, clear the focus and start from beginning
                store.focused_id = None
                if interactive_nodes:
                    self.focus_node(interactive_nodes[0])
                return

            current_index = interactive_nodes.index(current_node)
            next_index = current_index + 1 if current_index < len(interactive_nodes) - 1 else 0
            next_node = interactive_nodes[next_index]
        elif store.blur_pos and interactive_nodes:
            next_node = self._find_nearest_node(interactive_nodes, store.blur_pos)
        elif store.focused_tree:
            focusable_in_tree = [n for n in store.focused_tree.interactive_node_list if n.focusable]
            next_node = focusable_in_tree[0] if focusable_in_tree else None
        else:
            next_node = interactive_nodes[0] if interactive_nodes else None

        if next_node:
            store.blur_pos = None
            self.focus_node(next_node)

    def focus_previous(self):
        interactive_nodes = []

        for tree in store.trees:
            interactive_nodes.extend(n for n in tree.interactive_node_list if n.focusable)

        if store.focused_id:
            current_node = store.id_to_node.get(store.focused_id)

            if current_node is None:
                # The focused node was deleted, clear the focus and start from beginning
                store.focused_id = None
                if interactive_nodes:
                    self.focus_node(interactive_nodes[0])
                return

            current_index = interactive_nodes.index(current_node)
            previous_index = current_index - 1 if current_index > 0 else len(interactive_nodes) - 1
            previous_node = interactive_nodes[previous_index]
        elif store.blur_pos and interactive_nodes:
            previous_node = self._find_nearest_node(interactive_nodes, store.blur_pos)
        elif store.focused_tree:
            focusable_in_tree = [n for n in store.focused_tree.interactive_node_list if n.focusable]
            previous_node = focusable_in_tree[-1] if focusable_in_tree else None
        else:
            previous_node = interactive_nodes[-1] if interactive_nodes else None

        if previous_node:
            store.blur_pos = None
            self.focus_node(previous_node)

    def _get_scroll_data(self, node, id: str):
        """Get scroll data for a node, checking body_node for data_tables."""
        scroll_data = node.tree.meta_state.scrollable.get(id)
        if scroll_data:
            return scroll_data, id
        body = getattr(node, '_body_node', None)
        if body and body.id:
            scroll_data = node.tree.meta_state.scrollable.get(body.id)
            if scroll_data:
                return scroll_data, body.id
        return None, None

    def scroll_to_top(self, id: str):
        node = store.id_to_node.get(id)
        if node:
            scroll_data, scroll_id = self._get_scroll_data(node, id)
            if scroll_data and scroll_data.offset_y != 0:
                scroll_data.offset_y = 0
                scroll_data.target_offset_y = 0
                node.tree._scrollbar_show(scroll_id)
                node.tree.render_manager.queue_render(RenderTaskScrolling)

    def scroll_to_bottom(self, id: str):
        node = store.id_to_node.get(id)
        if node:
            tree = node.tree
            scroll_id = id
            body = getattr(node, '_body_node', None)
            if body and body.id and tree.meta_state.scrollable.get(body.id):
                scroll_id = body.id
            def apply_scroll_to_bottom(tree):
                scroll_data = tree.meta_state.scrollable.get(scroll_id)
                if scroll_data:
                    bottom = min(0, scroll_data.view_height - scroll_data.max_height)
                    if scroll_data.offset_y != bottom:
                        scroll_data.offset_y = bottom
                        scroll_data.target_offset_y = bottom
                        tree._scrollbar_show(scroll_id)
                on_base_canvas_change(tree)
            tree.render_manager.queue_render(RenderTask(
                RenderCause.SCROLLING,
                apply_scroll_to_bottom,
            ))

    def scroll_to(self, id: str, x: int, y: int):
        node = store.id_to_node.get(id)
        if node:
            scroll_data, scroll_id = self._get_scroll_data(node, id)
            if scroll_data and (scroll_data.offset_x != x or scroll_data.offset_y != y):
                scroll_data.offset_y = y
                scroll_data.offset_x = x
                node.tree._scrollbar_show(scroll_id)
                node.tree.render_manager.queue_render(RenderTaskScrolling)

    def smooth_scroll_node(self, id: str, axis: str = "y", direction: int = -1, fraction: float = 0.85):
        """Smoothly scroll a specific scrollable container by a fraction of its view size.
        axis: "y" or "x". direction: 1 = up/left, -1 = down/right.
        Reuses an in-flight scroll easing job, supporting redirection mid-scroll.
        Used by both the voice "scroll up/down" command and the floating scroll buttons."""
        node = store.id_to_node.get(id)
        if not node:
            return
        scroll_data, scroll_id = self._get_scroll_data(node, id)
        if not scroll_data:
            return
        scroll_node = node.tree.meta_state.id_to_node.get(scroll_id) or node
        if not scroll_node.box_model:
            return

        if axis == "y":
            view = scroll_node.box_model.padding_size.height
            content = scroll_node.box_model.content_children_with_padding_size.height
        else:
            view = scroll_node.box_model.padding_size.width
            content = scroll_node.box_model.content_children_with_padding_size.width

        offset_attr = "offset_y" if axis == "y" else "offset_x"
        target_attr = "target_offset_y" if axis == "y" else "target_offset_x"
        view_attr = "view_height" if axis == "y" else "view_width"
        max_attr = "max_height" if axis == "y" else "max_width"

        current_offset = getattr(scroll_data, offset_attr)
        prior = self._smooth_scroll_state if (
            self._smooth_scroll_state
            and self._smooth_scroll_state["node_id"] == scroll_id
            and self._smooth_scroll_state["axis"] == axis
        ) else None
        prior_target = prior["target"] if prior else current_offset
        prior_direction = (
            1 if prior and prior_target > current_offset
            else -1 if prior and prior_target < current_offset
            else 0
        )
        changing_direction = bool(prior) and prior_direction != 0 and direction != prior_direction
        base_target = current_offset if changing_direction else prior_target

        amount = view * fraction * direction
        min_offset = view - content
        new_target = max(min_offset, min(0, base_target + amount))

        if new_target == base_target and not prior:
            return

        setattr(scroll_data, view_attr, view)
        setattr(scroll_data, max_attr, content)
        # Keep target_offset_{y,x} in sync so a follow-up wheel/scrollbar
        # interaction starts from the new position instead of jumping back
        # to the pre-button-click target.
        setattr(scroll_data, target_attr, new_target)
        node.tree._scrollbar_show(scroll_id)

        self._smooth_scroll_state = {
            "tree": node.tree,
            "data": scroll_data,
            "node_id": scroll_id,
            "axis": axis,
            "target": new_target,
        }
        if not self._smooth_scroll_job:
            self._smooth_scroll_job = cron.interval("16ms", self._smooth_scroll_tick)

    def _smooth_scroll_tick(self):
        s = self._smooth_scroll_state
        if not s:
            self._smooth_scroll_stop()
            return
        tree, data, node_id, axis = s["tree"], s["data"], s["node_id"], s["axis"]
        if tree.destroying or node_id not in tree.meta_state.scrollable:
            self._smooth_scroll_stop()
            return

        offset_attr = "offset_y" if axis == "y" else "offset_x"
        current = getattr(data, offset_attr)
        delta = s["target"] - current
        if abs(delta) <= 1.0:
            setattr(data, offset_attr, s["target"])
            tree.render_manager.render_scroll()
            self._smooth_scroll_stop()
            return
        setattr(data, offset_attr, current + delta * 0.25)
        tree.render_manager.render_scroll()

    def _smooth_scroll_stop(self):
        if self._smooth_scroll_job:
            cron.cancel(self._smooth_scroll_job)
            self._smooth_scroll_job = None
        self._smooth_scroll_state = None

    def scroll_to_key(self, id: str, key: str):
        """Scroll a data_table so the row with the given key is visible."""
        node = store.id_to_node.get(id)
        if not node or not hasattr(node, 'scroll_to_key'):
            return
        if node.scroll_to_key(key):
            node.tree.render_manager.queue_render(RenderTaskScrolling)

    def scroll_to_id(self, target_id: str, focus: bool = True):
        """Scroll the nearest scrollable ancestor so that the target element is visible, and optionally focus it."""
        target_node = store.id_to_node.get(target_id)
        if not target_node or not target_node.box_model:
            return

        # Walk up to find nearest scrollable ancestor
        scrollable_node = target_node.parent_node
        scroll_data = None
        while scrollable_node:
            if scrollable_node.properties.is_scrollable() and scrollable_node.id:
                scroll_data = scrollable_node.tree.meta_state.scrollable.get(scrollable_node.id)
                if scroll_data:
                    break
            scrollable_node = scrollable_node.parent_node

        if not scrollable_node or not scroll_data:
            # No scrollable ancestor, but still focus if requested
            if focus and target_node.interactive:
                self.focus_node(target_node)
            return

        # Child's position relative to scrollable content (undo rendered scroll offset)
        child_y = target_node.box_model.margin_pos.y - scrollable_node.box_model.padding_pos.y - scroll_data.rendered_offset_y
        child_height = target_node.box_model.margin_size.height

        # Check if already fully visible
        visible_top = -scroll_data.rendered_offset_y
        visible_bottom = visible_top + scroll_data.view_height
        already_visible = child_y >= visible_top and child_y + child_height <= visible_bottom

        if not already_visible:
            # Scroll so child is near the top with a small margin
            new_offset_y = -child_y + 8
            min_offset_y = min(0, scroll_data.view_height - scroll_data.max_height)
            new_offset_y = max(min_offset_y, min(0, new_offset_y))

            if scroll_data.offset_y != new_offset_y:
                scroll_data.offset_y = new_offset_y
                scroll_data.target_offset_y = new_offset_y
                scrollable_node.tree._scrollbar_show(scrollable_node.id)
                scrollable_node.tree.render_manager.queue_render(RenderTaskScrolling)

        if focus and target_node.interactive:
            self.focus_node(target_node)

    def increment_ref_count_nodes(self):
        store.ref_count_nodes += 1

    def decrement_ref_count_nodes(self):
        store.ref_count_nodes -= 1

    def get_ref_count_nodes(self):
        return store.ref_count_nodes

    def increment_ref_count_trees(self):
        store.ref_count_trees += 1

    def decrement_ref_count_trees(self):
        store.ref_count_trees -= 1

    def get_ref_count_trees(self):
        return store.ref_count_trees

    def get_components(self):
        components = {}
        for tree in store.trees:
            components[tree.guid] = tree.meta_state.components
        return components

    def toggle_hints(self, enabled: bool):
        if isinstance(enabled, bool):
            for tree in store.trees:
                tree.show_hints = enabled
        else:
            for tree in store.trees:
                tree.show_hints = not tree.show_hints

    def clear_state(self):
        store.reactive_state.clear()
        store.processing_states.clear()
        store.reset_mouse_state()
        state_coordinator.reset()
        store.mouse_state['disable_events'] = False

    def clear_state_for_tree(self, tree: TreeType):
        from ..platform.custom_input import custom_input_manager
        for node in tree.interactive_node_list:
            if node.element_type in ("input_text", "textarea"):
                custom_input_manager.remove_input(node.id)
        for state_key in tree.meta_state.states:
            if state_key in store.reactive_state:
                del store.reactive_state[state_key]
            if state_key in store.processing_states:
                store.processing_states.remove(state_key)
        # Clean up per-tree component stack
        if tree in store.processing_components:
            del store.processing_components[tree]
        if not store.processing_states or not store.trees:
            state_coordinator.reset()

    def clear_tree(self, tree: TreeType):
        if tree in store.trees:
            store.root_nodes = [node for node in store.root_nodes if node.tree != tree]
            store.trees.remove(tree)
            self.clear_state_for_tree(tree)
            store.synchronize_ids()
        store.mouse_state['disable_events'] = False
        if not store.trees:
            from .. import fonts
            fonts.reset_font_state()

    def clear_all(self):
        from .. import fonts
        from ..platform.custom_input import custom_input_manager
        custom_input_manager.remove_all()
        store.clear()
        state_coordinator.reset()
        fonts.reset_font_state()

    def deprecated_event_register_on_lifecycle(self, callback):
        if callback not in _deprecated_event_subscribers:
            _deprecated_event_subscribers.append(callback)

    def deprecated_event_unregister_on_lifecycle(self, callback):
        if callback in _deprecated_event_subscribers:
            _deprecated_event_subscribers.remove(callback)

    def deprecated_event_fire_on_lifecycle(self, event: DeprecatedLifecycleEvent):
        for callback in _deprecated_event_subscribers:
            callback(event)

    def deprecated_event_fire_on_mount(self, tree):
        self.deprecated_event_fire_on_lifecycle(DeprecatedLifecycleEvent("mount", tree))

    def deprecated_event_fire_on_unmount(self, tree):
        self.deprecated_event_fire_on_lifecycle(DeprecatedLifecycleEvent("unmount", tree))

state_manager = StateManager()

def debug_gc():
    gc.collect()
    print("gc actual nodes:", state_manager.get_ref_count_nodes())
    print("gc actual trees:", state_manager.get_ref_count_trees())
    print("Store nodes with ids:", len(store.id_to_node.keys()))
    print("Store trees:", len(store.trees))
    print("Store focused_tree", store.focused_tree)
    print("Store processing_tree_stack", store.processing_tree_stack)
    print("Store processing_states", store.processing_states)
    print("Store root_nodes", store.root_nodes)
    print("Store id_to_node", store.id_to_node)
    print("Store reactive_state", store.reactive_state)
    print("Store staged_effects", store.staged_effects)