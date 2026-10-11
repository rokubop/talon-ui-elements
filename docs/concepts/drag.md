# Drag

## Decisions

- **Drag outline uses its own canvas on top**. Built at the end of the first full render, hidden, and only if the tree has a `draggable` or `resizable` node aka `window` element - 2026-09-07, v0.22.0.
- **Use ghost lines until release, rather than relayout UI live.** Helps with performance and visual consistency - 2026-09-07, v0.22.0
- **Many draggables per tree.** Each moves on its own, keyed by `id`, and the one painted on top under the cursor is grabbed. Nested draggables are confined to the canvas, which only spans the screens when the root is a `screen` or a direct child is draggable - 2026-10-10.
- **Throttle repaints rather than mouse events.** Uses `DRAG_OVERLAY_MIN_FRAME_MS` 8 ms and `DRAG_OVERLAY_STALL_MS` 120 ms - 2026-09-07, v0.22.0

## Affected by drag

| Kind | Starts on | Outline | Pauses renders |
| -- | -- | -- | -- |
| `draggable` move | 4px past mousedown | yes | yes |
| `resizable` edge | mousedown, 6px of the edge | yes | yes |
| scrollbar thumb | mousedown on thumb | no | yes |
| text selection | mousedown on text | no | no |

## Keyboard

Esc during dragging will cancel

## Properties

| Property | On | Value |
| -- | -- | -- |
| `draggable` | any div but the root | bool |
| `drag_handle` | child of a draggable | bool, the grabbable area |
| `drag_bounds` | draggable or resizable | `"root"` (the tree's screen), or `(x, y, width, height)` in screen pixels. Move and resize stop at its edges |
| `resizable` | node or window | `True`, `"right"`, `["right", "bottom"]` |
| `on_drag_end` | draggable | callable, arg: `id`, `dx`, `dy` (unscaled, this drag only) |
| `on_resize_end` | resizable | callable, arg: `id`, `width`, `height`, `edge` |
| `drag_title_bar_only` | window | bool, default True |

## Options
`constants.py`:

| Option | Description |
| -- | -- |
| `DRAG_GHOST_COLOR` | `FFFFFFAA` |
| `DRAG_GHOST_STROKE_WIDTH` | `2.0` |
| `DRAG_GHOST_FILL_COLOR` |  |
| `DRAG_DIM_COLOR` |  |
