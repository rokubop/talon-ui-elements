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
- "poll"       Ask the OS on an interval which window is active. No event to
               go missing, and measured against the others it was the only one
               that produced a verdict at all here. The default.
- "both"       canvas + win_focus.
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

from .constants import UNFOCUSED_OPACITY_FLOOR

# Long enough to swallow a blur/focus pair from our own canvas churn, short
# enough that the window visibly reacts to a real click away.
BLUR_GRACE = "120ms"
# One ui.active_window() call per tick, and a fade nobody is looking at does not
# need to be quicker than this.
POLL_INTERVAL = "200ms"

STRATEGY_SETTING = "user.ui_elements_focus_strategy"
OPACITY_SETTING = "user.ui_elements_unfocused_opacity"
MASK_SETTING = "user.ui_elements_unfocused_mask_color"
MASK_STRENGTH_SETTING = "user.ui_elements_unfocused_mask_strength"
MASK_SCOPE_SETTING = "user.ui_elements_unfocused_mask_scope"
INERT_SETTING = "user.ui_elements_unfocused_inert"

MASK_SCOPES = ("all", "title_bar")
DEFAULT_STRATEGY = "poll"
VALID_STRATEGIES = ("off", "canvas", "win_focus", "click", "poll", "both", "all")

# Runtime overrides beat the settings. Talon settings are read-only from
# Python - moving one needs a Context, and a Context declared in a file Talon
# imports rather than loads does not reliably take - so anything that wants to
# change these at runtime goes through here instead.
_strategy_override = None
_opacity_override = None
_mask_override = None
_mask_strength_override = None
_mask_scope_override = None
_inert_override = None


def _strategy():
    if _strategy_override in VALID_STRATEGIES:
        return _strategy_override
    try:
        value = (settings.get(STRATEGY_SETTING) or "").strip().lower()
    except Exception:
        value = ""
    return value if value in VALID_STRATEGIES else DEFAULT_STRATEGY


def get_strategy() -> str:
    return _strategy()


def set_strategy(value):
    """Override the strategy setting. None hands it back to the setting."""
    global _strategy_override
    if value is not None:
        value = str(value).strip().lower()
        if value not in VALID_STRATEGIES:
            raise ValueError(
                f"unknown focus strategy {value!r}, expected one of {VALID_STRATEGIES}"
            )
    _strategy_override = value
    window_focus_manager.refresh()


def get_unfocused_opacity() -> float:
    """How see-through a tree goes while unfocused. 1.0 leaves it alone."""
    value = _opacity_override
    if value is None:
        try:
            value = settings.get(OPACITY_SETTING, 1.0)
        except Exception:
            return 1.0
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 1.0
    if value >= 1.0:
        return 1.0
    # Floored rather than allowed to reach 0: a tree faded to nothing still
    # blocks the mouse where its canvases are, with nothing on screen to say so.
    return max(UNFOCUSED_OPACITY_FLOOR, value)


def set_unfocused_opacity(value):
    """Override the opacity setting. None hands it back to the setting."""
    global _opacity_override
    _opacity_override = None if value is None else float(value)
    window_focus_manager.repaint_trees()


def get_unfocused_mask_color() -> str:
    """Flatten an unfocused tree to one colour. "" leaves its colours alone,
    "auto" takes the tree's own background, anything else is a hex colour."""
    value = _mask_override
    if value is None:
        try:
            value = settings.get(MASK_SETTING, "")
        except Exception:
            return ""
    return (value or "").strip().lstrip("#")


def set_unfocused_mask_color(value):
    """Override the mask setting. None hands it back to the setting."""
    global _mask_override
    _mask_override = value
    window_focus_manager.repaint_trees()


def get_unfocused_mask_strength() -> float:
    """How far the mask colour pulls the tree's own colours toward it. 1.0
    replaces them outright, 0.5 is a tint over what is there, 0.0 is off."""
    value = _mask_strength_override
    if value is None:
        try:
            value = settings.get(MASK_STRENGTH_SETTING, 1.0)
        except Exception:
            return 1.0
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 1.0


def set_unfocused_mask_strength(value):
    """Override the mask strength setting. None hands it back to the setting."""
    global _mask_strength_override
    _mask_strength_override = None if value is None else float(value)
    window_focus_manager.repaint_trees()


def get_unfocused_mask_scope() -> str:
    """What the mask covers: the whole tree, or only its title bars the way an
    inactive OS window greys only its own."""
    value = _mask_scope_override
    if value is None:
        try:
            value = settings.get(MASK_SCOPE_SETTING, "all")
        except Exception:
            return "all"
    value = (value or "").strip().lower()
    return value if value in MASK_SCOPES else "all"


def set_unfocused_mask_scope(value):
    """Override the mask scope setting. None hands it back to the setting."""
    global _mask_scope_override
    _mask_scope_override = value
    window_focus_manager.repaint_trees()


def get_unfocused_inert() -> bool:
    """Whether an unfocused tree stops responding: no hints, no hover, and a
    click anywhere but a title bar only takes focus back."""
    value = _inert_override
    if value is None:
        try:
            value = settings.get(INERT_SETTING, False)
        except Exception:
            return False
    return bool(value)


