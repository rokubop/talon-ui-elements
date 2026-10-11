"""The canvas a drag previews on.

Nothing else draws on it, so a drag tick is one freeze of a few shapes rather
than a repaint of the tree.

It blocks the mouse and hands it to the tree, so a drag's mouse events come
from here: every screen, so the cursor can't leave it and nothing has to
follow it. Hidden, it blocks nothing.

Hidden between drags rather than closed, since a drag starting is the worst
time to pay for building a canvas. It closes with the tree.
"""

import time

from talon import cron
from talon.skia.canvas import Canvas as SkiaCanvas

from ..constants import DRAG_OVERLAY_MIN_FRAME_MS, DRAG_OVERLAY_STALL_MS
from .shapes import draw_shapes


class DragOverlay:
    def __init__(self, create_canvas: callable, on_key: callable = None,
                 on_mouse: callable = None):
        self._create_canvas = create_canvas
        self._on_key = on_key
        self._on_mouse = on_mouse
        self._canvas = None
        self._shapes = []
        self._pending = False
        self._painting = False
        self._trailing_job = None
        self._last_paint_ts = 0.0

    @property
    def is_open(self) -> bool:
        return self._canvas is not None

    def prepare(self) -> None:
        """Build it hidden, ahead of any drag. Cheap to call every render."""
        if self._canvas:
            return
        self._canvas = self._create_canvas()
        self._canvas.register("draw", self.on_draw)
        # It sits over the decorator, which owns the tree's keys.
        if self._on_key:
            self._canvas.register("key", self._on_key)
        if self._on_mouse:
            self._canvas.blocks_mouse = True
            self._canvas.register("mouse", self._on_mouse)
        self._hide()

    def open(self) -> None:
        self.prepare()
        try:
            self._canvas.show()
        except Exception as e:
            print(f"ui_elements: error showing drag overlay: {e}")
        # It blocks the mouse everywhere, so anything above it would keep
        # the mouseup that ends the drag.
        self.raise_to_top()

    def close(self) -> None:
        """End of a drag. The canvas stays, emptied and hidden."""
        self._cancel_trailing()
        self._shapes = []
        self._pending = False
        self._painting = False
        self._hide()

    def destroy(self) -> None:
        """End of the tree."""
        self.close()
        if self._canvas:
            try:
                self._canvas.unregister("draw", self.on_draw)
                if self._on_key:
                    self._canvas.unregister("key", self._on_key)
                if self._on_mouse:
                    self._canvas.unregister("mouse", self._on_mouse)
                self._canvas.close()
            except Exception as e:
                print(f"ui_elements: error closing drag overlay: {e}")
            self._canvas = None

    def _hide(self) -> None:
        if self._canvas:
            try:
                self._canvas.hide()
            except Exception as e:
                print(f"ui_elements: error hiding drag overlay: {e}")

    def set_shapes(self, shapes) -> None:
        self._shapes = shapes or []
        self._request_paint()

    def raise_to_top(self) -> None:
        if self._canvas:
            try:
                self._canvas.focused = True
            except Exception:
                pass

    def on_draw(self, canvas: SkiaCanvas) -> None:
        try:
            draw_shapes(canvas, self._shapes)
        except Exception as e:
            print(f"ui_elements: drag overlay draw error: {e}")
        finally:
            self._painting = False
            if self._pending:
                self._pending = False
                self._request_paint()

    def _request_paint(self) -> None:
        """One freeze per displayed frame, and never two in flight.

        A mouse can report faster than the display refreshes. Without the
        latch every report would queue a freeze and the outline would run
        a growing number of frames behind the cursor.
        """
        if not self._canvas:
            return

        elapsed_ms = (time.monotonic() - self._last_paint_ts) * 1000
        if self._painting:
            # A freeze that never draws would strand the outline.
            if elapsed_ms < DRAG_OVERLAY_STALL_MS:
                self._pending = True
                return
        elif elapsed_ms < DRAG_OVERLAY_MIN_FRAME_MS:
            self._schedule_trailing(DRAG_OVERLAY_MIN_FRAME_MS - elapsed_ms)
            return

        self._paint_now()

    def _paint_now(self) -> None:
        self._cancel_trailing()
        self._last_paint_ts = time.monotonic()
        self._painting = True
        try:
            self._canvas.freeze()
        except Exception as e:
            self._painting = False
            print(f"ui_elements: drag overlay freeze error: {e}")

    def _schedule_trailing(self, delay_ms: float) -> None:
        """The last report of a flick has to land, or the outline stops short."""
        if self._trailing_job:
            return
        delay = max(1, int(delay_ms) + 1)
        self._trailing_job = cron.after(f"{delay}ms", self._on_trailing_job)

    def _on_trailing_job(self) -> None:
        self._trailing_job = None
        if self._canvas and not self._painting:
            self._paint_now()

    def _cancel_trailing(self) -> None:
        if self._trailing_job:
            cron.cancel(self._trailing_job)
            self._trailing_job = None
