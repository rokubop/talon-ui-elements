
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from talon import cron
from typing import Any
from ..interfaces import TreeType, RenderTaskType, RenderManagerType, Point2d

class RenderCause(Enum):
    SCROLLING = "SCROLLING"
    STATE_CHANGE = "STATE_CHANGE"
    REF_CHANGE = "REF_CHANGE"
    DRAG_START = "DRAG_START"
    DRAG_END = "DRAG_END"
    DRAGGING = "DRAGGING"
    TEXT_MUTATION = "TEXT_MUTATION"
    HIGHLIGHT_CHANGE = "HIGHLIGHT_CHANGE"
    MOUSE_HIGHLIGHT = "MOUSE_HIGHLIGHT"
    FOCUS_CHANGE = "FOCUS_CHANGE"
    REQUEST_ANIMATION_FRAME = "REQUEST_ANIMATION_FRAME"

class Policy(Enum):
    TAKE_LATEST = "take_latest"
    TAKE_FIRST = "take_first"
    TAKE_ALL = "take_all"
    THROTTLE = "throttle"
    DEBOUNCE = "debounce"

class RenderTask(RenderTaskType):
    def __init__(
        self,
        cause: RenderCause,
        on_start: callable,
        on_end: callable = None,
        args: list[object] = None,
        metadata: dict[str, Any] = None,
        group: str = None,
        policy: Policy = Policy.TAKE_LATEST,
    ):
        self.running = False
        self.cause = cause
        self.on_start = on_start
        self.on_end = on_end
        self.args = args if args is not None else []
        self.group = group if group is not None else cause
        self.policy = policy
        self.metadata = metadata if metadata is not None else {}

    def start(self):
        self.running = True
        if self.on_start:
            self.on_start(*self.args)

def on_base_canvas_change(tree: TreeType):
    tree.render_base_canvas()

def on_decorator_canvas_change(tree: TreeType):
    tree.canvas_decorator.freeze()

def on_full_render(tree: TreeType, *args):
    tree.render(*args)

RenderTaskTextMutation = RenderTask(
    RenderCause.TEXT_MUTATION,
    on_decorator_canvas_change,
)

RenderTaskRefChange = RenderTask(
    RenderCause.REF_CHANGE,
    on_full_render,
)

RenderTaskScrolling = RenderTask(
    RenderCause.SCROLLING,
    on_base_canvas_change,
)

RenderTaskDragStart = RenderTask(
    RenderCause.DRAG_START,
    on_base_canvas_change,
)

RenderTaskDragEnd = RenderTask(
    RenderCause.DRAG_END,
    on_base_canvas_change,
)

RenderStateChange = RenderTask(
    RenderCause.STATE_CHANGE,
    on_full_render,
)

RenderMouseHighlight = RenderTask(
    RenderCause.MOUSE_HIGHLIGHT,
    on_decorator_canvas_change,
)

@dataclass
class RenderCallbackEvent:
    tree: TreeType = None
    cause: RenderCause = None
    args: list[object] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

