# Rendering

UI Elements uses a 3 canvas system for rendering.

1. **Base Canvas** - The primary rendering layer. All static elements and layout are rendered here.
2. **Decorator Canvas** - An overlay layer for dynamic rendering that do not affect the underlying layout. Elements with an `id` or `highlight_style` will be rendered here.
3. **Blockable Canvas** - Used for mouse interaction, only applied when interactive elements are present, or if the UI is draggable.
4. **Drag Overlay** - Only while a drag is held. Nothing else draws on it.

## When renders happen

### Full Re-renders
A complete re-render including base and decorator canvases happens when:
- `actions.user.ui_elements_show` is called
- `state` changes
- `actions.user.ui_elements_set_state` is called
- `actions.user.ui_elements_set_property` is called

### Decorator-Only Renders
Faster decorator-only renders update just the decoration layer and do not update the layout / base layer:

- `actions.user.ui_elements_highlight`
- `actions.user.ui_elements_highlight_briefly`
- `actions.user.ui_elements_unhighlight`
- `actions.user.ui_elements_set_text`
- Keyboard navigation and focus changes

If you give an element an `id` or a `highlight_style`, it will be rendered on the decorator canvas.

## Drags

Moving or resizing an element does not re-lay out the tree. From mousedown to
mouseup:

- the base and decorator canvases keep the paint they had when the drag started
- an outline of where the element will land is drawn on a canvas of its own
- the render queue is paused, so state changes wait for the drop
- on mouseup the outline is dropped and one render puts the element there

A drag tick is one `freeze` of one canvas drawing two shapes, capped at ~125Hz.
It used to be a repaint of the whole tree per mouse report.

Scrollbar and text-selection drags do not change layout, so they stay live and
draw no outline.

Esc abandons a drag and puts everything back.
