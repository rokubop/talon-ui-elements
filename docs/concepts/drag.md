# Drag

## Decisions

- **Drag outline uses its own canvas on top**. Built at the end of the first full render, hidden, and only if the tree has a `draggable` or `resizable` node aka `window` element - 2026-09-07, v0.22.0.
- **Use ghost lines until release, rather than relayout UI live.** Helps with performance and visual consistency - 2026-09-07, v0.22.0
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
| `draggable` | top level div | bool |
| `drag_handle` | child of a draggable | bool, the grabbable area |
| `resizable` | node or window | `True`, `"right"`, `["right", "bottom"]` |
| `on_drag_end` | draggable | callable, 1 event arg |
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
