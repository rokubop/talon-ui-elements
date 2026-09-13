# Drag

A drag does not move anything until you let go.

From mousedown to mouseup:

- base and decorator keep the paint they had when the drag started
- an outline of where it will land draws on a canvas of its own
- the render queue is paused, so state changes wait for the drop
- on mouseup the outline goes and one render puts the element there

Esc abandons a drag and puts everything back.

## Why

A drag used to relayout the whole tree on every mouse report. A high polling rate mouse reports far faster than the display refreshes, so the canvas draw thread fell behind and the window lagged the cursor.

A drag tick is now one `freeze` of one canvas drawing one stroked rect.

## What drags

| Kind | Outline | Pauses renders |
| -- | -- | -- |
| `draggable` move | yes | yes |
| `resizable` edge | yes | yes |
| scrollbar thumb | no | yes |
| text selection | no | no |

Scrollbar and text drags change no layout, so they stay live and follow the cursor directly.

A resize pins only the axis it touched, so a panel dragged by its right edge keeps stretching to its parent's height. The new size lasts until the UI hides.

## Appearance

`DRAG_GHOST_COLOR` and `DRAG_GHOST_STROKE_WIDTH` set the outline.

`DRAG_GHOST_FILL_COLOR` fills it, `DRAG_DIM_COLOR` washes over where the element still sits. Both off by default: each is a window-sized fill on every frame.

## Adding a mode

A mode is a `DragSession` subclass in `src/drag/modes/`.

- `preview = True` to draw an outline, which requires `pause_renders = True`
- `begin` returns False to abandon before the drag starts
- `commit` mutates state while renders are still paused
- `settle` paints and fires callbacks once they are live again
- `shapes` returns what the overlay draws

`DragController` owns the one active session and decides what a mouse event means.
