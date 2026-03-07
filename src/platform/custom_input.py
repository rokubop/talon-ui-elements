"""
Custom canvas-rendered text input state and keyboard handling.
Manages cursor position, text buffer, selection, and key event processing.
Uses Talon's canvas key events (not a Win32 hook).
"""

from talon import clip, Context, cron
from dataclasses import dataclass
from typing import Callable, Optional

_ctx = Context()

# Shifted symbol map for canvas key names
_SHIFT_CHARS = {
    '1': '!', '2': '@', '3': '#', '4': '$', '5': '%',
    '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
    '-': '_', '=': '+', '[': '{', ']': '}', '\\': '|',
    ';': ':', "'": '"', ',': '<', '.': '>', '/': '?', '`': '~',
}

@dataclass
class InputState:
    text: str = ""
    cursor_pos: int = 0
    selection_start: Optional[int] = None
    cursor_visible: bool = True
    scroll_offset: float = 0.0

    @property
    def has_selection(self) -> bool:
        return self.selection_start is not None and self.selection_start != self.cursor_pos

    @property
    def selection_range(self) -> Optional[tuple[int, int]]:
        if not self.has_selection:
            return None
        start = min(self.selection_start, self.cursor_pos)
        end = max(self.selection_start, self.cursor_pos)
        return (start, end)

    def delete_selection(self) -> str:
        if not self.has_selection:
            return self.text
        start, end = self.selection_range
        self.text = self.text[:start] + self.text[end:]
        self.cursor_pos = start
        self.selection_start = None
        return self.text


