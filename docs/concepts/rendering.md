# Rendering

Three canvases, plus one that exists only during a drag.

| Canvas | Draws | Present |
| -- | -- | -- |
| Base | Layout and static elements | Always |
| Decorator | Changes that do not move layout | Always |
| Blockable | Nothing. Receives mouse events | When the UI is interactive or draggable |
| Drag overlay | The outline of a held drag | Only mid-drag |

Give an element an `id` or a `highlight_style` and it draws on the decorator canvas.

## Full renders

Relayout, then base and decorator. Triggered by:

- `actions.user.ui_elements_show`
- `state` changes
- `actions.user.ui_elements_set_state`
- `actions.user.ui_elements_set_property`

## Decorator-only renders

No relayout, no base repaint. Much faster. Triggered by:

- `actions.user.ui_elements_highlight`, `..._highlight_briefly`, `..._unhighlight`
- `actions.user.ui_elements_set_text`
- keyboard navigation and focus changes

Prefer these when only appearance changes. See [State](./state.md).

## Drags

A drag never relayouts. See [Drag](./drag.md).

## Mouse

Events arrive through the blockable canvas, which is why a click landing outside the UI needs a separate mechanism. See [Mouse](./mouse.md).