def set_unfocused_inert(value):
    """Override the inert setting. None hands it back to the setting."""
    global _inert_override
    _inert_override = None if value is None else bool(value)
    window_focus_manager.repaint_trees()


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
        # Testing hook: True/False pins the verdict, None hands it back.
        self._forced = None
        self._pending_blur_job = None
        self._win_focus_cb = None
        self._strategy_cb = None
        self._click_key = "__ui_elements_window_focus__"
        self._click_watching = False
        self._last_strategy = None
        self._refresh_count = 0
        self._poll_job = None
        # Which sources are actually producing events, as opposed to being
        # registered and silent.
        self._source_counts = {}

    # -- registration ---------------------------------------------------

    def watch(self, tree):
        """Called on every decorator paint, not only when the canvas is built.

        Saving a file re-imports src/ and leaves this module with a fresh
        manager while the trees stay mounted. Those trees never call watch()
        again, so a manager that only learned about them at canvas creation
        would sit there with no trees and silently detect nothing until the UI
        was re-shown. Cheap enough to call every paint: a hit on the dict and
        nothing else.
        """
        if self._trees.get(tree.guid) is tree:
            return
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
        # Drops the poll and the click watcher with the last tree.
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
        """Re-read the strategy and attach or drop listeners to match.

        Idempotent when the strategy has not moved, and that matters: this is
        wired to the settings callback, and Talon re-resolves settings whenever
        the active context set changes - which includes every app switch, the
        exact moment a blur is in flight. Cancelling the pending blur and
        resetting the verdict here made the window unable to ever unfocus.
        """
        self._refresh_count += 1
        changed = _strategy() != self._last_strategy
        self._sync_listeners()
        if changed:
            # A genuine strategy change has no history to carry over.
            self._cancel_pending()
            self._set_focused(True, "refresh")

    def repaint_trees(self):
        """Push a repaint through every watched tree. For a change that alters
        how an unfocused tree looks without altering whether it is focused."""
        for tree in list(self._trees.values()):
            try:
                tree.refresh_unfocused_state()
                tree.repaint_base_canvas()
                tree.render_decorator_canvas()
            except Exception as e:
                print(f"ui_elements: focus repaint error: {e}")

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

        # The sources with a running cost track the strategy rather than
        # staying attached like the passive ones.
        want_click = has_trees and _uses("click")
        if want_click != self._click_watching:
            from .click_outside import click_outside_watcher
            if want_click:
                click_outside_watcher.watch(self._click_key, self._on_global_click)
            else:
                click_outside_watcher.unwatch(self._click_key)
            self._click_watching = want_click

        want_poll = has_trees and _uses("poll")
        if want_poll and not self._poll_job:
            self._poll_job = cron.interval(POLL_INTERVAL, self._on_poll)
        elif not want_poll and self._poll_job:
            cron.cancel(self._poll_job)
            self._poll_job = None

        self._last_strategy = _strategy()

    # -- signal sources -------------------------------------------------

    def signal(self, focused: bool, source: str = ""):
        """Every strategy funnels here. Focus is taken at once; blur is only a
        proposal until _commit_blur has checked it against the OS."""
        self._source_counts[source] = self._source_counts.get(source, 0) + 1
        if not self._trees or self._forced is not None or not _uses(source):
            return
        if focused:
            self._cancel_pending()
            self._set_focused(True, source)
        elif not self._pending_blur_job:
            self._pending_blur_job = cron.after(
                BLUR_GRACE, lambda: self._commit_blur(source)
            )

    def _on_poll(self):
        self.signal(_talon_holds_focus(), "poll")

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

    def claim_focus(self):
        """The user clicked one of our trees. Not a strategy signal - it is not
        filtered by the strategy and it does not wait out the grace period."""
        if self._forced is not None:
            return
        self._cancel_pending()
        self._set_focused(True, "claim")

    def force(self, focused):
        """Pin the verdict, or None to hand it back to the strategies. Splits
        "detection never fired" from "the fade never rendered"."""
        self._forced = focused
        self._cancel_pending()
        if focused is None:
            # Do not leave a pinned verdict standing after the pin is gone.
            self._set_focused(_talon_holds_focus(), "released")
            return
        self._set_focused(focused, "forced")

    def _commit_blur(self, source: str):
        self._pending_blur_job = None
        if self._forced is not None:
            return
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
            "strategy_from": "override" if _strategy_override else "setting",
            "unfocused_opacity": get_unfocused_opacity(),
            "unfocused_mask_color": get_unfocused_mask_color() or None,
            "unfocused_mask_strength": get_unfocused_mask_strength(),
            "unfocused_mask_scope": get_unfocused_mask_scope(),
            "unfocused_inert": get_unfocused_inert(),
            "focused": self._focused,
            "forced": self._forced,
            "trees": len(self._trees),
            "talon_holds_focus": _talon_holds_focus(),
            "blur_pending": bool(self._pending_blur_job),
            "refreshes": self._refresh_count,
            "source_events": dict(self._source_counts),
            "polling": bool(self._poll_job),
            "win_focus_registered": bool(self._win_focus_cb),
            "click_watching": self._click_watching,
        }


window_focus_manager = WindowFocusManager()
