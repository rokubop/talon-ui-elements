"""The canvas a drag previews on.

Nothing else draws on it. While a preview drag is held the base and decorator
canvases keep the paint they had at drag start, so a tick is one freeze and a
handful of shapes instead of a repaint of the tree.
"""

import time

from talon import cron
from talon.skia.canvas import Canvas as SkiaCanvas

from ..constants import DRAG_OVERLAY_MIN_FRAME_MS, DRAG_OVERLAY_STALL_MS
from .shapes import draw_shapes


class DragOverlay:
    def __init__(self, create_canvas: callable, on_key: callable = None):
        self._create_canvas = create_canvas
        self._on_key = on_key
        self._canvas = None
        self._shapes = []
        self._pending = False
        self._painting = False
        self._trailing_job = None
        self._last_paint_ts = 0.0

    @property
    def is_open(self) -> bool:
        return self._canvas is not None

    def open(self) -> None:
        if self._canvas:
            return
        self._canvas = self._create_canvas()
        self._canvas.register("draw", self.on_draw)
        # The overlay is raised over the decorator, which owns the tree's key
        # handler, so it has to answer for keys itself while it is up.
        if self._on_key:
            self._canvas.register("key", self._on_key)

    def close(self) -> None:
        self._cancel_trailing()
        self._shapes = []
        self._pending = False
        self._painting = False
        if self._canvas:
            try:
                self._canvas.unregister("draw", self.on_draw)
                if self._on_key:
                    self._canvas.unregister("key", self._on_key)
                self._canvas.close()
            except Exception as e:
                print(f"ui_elements: error closing drag overlay: {e}")
            self._canvas = None

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
            # A freeze that never draws would otherwise strand the outline
            # for the rest of the drag.
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
