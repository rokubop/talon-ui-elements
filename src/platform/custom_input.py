"""
Custom canvas-rendered text input state and keyboard handling.
Manages cursor position, text buffer, selection, and key event processing.
Uses Talon's canvas key events (not a Win32 hook).
"""

from talon import clip, Context, cron
from dataclasses import dataclass
from typing import Callable, Optional
from ..constants import (
    parse_mods, MODIFIER_KEYS,
    KEY_ENTER, KEY_RETURN, KEY_ESCAPE, KEY_BACKSPACE, KEY_DELETE, KEY_TAB,
    KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_HOME, KEY_END,
)

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
        self._multiline_ids: set[str] = set()
        self._on_change_callbacks: dict[str, Callable] = {}
        self._on_submit_callbacks: dict[str, Callable] = {}
        self._render_callbacks: dict[str, Callable] = {}
        self._trees: dict[str, object] = {}
        self._blink_job = None

    def create_input(self, id: str, initial_value: str = "", on_change: Callable = None, on_submit: Callable = None, multiline: bool = False, tree=None):
        if id not in self._inputs:
            self._inputs[id] = InputState(text=initial_value, cursor_pos=len(initial_value))
        if multiline:
            self._multiline_ids.add(id)
        if on_change:
            self._on_change_callbacks[id] = on_change
        if on_submit:
            self._on_submit_callbacks[id] = on_submit
        if tree is not None:
            self._trees[id] = tree

    def remove_input(self, id: str):
        self._inputs.pop(id, None)
        self._multiline_ids.discard(id)
        self._on_change_callbacks.pop(id, None)
        self._on_submit_callbacks.pop(id, None)
        self._render_callbacks.pop(id, None)
        self._trees.pop(id, None)
        if self._focused_id == id:
            self._focused_id = None
            self._stop_blink()
            _ctx.tags = []

    def remove_all(self):
        self._inputs.clear()
        self._multiline_ids.clear()
        self._on_change_callbacks.clear()
        self._on_submit_callbacks.clear()
        self._render_callbacks.clear()
        self._trees.clear()
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

    def set_render_callback(self, id: str, callback: Callable):
        self._render_callbacks[id] = callback

    def _render(self):
        if self._focused_id and self._focused_id in self._render_callbacks:
            self._render_callbacks[self._focused_id]()

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
        shift, ctrl, alt = parse_mods(e.mods)

        old_text = state.text
        handled = self._process_key(state, key, shift, ctrl, alt)

        if handled:
            if state.text != old_text:
                self._fire_on_change(self._focused_id, state.text, old_text)
            self._reset_blink()
            self._render()
            return True

        return False

    @property
    def _is_multiline(self) -> bool:
        return self._focused_id in self._multiline_ids

    def _get_line_info(self, state: InputState):
        """Get (line_index, col_index, lines) for cursor position in raw text."""
        lines = state.text.split("\n")
        pos = 0
        for i, line in enumerate(lines):
            if pos + len(line) >= state.cursor_pos:
                return i, state.cursor_pos - pos, lines
            pos += len(line) + 1  # +1 for \n
        return len(lines) - 1, len(lines[-1]) if lines else 0, lines

    def _line_col_to_pos(self, line_idx: int, col: int, lines: list[str]) -> int:
        pos = 0
        for i in range(min(line_idx, len(lines) - 1)):
            pos += len(lines[i]) + 1
        target_line = lines[min(line_idx, len(lines) - 1)]
        return pos + min(col, len(target_line))

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
                    text = text.replace('\r\n', '\n').replace('\r', '')
                    if not self._is_multiline:
                        text = text.replace('\n', ' ')
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
            elif key == KEY_BACKSPACE:
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
            elif key == KEY_DELETE:
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
            elif key == KEY_LEFT:
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
            elif key == KEY_RIGHT:
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
        if key == KEY_LEFT:
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

        if key == KEY_RIGHT:
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

        if key == KEY_HOME:
            if shift:
                if state.selection_start is None:
                    state.selection_start = state.cursor_pos
            else:
                state.selection_start = None
            if self._is_multiline:
                line_idx, col, lines = self._get_line_info(state)
                state.cursor_pos = self._line_col_to_pos(line_idx, 0, lines)
            else:
                state.cursor_pos = 0
            return True

        if key == KEY_END:
            if shift:
                if state.selection_start is None:
                    state.selection_start = state.cursor_pos
            else:
                state.selection_start = None
            if self._is_multiline:
                line_idx, col, lines = self._get_line_info(state)
                state.cursor_pos = self._line_col_to_pos(line_idx, len(lines[line_idx]), lines)
            else:
                state.cursor_pos = len(state.text)
            return True

        if key == KEY_UP and self._is_multiline:
            line_idx, col, lines = self._get_line_info(state)
            if line_idx > 0:
                if shift:
                    if state.selection_start is None:
                        state.selection_start = state.cursor_pos
                else:
                    state.selection_start = None
                state.cursor_pos = self._line_col_to_pos(line_idx - 1, col, lines)
            return True

        if key == KEY_DOWN and self._is_multiline:
            line_idx, col, lines = self._get_line_info(state)
            if line_idx < len(lines) - 1:
                if shift:
                    if state.selection_start is None:
                        state.selection_start = state.cursor_pos
                else:
                    state.selection_start = None
                state.cursor_pos = self._line_col_to_pos(line_idx + 1, col, lines)
            return True

        if key == KEY_BACKSPACE:
            if state.has_selection:
                state.delete_selection()
            elif state.cursor_pos > 0:
                state.text = state.text[:state.cursor_pos - 1] + state.text[state.cursor_pos:]
                state.cursor_pos -= 1
                state.selection_start = None
            return True

        if key == KEY_DELETE:
            if state.has_selection:
                state.delete_selection()
            elif state.cursor_pos < len(state.text):
                state.text = state.text[:state.cursor_pos] + state.text[state.cursor_pos + 1:]
                state.selection_start = None
            return True

        if key == KEY_ENTER or key == KEY_RETURN:
            if self._is_multiline:
                if ctrl:
                    self._fire_form_submit(self._focused_id)
                    return True
                if state.has_selection:
                    state.delete_selection()
                state.text = state.text[:state.cursor_pos] + "\n" + state.text[state.cursor_pos:]
                state.cursor_pos += 1
                state.selection_start = None
                return True
            cb = self._on_submit_callbacks.get(self._focused_id)
            if cb:
                cb(state.text)
            else:
                self._fire_form_submit(self._focused_id)
            return True

        if key == KEY_ESCAPE:
            self.blur()
            self._render()
            return True

        if key == KEY_TAB:
            return False  # Let tab through for focus navigation

        # Skip modifier-only and function keys
        if key in MODIFIER_KEYS \
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

    def _fire_form_submit(self, id: str):
        """Find parent form of the input and call its on_submit."""
        tree = self._trees.get(id)
        node = tree.meta_state.id_to_node.get(id) if tree else None
        if node:
            from ..nodes.node_form import find_parent_form
            form_node = find_parent_form(node)
            if form_node:
                form_node.fire_submit()

    def _fire_on_change(self, id: str, new_value: str, old_value: str):
        cb = self._on_change_callbacks.get(id)
        if cb:
            from ..core.entity_manager import ChangeEvent
            cb(ChangeEvent(value=new_value, id=id, previous_value=old_value))


custom_input_manager = CustomInputManager()


def setup_custom_input(node, multiline: bool = False):
    """Shared setup for custom input nodes (input_text and textarea)."""
    if not custom_input_manager.get_state(node.id):
        custom_input_manager.create_input(
            id=node.id,
            initial_value=node.properties.value or "",
            on_change=node.properties.on_change,
            multiline=multiline,
            tree=node.tree,
        )

        def make_render_cb(tree_ref):
            def render_cb():
                if tree_ref.canvas_decorator:
                    tree_ref.render_decorator_canvas()
            return render_cb
        custom_input_manager.set_render_callback(node.id, make_render_cb(node.tree))
