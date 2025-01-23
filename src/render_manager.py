
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from talon import cron
from typing import Any
from .interfaces import TreeType, RenderTaskType, RenderManagerType

class RenderCause(Enum):
    STATE_CHANGE = "STATE_CHANGE"
    REF_CHANGE = "REF_CHANGE"
    DRAG_END = "DRAG_END"
    DRAGGING = "DRAGGING"
    TEXT_MUTATION = "TEXT_MUTATION"
    HIGHLIGHT_CHANGE = "HIGHLIGHT_CHANGE"
    FOCUS_CHANGE = "FOCUS_CHANGE"

@dataclass
class RenderTask(RenderTaskType):
    cause: RenderCause
    on_render: callable
    args: list[object] = field(default_factory=list)

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

RenderTaskDragEnd = RenderTask(
    RenderCause.DRAG_END,
    on_base_canvas_change,
)

class RenderManager(RenderManagerType):
    def __init__(self, tree: TreeType):
        self.queue = deque()
        self.current_render_task = None
        self.tree = tree
        self._render_debounce_job = None
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
                render_task.on_render(self.tree, *render_task.args)
            else:
                self.queue.append(render_task)

    def _queue_render_after_debounce(self, interval: str, render_task: RenderTask):
        if self._render_debounce_job:
            cron.cancel(self._render_debounce_job)

        self._render_debounce_job = cron.after(
            interval,
            lambda: self._queue_render_after_debounce_execute(render_task)
        )

    def _queue_render_after_debounce_execute(self, render_task: RenderTask):
        self.queue_render(render_task)
        self._render_debounce_job = None

    def process_next_render(self):
        if not self._destroying and self.queue:
            self.current_render_task = self.queue.popleft()
            self.current_render_task.on_render(self.tree, *self.current_render_task.args)

    def finish_current_render(self):
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
            RenderCause.STATE_CHANGE,
            on_full_render,
            [props, on_mount, on_unmount, show_hints],
        )

        self.queue_render(render_task)

    def render_text_mutation(self):
        if self.tree.canvas_decorator:
            self.queue_render(RenderTaskTextMutation)

    def render_ref_change(self):
        self._queue_render_after_debounce("1ms", RenderTaskRefChange)

    def render_drag_end(self):
        self.queue_render(RenderTaskDragEnd)

    def prepare_destroy(self):
        self._destroying = True

    def destroy(self):
        if self._render_debounce_job:
            cron.cancel(self._render_debounce_job)
        self._render_debounce_job = None
        self.queue.clear()
        self.current_render_task = None
        self.tree = None
