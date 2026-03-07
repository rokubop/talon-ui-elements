# Custom Canvas-Rendered Text Input — Progress Report

## Overview
Replacing Talon's buggy experimental `TextArea` with a fully custom canvas-rendered text input. Feature-toggled via `user.ui_elements_custom_input` setting (default `False`).

## Status: Core typing works, needs testing of edge cases

### What works
- Custom input renders on the Skia canvas (text, cursor, selection highlight)
- Real-time typing with immediate visual feedback
- Cursor blink animation
- Autofocus on load
- Click-to-focus
- Focus outline ring
- `user.ui_elements_typing` tag activates when input is focused (suppresses other commands)
- on_change callback fires with ChangeEvent

### Needs testing
- Tab / shift-tab focus navigation (does typing work after tabbing back?)
- Escape to blur
- Ctrl+A (select all), Ctrl+C/V/X (copy/paste/cut)
- Shift+arrow selection
- Ctrl+arrow word navigation
- Ctrl+backspace/delete (word delete)
- Home/End keys
- Click off UI completely and back
- Destroy/cleanup (keyboard hook cleanup, tag clearing)
- Multiple inputs in same UI

### Known issues to watch for
- After tabbing to a button and back to input, verify typing still works
- Escape blur should clear the `user.ui_elements_typing` tag
- Cleanup on UI destroy must be reliable

## Architecture

### Key insight (IMPORTANT)
**Do NOT use Win32 `SetWindowsHookEx` for keyboard capture.** We tried extensively — the hook installs but the callback never fires when Talon canvases are active. Talon's canvas system intercepts keyboard events at a level that blocks Win32 low-level hooks. This was debugged over many iterations.

**The correct approach:** Use Talon's own canvas key events. Set `canvas_decorator.focused = True` and handle keys in `tree.on_key`, routing them to `custom_input_manager.handle_canvas_key(e)`. Everything runs on the main thread — no threads, no GIL issues, no message pumps.

### How it works
1. `canvas_decorator.focused = True` — canvas receives key events from Talon
2. `tree.on_key(e)` — checks if custom input is focused, routes to `custom_input_manager.handle_canvas_key(e)`
3. `handle_canvas_key` — processes the key (typing, navigation, selection, clipboard), updates `InputState`
4. Calls `_render()` → `render_decorator_canvas()` → redraws text/cursor on decorator canvas
5. Cursor blink via `cron.interval("530ms")` — separate from key handling

### File map

**Modified files:**
- `settings.py` — Added `user.ui_elements_custom_input` setting and `user.ui_elements_typing` tag
- `src/nodes/tree.py` — `on_key` routes to custom input; `get_mouse_hovered_input_id` checks `interactive_node_list`; `render_decorator_canvas` sets canvas focused for custom input; various guards for custom input state
- `src/nodes/node_input_text.py` — `v2_render`/`v2_render_decorator` branch for custom input; `_setup_custom_input` creates input state; `_render_custom_input_text` draws text/cursor/selection on canvas
- `src/core/state_manager.py` — `focus_input`/`focus_node`/`blur`/`blur_all`/`autofocus_node`/`get_input_value`/`clear_all`/`clear_state_for_tree` all route through `custom_input_manager` when enabled
- `src/core/entity_manager.py` — `create_input` returns early when custom input enabled
- `src/ref.py` — `clear`/`set_value`/`get("value")` route through `custom_input_manager`

**New files:**
- `src/platform/__init__.py` — Empty init for platform module
- `src/platform/keyboard_hook.py` — Just contains `KeyEvent` dataclass and `KeyCallback` type (Win32 hook code removed, kept for potential future use)
- `src/platform/custom_input.py` — `InputState` dataclass, `CustomInputManager` singleton with text editing logic, canvas key event handling, cursor blink

**Test files:**
- `test-topic-a/tap_test.py` — Test UI with input_text (autofocus), text label, close button
- `test-topic-a/tap_test.talon` — Sets `user.ui_elements_custom_input = true`

### Canvas key event format
From `tree.on_key(e)`:
- `e.key` — string like `"a"`, `"space"`, `"backspace"`, `"left"`, `"enter"`, etc.
- `e.down` — bool, True for key press
- `e.mods` — list of strings like `["shift"]`, `["ctrl"]`, `["shift", "ctrl"]`

### Rendering pipeline
- Base canvas: heavy render (layout, backgrounds, borders) — `v2_render` registers input as `decoration_render`
- Decorator canvas: fast overlay — `v2_render_decorator` → `_render_custom_input_text` draws text/cursor/selection
- The render callback (`custom_input_manager._render_callback`) calls `tree.render_decorator_canvas()` which freezes the decorator canvas, triggering `on_draw_decorator_canvas` → `draw_decoration_renders` → `v2_render_decorator`

## What was tried and abandoned

### Win32 SetWindowsHookEx (abandoned)
- Installed WH_KEYBOARD_LL hook on a separate thread with its own message pump
- Hook installed successfully but callback was never invoked when Talon canvases were active
- Tried: GetMessageW loop, PeekMessageW+DispatchMessageW, MsgWaitForMultipleObjectsEx, posting WM_NULL to wake queue, PeekMessage before install, ready_event synchronization, main-thread installation
- Root cause: Talon's canvas system intercepts keyboard events, preventing the Win32 hook callback from firing
- The hook would start working only after clicking completely off the UI and back (which changed the canvas focus state)

### talon.tap (abandoned)
- `tap.register(tap.KEY, callback)` — registered without error but callback never fired
- Nobody in the Talon community codebase uses tap for key events
