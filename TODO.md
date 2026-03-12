# TODO

## Bugs

### Padding causes text cut-off in input_text/textarea
- Padding behavior is inconsistent and causes text to be clipped
- Thoroughly test padding expectations in inputs
- Check how `NodeInputTextProperties.__init__` adds horizontal padding on top of user-specified padding (lines 863-870) — may be doubling up
- Verify `content_children_pos` and `content_size` from box model correctly account for padding
- Test combinations: `padding`, `padding_top`, `padding_bottom`, `padding_left`, `padding_right` with various font sizes
- Investigate why underscores/descenders are cut off at font_size 14-15 but not 16 — likely related to padding reducing content_height

## Completed

### Space key not visually updating in input_text/textarea
- Fixed: `paint.measure_text(text)[1].width` (bounds rect) → `[0]` (advance width)
- Bounds rect excludes trailing whitespace; advance width includes it
- Fixed in `node_input_text.py` (8 places) and `node_textarea.py` (4 places)
