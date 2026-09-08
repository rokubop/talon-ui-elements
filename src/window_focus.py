"""Detecting that the ui_elements window lost focus.

Talon gives us no single dependable "the user clicked away" event, so this
module runs the candidates side by side behind
`user.ui_elements_focus_strategy` and lets one verdict fall out of them.

The candidates:

- "canvas"     Talon's own Canvas.on_focused(bool). Only the decorator canvas
               ever holds keyboard focus, so it is the one we listen on. Fires
               spuriously while we juggle our own canvases: a blockable canvas
               going up, or a decorator being recreated mid-render, both
               register as a blur followed immediately by a focus.
- "win_focus"  ui.register("win_focus"). Fires for every window the OS focuses
               anywhere. Ours iff the window's pid is Talon's. Misses the case
               where focus goes nowhere (a desktop click on some setups).
- "click"      The global button poll already used for on_click_outside. Sees
               presses that land outside every tree rect. Works even for a UI
               that never took OS focus at all, but says nothing about focus
               moving by alt-tab or a keyboard shortcut.
- "both"       canvas + win_focus. The default.
- "all"        every signal.
- "off"        none; the tree is always treated as focused.

Whatever the source, a blur signal is never committed on the spot. It waits
out BLUR_GRACE and is then checked against the OS: if a Talon window is still
active, the blur was our own canvas churn and is dropped. That grace is what
makes the noisy canvas event usable.

The passive sources (the canvas event, win_focus) stay attached whatever the
strategy is and are filtered when they fire, so switching strategy takes hold
at once. Only the click poll, which costs a 16ms cron, is attached and dropped
to match.
"""

import os
import weakref
from talon import cron, settings, ui
from talon.types import Point2d

# Long enough to swallow a blur/focus pair from our own canvas churn, short
# enough that the window visibly reacts to a real click away.
BLUR_GRACE = "120ms"

STRATEGY_SETTING = "user.ui_elements_focus_strategy"
DEFAULT_STRATEGY = "both"
VALID_STRATEGIES = ("off", "canvas", "win_focus", "click", "both", "all")


def _strategy():
    try:
        value = (settings.get(STRATEGY_SETTING) or "").strip().lower()
    except Exception:
        value = ""
    return value if value in VALID_STRATEGIES else DEFAULT_STRATEGY


def _uses(name: str) -> bool:
    strategy = _strategy()
    if strategy == "off":
        return False
    if strategy == "all":
        return True
    if strategy == "both":
        return name in ("canvas", "win_focus")
    return strategy == name


def _talon_holds_focus() -> bool:
    """Is the OS-focused window one of ours? Pid rather than app name: the
    canvases are Talon's own windows, and the name differs per platform."""
    try:
        window = ui.active_window()
    except Exception:
        return False
    if not window:
        return False
    try:
        return window.app.pid == os.getpid()
    except Exception:
        return False