class RenderManager(RenderManagerType):
    def __init__(self, tree: TreeType):
        self.queue = deque()
        self.current_render_task = None
        self.tree = tree
        self._render_debounce_job = None
        self._render_throttle_job = None
        self._destroying = False

    @property
    def render_cause(self):
        return self.current_render_task.cause if self.current_render_task else None

    @property
    def is_rendering(self):
        return self.current_render_task is not None

    @property
    def is_destroying(self):
        return self._destroying

    def queue_render(self, render_task: RenderTask):
        if not self._destroying:
            if not self.current_render_task:
                self.current_render_task = render_task
                render_task.on_start(self.tree, *render_task.args)
            else:
                self.queue.append(render_task)

    def is_dragging(self):
        return self.current_render_task and \
            self.current_render_task.cause == RenderCause.DRAGGING

    def is_drag_end(self):
        return self.current_render_task and \
            self.current_render_task.cause == RenderCause.DRAG_END

    def is_drag_start(self):
        return self.current_render_task and \
            self.current_render_task.cause == RenderCause.DRAG_START

    def is_scrolling(self):
        return self.current_render_task and \
            self.current_render_task.cause == RenderCause.SCROLLING

    def _queue_render_after_debounce(self, interval: str, render_task: RenderTask):
        if self._render_debounce_job:
            cron.cancel(self._render_debounce_job)

        self._render_debounce_job = cron.after(
            interval,
            lambda: self._queue_render_after_debounce_execute(render_task)
        )

    def clear_throttle(self):
        self._render_throttle_job = None

    def _render_throttle(self, interval: str, render_task: RenderTask):
        if not self._render_debounce_job and not \
                self._render_throttle_job and not \
                self.current_render_task:
            self.queue_render(render_task)
            self._render_throttle_job = cron.after(
                interval,
                self.clear_throttle
            )

    def _queue_render_after_debounce_execute(self, render_task: RenderTask):
        self.queue_render(render_task)
        self._render_debounce_job = None

    def process_next_render(self):
        if not self._destroying and self.queue:
            self.current_render_task = self.queue.popleft()
            if self.current_render_task.cause == RenderCause.REQUEST_ANIMATION_FRAME:
                self.current_render_task.on_start()
                self.process_next_render()
                return
            self.current_render_task.on_start(self.tree, *self.current_render_task.args)

    def finish_current_render(self):
        if self.current_render_task and self.current_render_task.on_end:
            # print("on_end is", self.current_render_task.on_end)
            # print("type:", type(self.current_render_task.on_end))
            self.current_render_task.on_end(RenderCallbackEvent(
                tree=self.tree,
                cause=self.current_render_task.cause,
                args=self.current_render_task.args,
                metadata=self.current_render_task.metadata,
            ))
        self.current_render_task = None
        self.process_next_render()

    def render_mount(
            self,
            props: dict[str, Any] = {},
            on_mount: callable = None,
            on_unmount: callable = None,
            show_hints: bool = None
        ):
        render_task = RenderTask(
            cause=RenderCause.STATE_CHANGE,
            on_start=on_full_render,
            args=[props, on_mount, on_unmount, show_hints],
        )

        self.queue_render(render_task)

    def render_text_mutation(self):
        if self.tree.canvas_decorator:
            self.queue_render(RenderTaskTextMutation)

    def render_ref_change(self):
        self._queue_render_after_debounce("1ms", RenderTaskRefChange)

    def render_drag_start(
        self,
        mouse_pos: Point2d,
        mousedown_start_pos: Point2d,
        mousedown_start_offset: Point2d
    ):
        render_task = RenderTask(
            cause=RenderCause.DRAG_START,
            on_start=on_base_canvas_change,
            metadata = {
                "mouse_pos": mouse_pos,
                "mousedown_start_pos": mousedown_start_pos,
                "mousedown_start_offset": mousedown_start_offset,
            }
        )
        self.queue_render(render_task)
        # self.render_dragging(offset)
        # task = RenderTask(
        #     cause=RenderCause.DRAGGING,
        #     on_start=on_base_canvas_change,
        #     props = {
        #         "offset": offset,
        #     }
        # )
        # self.queue_render(task)

    def render_drag_end(
        self,
        mouse_pos: Point2d,
        mousedown_start_pos: Point2d,
        mousedown_start_offset: Point2d,
        on_start: callable = None,
        on_end: callable = None
    ):
        render_task = RenderTask(
            cause=RenderCause.DRAG_END,
            on_start=lambda tree: (
                on_start(RenderCallbackEvent(
                    tree=tree,
                    cause=RenderCause.DRAG_END,
                )),
                on_base_canvas_change(tree)
            ),
            on_end=on_end,
            metadata = {
                "mouse_pos": mouse_pos,
                "mousedown_start_pos": mousedown_start_pos,
                "mousedown_start_offset": mousedown_start_offset,
            }
        )
        self.queue_render(render_task)

    def render_dragging(
        self,
        mouse_pos: Point2d,
        mousedown_start_pos: Point2d,
        mousedown_start_offset: Point2d
    ):
        render_task = RenderTask(
            cause=RenderCause.DRAGGING,
            on_start=on_base_canvas_change,
            metadata = {
                "mouse_pos": mouse_pos,
                "mousedown_start_pos": mousedown_start_pos,
                "mousedown_start_offset": mousedown_start_offset,
            }
        )
        self._render_throttle("10ms", render_task)

    def render_scroll(self):
        self._render_throttle("16ms", RenderTaskScrolling)

    def render_state_change(self):
        self.queue_render(RenderStateChange)

    def render_mouse_highlight(self):
        self.queue_render(RenderMouseHighlight)

    def schedule_state_change(self, on_start: callable, on_end: callable = None):
        self.queue_render(RenderTask(
            RenderCause.STATE_CHANGE,
            on_start,
            on_end,
            [],
        ))

    def request_animation_frame(self, callback: callable):
        cron.after("500ms", self.queue_render(RenderTask(
            RenderCause.REQUEST_ANIMATION_FRAME,
            callback,
        )))

    def prepare_destroy(self):
        self._destroying = True

    def destroy(self):
        if self._render_debounce_job:
            cron.cancel(self._render_debounce_job)
        if self._render_throttle_job:
            cron.cancel(self._render_throttle_job)
        self._render_debounce_job = None
        self._render_throttle_job = None
        self.queue.clear()
        self.current_render_task = None
        self.tree = None
