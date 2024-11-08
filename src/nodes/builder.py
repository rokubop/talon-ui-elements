from talon import cron
from talon.skia.canvas import Canvas as SkiaCanvas
from talon.canvas import Canvas
from talon.skia import RoundRect
from talon.types import Rect, Point2d
from .node import Node
from .container import UIContainer
from ..state import state
from ..utils import get_screen, canvas_from_screen, draw_text_simple
from ..core.cursor import Cursor
from ..options import UIOptionsDict, UIOptions
from typing import Literal
import uuid
import hashlib
import pickle

RootElementType = Literal['screen', 'window']

class UIBuilder(UIContainer):
    def __init__(self, element_type: RootElementType, options: UIOptions):
        super().__init__(
            element_type=element_type,
            options=options,
        )
        screen_index = options.screen
        screen = get_screen(screen_index)
        self.screen_index = screen_index
        self.cursor = Cursor(screen)

        state.builders[self.guid] = self
        state.nodes[self.guid] = self

        self.static_canvas = None
        self.dynamic_canvas = None
        self.highlight_canvas = None
        self.blockable_canvases = []
        self.is_blockable_canvas_init = False

        self.unhighlight_jobs = {}
        self.highlight_color = options.highlight_color

        self.scroll_y = 0
        self.hash = None

        self.update = self.show
        self.updater = None
        self.window = None
        self.is_mounted = False
        self.render_busy = False

        if not self.id:
            self.id = uuid.uuid4()

        # if updaters.get(self.id):
        #     self.set_updater(updaters[self.id])

    # TODO
    # def reset(self, **options: UIOptionsDict):
    #     self.__init__(**options)

    # def set_updater(self, updater):
    #     global updaters
    #     # this is for if we need a wrapper to contain state and
    #     # conditionals for dynamic elements
    #     self.updater = updater
    #     updaters[self.id] = updater

    #     def new_update():
    #         pass
    #         # global updating_builder_id
    #         # updating_builder_id = self.id
    #         # getattr(builders[self.id], "hide", lambda: None)(destroy=False)
    #         # builder = self.updater()
    #         # builder.show()

    #     self.update = new_update

    def on_draw_static(self, c: SkiaCanvas):
        screen = get_screen(self.screen_index)
        self.cursor = Cursor(screen)
        self.virtual_render(c, self.cursor)
        self.render(c, self.cursor)

        if not self.dynamic_canvas:
            screen = get_screen(self.screen_index)
            self.dynamic_canvas = canvas_from_screen(screen)
            self.dynamic_canvas.register("draw", self.on_draw_dynamic)

            self.highlight_canvas = canvas_from_screen(screen)
            self.highlight_canvas.register("draw", self.on_draw_highlight)
            self.highlight_canvas.freeze()

        # dynamic canvas depends on static canvas first
        self.dynamic_canvas.freeze()

    def on_draw_dynamic(self, c: SkiaCanvas):
        global state
        # for node in state.get_builder_text_nodes(self.id):
            # options = node["options"]
            # cursor = node["cursor"]

            # has_scroll_region = node["scroll_region_key"] and node["scroll_region_key"] in scrollable_regions
            # if has_scroll_region:
            #     c.save()
            #     c.clip_rect(scrollable_regions[node["scroll_region_key"]]["scroll_box_rect"])

            # draw_text_simple(c, state["text"][id], options, cursor["x"], cursor["y"])

            # if has_scroll_region:
            #     c.restore()

        # self.update_blockable_canvases_debounced()
        self.on_fully_rendered()
        self.render_busy = False

    def update_blockable_canvases(self):
        pass
        # global debounce_blockable_canvas

        # if drag_active:
        #     return

        # if self.window and self.window.offset_dirty:
        #     self.window.offset_dirty = False
        #     self.clear_blockable_canvases()

        # if not self.blockable_canvases:
        #     self.init_blockable_canvases()

        # debounce_blockable_canvas = None

    def update_blockable_canvases_debounced(self):
        global debounce_blockable_canvas

        if debounce_blockable_canvas:
            cron.cancel(debounce_blockable_canvas)

        debounce_blockable_canvas = cron.after("100ms", self.update_blockable_canvases)

    def on_fully_rendered(self):
        global current_builder_id_render, updating_builder_id
        if not self.is_mounted:
            self.is_mounted = True

            if self.on_mount:
                self.on_mount()

            current_builder_id_render = None
            updating_builder_id = None

            # cron.after("10ms", lambda: event_fire_on_mount(self.id))

    def on_draw_highlight(self, c: SkiaCanvas):
        pass
        # global state

        # for node in state.get_builder_highlighted_nodes(self.id):
        #     box_model = node.box_model
        #     c.paint.color = state["highlighted"][id]
        #     c.paint.style = c.paint.Style.FILL

        #     has_scroll_region = ids[id]["scroll_region_key"] and ids[id]["scroll_region_key"] in scrollable_regions
        #     if has_scroll_region:
        #         c.save()
        #         c.clip_rect(scrollable_regions[ids[id]["scroll_region_key"]]["scroll_box_rect"])

        #     if 'options' in ids[id] and hasattr(ids[id]['options'], 'border_radius'):
        #         border_radius = ids[id]['options'].border_radius
        #         c.draw_rrect(RoundRect.from_rect(box_model.padding_rect, x=border_radius, y=border_radius))
        #     else:
        #         c.draw_rect(box_model.padding_rect)

        #     if has_scroll_region:
        #         c.restore()

    def clear_blockable_canvases(self):
        if self.blockable_canvases:
            for canvas in self.blockable_canvases:
                canvas.unregister("mouse", self.on_mouse)
                canvas.unregister("mouse", self.on_scroll)
                canvas.hide()
                canvas.close()
            self.blockable_canvases = []
            self.is_blockable_canvas_init = False

    def init_blockable_canvases(self):
        """
        If we have at least one button or input, then we will consider the whole content area as blockable.
        If we have an inputs, then everything should be blockable except for those inputs.
        """

        if buttons or inputs:
            full_rect = self.box_model.content_children_rect
            if self.window and self.window.offset:
                full_rect.x += self.window.offset.x
                full_rect.y += self.window.offset.y

                for input in list(inputs.values()):
                    input.rect.x += self.window.offset.x
                    input.rect.y += self.window.offset.y

            if inputs:
                bottom_rect = None
                for input in list(inputs.values()):
                    current_rect = bottom_rect or full_rect

                    top_rect = Rect(current_rect.x, current_rect.y, current_rect.width, input.rect.y - current_rect.y)
                    self.blockable_canvases.append(Canvas.from_rect(top_rect))

                    left_rect = Rect(current_rect.x, input.rect.y, input.rect.x - current_rect.x, input.rect.height)
                    self.blockable_canvases.append(Canvas.from_rect(left_rect))

                    right_rect = Rect(input.rect.x + input.rect.width, input.rect.y, current_rect.x + current_rect.width - input.rect.x - input.rect.width, input.rect.height)
                    self.blockable_canvases.append(Canvas.from_rect(right_rect))

                    bottom_rect = Rect(current_rect.x, input.rect.y + input.rect.height, current_rect.width, current_rect.y + current_rect.height - input.rect.y - input.rect.height)
                self.blockable_canvases.append(Canvas.from_rect(bottom_rect))
            else:
                self.blockable_canvases = [Canvas.from_rect(full_rect)]

            for blockable_canvas in self.blockable_canvases:
                blockable_canvas.blocks_mouse = True
                blockable_canvas.register("mouse", self.on_mouse)
                # blockable_canvas.register("scroll", self.on_scroll)
                blockable_canvas.freeze()

        self.is_blockable_canvas_init = True

    def generate_hash_from_tree(self):
        def collect_options_and_children(obj):
            tree = {}

            if hasattr(obj, 'options'):
                tree['options'] = {k: v for k, v in vars(obj.options).items() if not callable(v)}

            if hasattr(obj, 'children'):
                tree['children'] = [
                    collect_options_and_children(child) for child in obj.children
                ]

            return tree

        state_to_serialize = collect_options_and_children(self)
        serialized_self = pickle.dumps(state_to_serialize)
        self.hash = hashlib.md5(serialized_self).hexdigest()

    def hash_and_prevent_duplicate_render(self):
        global hash_id_map
        self.generate_hash_from_tree()

        for node in state.builders.values():
            if node.hash == self.hash:
                node.hide(destroy=False)

    def show(self, on_mount: callable = None):
        global state, debug_current_step, render_step, debug_start_step, debug_draw_step_by_step, unique_key, current_builder_id_render
        unique_key = 0

        self.hash_and_prevent_duplicate_render()

        screen = get_screen(self.screen_index)

        current_builder_id_render = self.id
        # if state["user_pending"]:
        #     for state_value in state["user_pending"]:
        #         state_value.append_target(self.id)
        #     state["user_pending"].clear()

        # if debug_draw_step_by_step:
        #     if self.static_canvas:
        #         render_step = 0
        #         debug_current_step += 1

        #     else:
        #         render_step = 0
        #         debug_current_step = debug_start_step

        if self.static_canvas:
            self.cursor = Cursor(screen)
            self.static_canvas.freeze()
            # self.highlight_canvas.freeze()
            # for canvas in self.blockable_canvases:
            #     canvas.freeze()
        else:
            self.is_mounted = False
            self.on_mount = on_mount

            self.static_canvas = canvas_from_screen(screen)
            self.static_canvas.register("draw", self.on_draw_static)

            # FLOW:
            # 1. self.static_canvas.freeze() -> self.on_draw_static() ->
            # 2. self.dynamic_canvas.freeze() -> self.on_draw_dynamic() ->
            # 4. self.on_fully_rendered() -> self.is_mounted = True ->
            # 5. setup blockable canvases and fire on mounted events
            # Other: highlight_canvas triggered manually
            self.static_canvas.freeze()

    def on_hover_button(self, gpos):
        pass
        # for id, button in list(buttons.items()):
        #     if button["builder_id"] == self.id:
        #         rect = ids[id]["box_model"].padding_rect
        #         hovering = rect.contains(gpos)
        #         if state["highlighted"].get(id) != hovering:
        #             if hovering:
        #                 self.highlight(id)
        #             else:
        #                 self.unhighlight(id)

    def on_click_button(self, gpos):
        pass
        # found_button = False
        # for id, button in list(buttons.items()):
        #     if button["builder_id"] == self.id:
        #         rect = ids[id]["box_model"].padding_rect
        #         if rect.contains(gpos):
        #             button["on_click"]()
        #             found_button = True
        #             break
        # return found_button

    def on_mouse_window(self, e):
        pass
        # global drag_relative_offset, drag_active, drag_start_pos

        # if e.button == 0:
        #     if e.event == "mousedown" and not drag_relative_offset:
        #         drag_start_pos = e.gpos
        #         drag_relative_offset = Point2d(e.gpos.x - self.window.offset.x, e.gpos.y - self.window.offset.y)
        #         drag_active = True
        #     elif e.event == "mouseup":
        #         drag_active = False
        #         drag_start_pos = None
        #         drag_relative_offset = None

        # if e.event == "mousemove" and drag_relative_offset:
        #     if not drag_active:
        #         if abs(e.gpos.x - drag_start_pos.x) > drag_init_threshold or abs(e.gpos.y - drag_start_pos.y) > drag_init_threshold:
        #             drag_active = True

        #     if drag_active and self.window and self.static_canvas:
        #         self.window.offset.x = e.gpos.x - drag_relative_offset.x
        #         self.window.offset.y = e.gpos.y - drag_relative_offset.y
        #         self.window.offset_dirty = True

        #         self.freeze_if_not_busy()

    def on_mouse(self, e):
        pass
        # found_clickable = False
        # if e.event == "mousemove":
        #     self.on_hover_button(e.gpos)
        # elif e.event == "mousedown":
        #     found_clickable = self.on_click_button(e.gpos)

        # if not found_clickable and self.window:
        #     self.on_mouse_window(e)

    # def on_scroll_tick(self, e):
    #     smallest_region = None
    #     if scrollable_regions:
    #         for region in list(scrollable_regions.values()):
    #             if region["scroll_box_rect"].contains(e.gpos):
    #                 smallest_region = region if not smallest_region or region["scroll_box_rect"].height < smallest_region["scroll_box_rect"].height else smallest_region

    #         if smallest_region:
    #             if e.degrees.y > 0:
    #                 smallest_region["on_scroll_y"](-scroll_amount_per_tick)
    #             elif e.degrees.y < 0:
    #                 smallest_region["on_scroll_y"](scroll_amount_per_tick)

    #         self.static_canvas.freeze()

    # def on_scroll(self, e):
    #     global scroll_throttle_job
    #     if not scroll_throttle_job:
    #         self.on_scroll_tick(e)
    #         scroll_throttle_job = cron.after(scroll_throttle_time, scroll_throttle_clear)

    def get_ids(self):
        return ids

    def set_text(self, id: str, text: str):
        global state

        # state["text"][id] = text
        # if self.dynamic_canvas:
        #     self.dynamic_canvas.freeze()

    def highlight(self, id: str, color: str = None):
        global state
        # if id in ids:
        #     state["highlighted"][id] = color or self.highlight_color or "FFFFFF88"
        #     self.highlight_canvas.freeze()

    def unhighlight(self, id: str):
        global state
        # if id in ids and id in state["highlighted"]:
        #     state["highlighted"].pop(id)

        #     if self.unhighlight_jobs.get(id):
        #         cron.cancel(self.unhighlight_jobs[id][0])
        #         self.unhighlight_jobs[id][1]()
        #         self.unhighlight_jobs[id] = None

        #     self.highlight_canvas.freeze()

    def highlight_briefly(self, id: str, color: str = None, duration: int = 150):
        pass
        # if id in ids:
        #     self.highlight(id, color)
        #     pending_unhighlight = lambda: self.unhighlight(id)
        #     self.unhighlight_jobs[id] = (cron.after(f"{duration}ms", pending_unhighlight), pending_unhighlight)

    def freeze_if_not_busy(self):
        if not self.render_busy:
            self.render_busy = True
            self.static_canvas.freeze()

    def hide(self, destroy=True):
        """Hide and destroy the UI builder."""
        global ids, state, buttons, inputs, unique_key

        # event_fire_on_unmount(self.id)
        self.is_mounted = False

        if self.static_canvas:
            self.static_canvas.unregister("draw", self.on_draw_static)

            if destroy:
                self.static_canvas.hide()
                self.static_canvas.close()
                self.static_canvas = None

        if self.dynamic_canvas:
            self.dynamic_canvas.unregister("draw", self.on_draw_dynamic)
            if destroy:
                self.dynamic_canvas.hide()
                self.dynamic_canvas.close()
                self.dynamic_canvas = None

        if self.highlight_canvas:
            self.highlight_canvas.unregister("draw", self.on_draw_highlight)
            if destroy:
                self.highlight_canvas.hide()
                self.highlight_canvas.close()
                self.highlight_canvas = None

        if self.blockable_canvases:
            for canvas in self.blockable_canvases:
                canvas.unregister("mouse", self.on_mouse)
                # canvas.unregister("mouse", self.on_scroll)
                canvas.hide()
                canvas.close()
            self.blockable_canvases = []
            self.is_blockable_canvas_init = False

        # for id in list(inputs):
        #     inputs[id].hide()

        if destroy:
            # remove_ids = [id for id in ids if ids[id]["builder_id"] == self.id]

            # for id in remove_ids:
            #     state["highlighted"].pop(id, None)
            #     state["text"].pop(id, None)
            #     ids.pop(id, None)

            # clean_state(self.id)
            # state.builders.pop(self.guid, None)
            # state.nodes.pop(self.guid, None)
            # pass
            # builders.pop(self.id, None)
            # hash_id_map.pop(self.hash, None)
            self.hash = None
            # updaters.pop(self.id, None)
            self.window = None
            self.destroy()

        # for id in list(buttons):
        #     if id in state["text"]:
        #         state["text"].pop(id, None)

        # buttons.clear()
        # inputs.clear()
        # scrollable_regions.clear()
        unique_key = 0