class WindowFocusManager:
    """One verdict for the whole library, not one per tree. OS focus is a
    single thing - either a ui_elements canvas holds it or nothing does - and
    trees that each decided for themselves would fight over it."""

    def __init__(self):
        # Weak: store.trees owns them, and a tree that goes away without
        # reaching destroy() should not be kept alive by this.
        self._trees = weakref.WeakValueDictionary()
        self._focused = True
        self._pending_blur_job = None
        self._win_focus_cb = None
        self._strategy_cb = None
        self._click_key = "__ui_elements_window_focus__"
        self._click_watching = False

    # -- registration ---------------------------------------------------

    def watch(self, tree):
        """Called when a tree's decorator canvas comes up."""
        is_first = not self._trees
        self._trees[tree.guid] = tree
        if is_first:
            self._focused = True
        self._sync_listeners()

    def unwatch(self, tree):
        self._trees.pop(tree.guid, None)
        if not self._trees:
            self._cancel_pending()
            self._focused = True
        self._sync_listeners()

    def register_canvas(self, tree, canvas):
        """Attach the canvas 'focused' event. Separate from watch() because
        the decorator canvas is recreated over a tree's life while the tree
        itself stays registered. Attached whatever the strategy: the handler
        is passive and signal() drops what the strategy does not want."""
        if not canvas:
            return
        try:
            canvas.register("focused", tree.on_canvas_focused)
        except Exception as e:
            print(f"ui_elements: could not register canvas focus event: {e}")

    def unregister_canvas(self, tree, canvas):
        if not canvas:
            return
        try:
            canvas.unregister("focused", tree.on_canvas_focused)
        except Exception:
            pass

    def refresh(self):
        """Re-read the strategy and attach or drop listeners to match. Called
        for you when the setting changes."""
        self._cancel_pending()
        self._set_focused(True, "refresh")
        self._sync_listeners()

    def _sync_listeners(self):
        has_trees = bool(self._trees)

        if has_trees and not self._strategy_cb:
            self._strategy_cb = lambda *_: self.refresh()
            try:
                settings.register(STRATEGY_SETTING, self._strategy_cb)
            except Exception:
                self._strategy_cb = None
        elif not has_trees and self._strategy_cb:
            try:
                settings.unregister(STRATEGY_SETTING, self._strategy_cb)
            except Exception:
                pass
            self._strategy_cb = None

        if has_trees and not self._win_focus_cb:
            self._win_focus_cb = self._on_win_focus
            try:
                ui.register("win_focus", self._win_focus_cb)
            except Exception as e:
                self._win_focus_cb = None
                print(f"ui_elements: could not register win_focus: {e}")
        elif not has_trees and self._win_focus_cb:
            try:
                ui.unregister("win_focus", self._win_focus_cb)
            except Exception:
                pass
            self._win_focus_cb = None

        # The only source with a running cost, so this one tracks the strategy.
        want_click = has_trees and _uses("click")
        if want_click != self._click_watching:
            from .click_outside import click_outside_watcher
            if want_click:
                click_outside_watcher.watch(self._click_key, self._on_global_click)
            else:
                click_outside_watcher.unwatch(self._click_key)
            self._click_watching = want_click

    # -- signal sources -------------------------------------------------

    def signal(self, focused: bool, source: str = ""):
        """Every strategy funnels here. Focus is taken at once; blur is only a
        proposal until _commit_blur has checked it against the OS."""
        if not self._trees or not _uses(source):
            return
        if focused:
            self._cancel_pending()
            self._set_focused(True, source)
        elif not self._pending_blur_job:
            self._pending_blur_job = cron.after(
                BLUR_GRACE, lambda: self._commit_blur(source)
            )

    def _on_win_focus(self, window):
        try:
            is_ours = window.app.pid == os.getpid()
        except Exception:
            is_ours = False
        self.signal(is_ours, "win_focus")

    def _on_global_click(self, gpos: Point2d):
        for tree in list(self._trees.values()):
            try:
                if tree.contains_global_pos(gpos):
                    self.signal(True, "click")
                    return
            except Exception:
                continue
        self.signal(False, "click")

    # -- commit ---------------------------------------------------------

    def _cancel_pending(self):
        if self._pending_blur_job:
            cron.cancel(self._pending_blur_job)
            self._pending_blur_job = None

    def _commit_blur(self, source: str):
        self._pending_blur_job = None
        # The OS is the tiebreaker for anything that watches OS focus. A
        # click-only strategy has no OS opinion to check - a press outside our
        # rects is the whole signal - so it skips this.
        if _uses("win_focus") or _uses("canvas"):
            if _talon_holds_focus():
                return
        self._set_focused(False, source)

    def _set_focused(self, focused: bool, source: str):
        if self._focused == focused:
            return
        self._focused = focused
        for tree in list(self._trees.values()):
            try:
                tree.on_window_focus_changed(focused)
            except Exception as e:
                print(f"ui_elements: window focus handler error: {e}")

    # -- introspection --------------------------------------------------

    @property
    def is_focused(self) -> bool:
        return self._focused

    def debug_state(self) -> dict:
        return {
            "strategy": _strategy(),
            "focused": self._focused,
            "trees": len(self._trees),
            "talon_holds_focus": _talon_holds_focus(),
            "blur_pending": bool(self._pending_blur_job),
            "win_focus_registered": bool(self._win_focus_cb),
            "click_watching": self._click_watching,
        }


window_focus_manager = WindowFocusManager()
