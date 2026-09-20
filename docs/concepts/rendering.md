# Rendering

UI Elements uses a 3 canvas system for rendering (+ 1 drag canvas if applicable).

| Canvas name | Draws | Present |
| -- | -- | -- |
| Base | Layout and static elements | Always |
| Decorator | Changes that do not move layout, such as highlights and hovers | Always |
| Blockable | Nothing. Receives mouse events | When the UI is interactive or draggable |
| Drag overlay | The outline of a held drag | Only mid-drag |

An element draws on the decorator canvas instead of the base canvas when its appearance can change without moving layout: a `highlight_style` that differs from its resting style, a `disabled_style` while disabled, an open `select`, or an `input_text`. Its children go with it.

## Full renders

Relayout, base + decorator. Triggered by:

- `actions.user.ui_elements_show`
- `state` changes
- `actions.user.ui_elements_set_state`
- `actions.user.ui_elements_set_property`

## Decorator-only renders

Much faster. Triggered by:

- `actions.user.ui_elements_highlight`, `..._highlight_briefly`, `..._unhighlight`
- `actions.user.ui_elements_set_text`
- keyboard navigation and focus changes

Prefer these when only appearance changes. See [State](./state.md).

## Drags

See [Drag](./drag.md).
