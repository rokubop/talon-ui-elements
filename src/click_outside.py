from talon import cron, ctrl
from talon.types import Point2d

# A click that lands outside a window never reaches ui_elements: mouse events
# only arrive through the blocking canvases sized to the window's own rect
# (see Tree.draw_blockable_canvases). A full-screen canvas is not an option
# either - one with blocks_mouse=False receives no events at all, and one with
# blocks_mouse=True would swallow the click before the app underneath sees it,
# which is exactly wrong for an overlay sitting on top of a game.
#
# So we poll the global button state instead. Measured on Windows: physical
# click holds run 65-96ms, so a 16ms poll samples each click 4-6 times. The
# poll runs only while at least one tree is watching, and reads global
# coordinates, so it works across every display rather than one screen's
# canvas.
POLL_INTERVAL = "16ms"


class ClickOutsideWatcher:
    """Detects mouse-button presses anywhere on screen and reports the global
    position to each registered watcher, which decides whether that position
    counts as 'outside' for its own nodes."""

    def __init__(self):
        self._watchers = {}
        self._job = None
        self._prev_down = set()
        self._armed = False

    def watch(self, key: str, callback: callable):
        is_first = not self._watchers
        self._watchers[key] = callback
        if is_first:
            self._start()

    def unwatch(self, key: str):
        self._watchers.pop(key, None)
        if not self._watchers:
            self._stop()

    def _start(self):
        self._prev_down = self._buttons_down()
        # A button already held when we start belongs to whatever opened the
        # window - don't let it immediately close what it just opened. Wait
        # for a clean release before treating presses as click-outside.
        self._armed = not self._prev_down
        if not self._job:
            self._job = cron.interval(POLL_INTERVAL, self._tick)

    def _stop(self):
        if self._job:
            cron.cancel(self._job)
            self._job = None
        self._prev_down = set()
        self._armed = False

    def _buttons_down(self):
        try:
            return set(ctrl.mouse_buttons_down() or ())
        except Exception:
            return set()

    def _tick(self):
        down = self._buttons_down()
        prev, self._prev_down = self._prev_down, down

        if not self._armed:
            if not down:
                self._armed = True
            return

        if not down - prev:
            return

        try:
            x, y = ctrl.mouse_pos()
        except Exception:
            return

        gpos = Point2d(x, y)
        for key, callback in list(self._watchers.items()):
            try:
                callback(gpos)
            except Exception as e:
                print(f"talon_ui_elements click outside error ({key}): {e}")


click_outside_watcher = ClickOutsideWatcher()