class CustomInputManager:
    """Manages all active custom input fields and routes keyboard events."""

    CURSOR_BLINK_MS = 530

    def __init__(self):
        self._inputs: dict[str, InputState] = {}
        self._focused_id: Optional[str] = None
        self._on_change_callbacks: dict[str, Callable] = {}
        self._on_submit_callbacks: dict[str, Callable] = {}
        self._render_callback: Optional[Callable] = None
        self._blink_job = None

    def create_input(self, id: str, initial_value: str = "", on_change: Callable = None, on_submit: Callable = None):
        if id not in self._inputs:
            self._inputs[id] = InputState(text=initial_value, cursor_pos=len(initial_value))
        if on_change:
            self._on_change_callbacks[id] = on_change
        if on_submit:
            self._on_submit_callbacks[id] = on_submit

    def remove_input(self, id: str):
        self._inputs.pop(id, None)
        self._on_change_callbacks.pop(id, None)
        self._on_submit_callbacks.pop(id, None)
        if self._focused_id == id:
            self._focused_id = None
            self._stop_blink()
            _ctx.tags = []

    def remove_all(self):
        self._inputs.clear()
        self._on_change_callbacks.clear()
        self._on_submit_callbacks.clear()
        self._focused_id = None
        self._stop_blink()
        _ctx.tags = []

    def get_state(self, id: str) -> Optional[InputState]:
        return self._inputs.get(id)

    def get_value(self, id: str) -> str:
        state = self._inputs.get(id)
        return state.text if state else ""

    def set_value(self, id: str, value: str):
        state = self._inputs.get(id)
        if state:
            state.text = value
            state.cursor_pos = len(value)
            state.selection_start = None

    def focus(self, id: str):
        if id in self._inputs:
            self._focused_id = id
            self._start_blink()
            _ctx.tags = ["user.ui_elements_typing"]

    def blur(self):
        if self._focused_id:
            state = self._inputs.get(self._focused_id)
            if state:
                state.selection_start = None
        self._focused_id = None
        self._stop_blink()
        _ctx.tags = []

    def is_focused(self, id: str) -> bool:
        return self._focused_id == id

    @property
    def focused_id(self) -> Optional[str]:
        return self._focused_id

    @property
    def has_focused_input(self) -> bool:
        return self._focused_id is not None

    def set_render_callback(self, callback: Callable):
        self._render_callback = callback

    def _render(self):
        if self._render_callback:
            self._render_callback()

    def _start_blink(self):
        self._stop_blink()
        state = self._inputs.get(self._focused_id)
        if state:
            state.cursor_visible = True

        def blink():
            state = self._inputs.get(self._focused_id)
            if state:
                state.cursor_visible = not state.cursor_visible
                self._render()

        self._blink_job = cron.interval(f"{self.CURSOR_BLINK_MS}ms", blink)

    def _stop_blink(self):
        if self._blink_job:
            cron.cancel(self._blink_job)
            self._blink_job = None

    def _reset_blink(self):
        """Reset cursor to visible and restart blink timer."""
        state = self._inputs.get(self._focused_id)
        if state:
            state.cursor_visible = True
        self._start_blink()

    def handle_canvas_key(self, e) -> bool:
        """Handle a key event from Talon's canvas. Returns True if handled.
        Called from tree.on_key on the main thread."""
        if not self._focused_id:
            return False

        state = self._inputs.get(self._focused_id)
        if not state:
            return False

        if not e.down:
            return True  # Block key-up when focused

        key = e.key.lower() if e.key else ""
        mods = [m.lower() for m in e.mods] if e.mods else []
        shift = "shift" in mods
        ctrl = "ctrl" in mods or "control" in mods
        alt = "alt" in mods

        old_text = state.text
        handled = self._process_key(state, key, shift, ctrl, alt)

        if handled:
            if state.text != old_text:
                self._fire_on_change(self._focused_id, state.text, old_text)
            self._reset_blink()
            self._render()
            return True

        return False

    def _process_key(self, state: InputState, key: str, shift: bool, ctrl: bool, alt: bool) -> bool:
        # Ctrl shortcuts
        if ctrl:
            if key == 'a':
                state.selection_start = 0
                state.cursor_pos = len(state.text)
                return True
            elif key == 'c':
                if state.has_selection:
                    start, end = state.selection_range
                    clip.set_text(state.text[start:end])
                return True
            elif key == 'v':
                text = clip.text()
                if text:
                    text = text.replace('\n', ' ').replace('\r', '')
                    if state.has_selection:
                        state.delete_selection()
                    state.text = state.text[:state.cursor_pos] + text + state.text[state.cursor_pos:]
                    state.cursor_pos += len(text)
                return True
            elif key == 'x':
                if state.has_selection:
                    start, end = state.selection_range
                    clip.set_text(state.text[start:end])
                    state.delete_selection()
                return True
            elif key == 'backspace':
                if state.has_selection:
                    state.delete_selection()
                elif state.cursor_pos > 0:
                    pos = state.cursor_pos - 1
                    while pos > 0 and state.text[pos - 1] == ' ':
                        pos -= 1
                    while pos > 0 and state.text[pos - 1] != ' ':
                        pos -= 1
                    state.text = state.text[:pos] + state.text[state.cursor_pos:]
                    state.cursor_pos = pos
                    state.selection_start = None
                return True
            elif key == 'delete':
                if state.has_selection:
                    state.delete_selection()
                elif state.cursor_pos < len(state.text):
                    pos = state.cursor_pos
                    while pos < len(state.text) and state.text[pos] == ' ':
                        pos += 1
                    while pos < len(state.text) and state.text[pos] != ' ':
                        pos += 1
                    state.text = state.text[:state.cursor_pos] + state.text[pos:]
                    state.selection_start = None
                return True
            elif key == 'left':
                pos = state.cursor_pos - 1
                while pos > 0 and state.text[pos - 1] == ' ':
                    pos -= 1
                while pos > 0 and state.text[pos - 1] != ' ':
                    pos -= 1
                pos = max(0, pos)
                if shift:
                    if state.selection_start is None:
                        state.selection_start = state.cursor_pos
                else:
                    state.selection_start = None
                state.cursor_pos = pos
                return True
            elif key == 'right':
                pos = state.cursor_pos
                while pos < len(state.text) and state.text[pos] == ' ':
                    pos += 1
                while pos < len(state.text) and state.text[pos] != ' ':
                    pos += 1
                if shift:
                    if state.selection_start is None:
                        state.selection_start = state.cursor_pos
                else:
                    state.selection_start = None
                state.cursor_pos = pos
                return True
            return False

        # Navigation keys
        if key == 'left':
            if shift:
                if state.selection_start is None:
                    state.selection_start = state.cursor_pos
                state.cursor_pos = max(0, state.cursor_pos - 1)
            elif state.has_selection:
                state.cursor_pos = min(state.selection_start, state.cursor_pos)
                state.selection_start = None
            else:
                state.cursor_pos = max(0, state.cursor_pos - 1)
            return True

        if key == 'right':
            if shift:
                if state.selection_start is None:
                    state.selection_start = state.cursor_pos
                state.cursor_pos = min(len(state.text), state.cursor_pos + 1)
            elif state.has_selection:
                state.cursor_pos = max(state.selection_start, state.cursor_pos)
                state.selection_start = None
            else:
                state.cursor_pos = min(len(state.text), state.cursor_pos + 1)
            return True

        if key == 'home':
            if shift:
                if state.selection_start is None:
                    state.selection_start = state.cursor_pos
            else:
                state.selection_start = None
            state.cursor_pos = 0
            return True

        if key == 'end':
            if shift:
                if state.selection_start is None:
                    state.selection_start = state.cursor_pos
            else:
                state.selection_start = None
            state.cursor_pos = len(state.text)
            return True

        if key == 'backspace':
            if state.has_selection:
                state.delete_selection()
            elif state.cursor_pos > 0:
                state.text = state.text[:state.cursor_pos - 1] + state.text[state.cursor_pos:]
                state.cursor_pos -= 1
                state.selection_start = None
            return True

        if key == 'delete':
            if state.has_selection:
                state.delete_selection()
            elif state.cursor_pos < len(state.text):
                state.text = state.text[:state.cursor_pos] + state.text[state.cursor_pos + 1:]
                state.selection_start = None
            return True

        if key == 'enter' or key == 'return':
            cb = self._on_submit_callbacks.get(self._focused_id)
            if cb:
                cb(state.text)
            return True

        if key == 'escape':
            self.blur()
            self._render()
            return True

        if key == 'tab':
            return False  # Let tab through for focus navigation

        # Skip modifier-only and function keys
        if key in ('shift', 'ctrl', 'control', 'alt', 'win', 'super',
                    'capslock', 'numlock', 'scrolllock', 'fn') \
                or key.startswith('f') and key[1:].isdigit():
            return True  # Block but don't type

        # Printable character
        char = self._key_to_char(key, shift)
        if char:
            if state.has_selection:
                state.delete_selection()
            state.text = state.text[:state.cursor_pos] + char + state.text[state.cursor_pos:]
            state.cursor_pos += 1
            state.selection_start = None
            return True

        return True  # Block unknown keys when focused

    def _key_to_char(self, key: str, shift: bool) -> Optional[str]:
        """Convert a canvas key name to a printable character."""
        if key == 'space':
            return ' '
        if len(key) == 1:
            if shift:
                if key in _SHIFT_CHARS:
                    return _SHIFT_CHARS[key]
                return key.upper()
            return key
        return None

    def _fire_on_change(self, id: str, new_value: str, old_value: str):
        cb = self._on_change_callbacks.get(id)
        if cb:
            from ..core.entity_manager import ChangeEvent
            cb(ChangeEvent(value=new_value, id=id, previous_value=old_value))


custom_input_manager = CustomInputManager()
