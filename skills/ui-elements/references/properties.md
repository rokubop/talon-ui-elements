# Properties Reference

All properties are passed as keyword arguments: `div(background_color="333333", padding=16)`.

## Layout

- `flex_direction`: str = "column" - "column", "row"
- `justify_content`: str = "flex_start" - "flex_start", "flex_end", "center", "space_between", "space_evenly"
- `align_items`: str = "stretch" - "stretch", "center", "flex_start", "flex_end"
- `align_self`: str = None - "stretch", "center", "flex_start", "flex_end"
- `flex`: int = None - e.g. `1`, fills available space
- `flex_wrap`: bool/str = False - "wrap" or True. Requires explicit primary-axis size (e.g. width for row).
- `gap`: int/float = None - space between children in pixels

## Sizing

- `width`: int/float/str - pixels or "100%"
- `height`: int/float/str - pixels or "100%"
- `min_width`, `max_width`: int - pixels
- `min_height`, `max_height`: int - pixels

## Spacing

- `padding`: int - all sides
- `padding_top`, `padding_right`, `padding_bottom`, `padding_left`: int - individual sides
- `margin`: int - all sides
- `margin_top`, `margin_right`, `margin_bottom`, `margin_left`: int - individual sides

## Positioning

- `position`: str = "static" - "static", "relative", "absolute", "fixed"
- `top`, `left`, `right`, `bottom`: int/float - requires position to be set (not "static")

## Colors

- `background`: str = None - plain color or gradient: `"FF0000"`, `"linear_gradient(to_right, FF0000, 0000FF)"`. Directions: `to_right`, `to_left`, `to_bottom`, `to_top`, `to_bottom_right`, `to_top_left`, or `45deg`.
- `background_color`: str = None - hex "FF0000", "#FF0000", "FF000080" (with alpha), or named color
- `color`: str = "FFFFFF" - text/foreground color
- `border_color`: str = "555555"

Named colors: black, white, red, green, blue, yellow, cyan, gray, silver, lime, purple, teal, navy, orange, pink, brown, gold

## Font

- `font_size`: int/float = 16
- `font_style`: str = "normal" - "normal", "italic"
- `font_weight`: str = "normal" - "normal", "bold"
- `font_family`: str = "" - system font name
- `text_align`: str = "left" - "left", "center", "right"
- `white_space`: str = "normal" - "normal" (wraps to container), "nowrap" (no wrapping)

## Border

- `border_width`: int - all sides
- `border_top`, `border_right`, `border_bottom`, `border_left`: int - individual sides
- `border_radius`: int/float/tuple - single value or tuple for individual corners
- `border_color`: str = "555555"

## Opacity

- `opacity`: float - 0.0 to 1.0, cascades to children

## Scrolling

- `overflow`: str - "hidden", "scroll"
- `overflow_x`, `overflow_y`: str - "hidden", "scroll"

## Interactivity

- `on_click`: callable - receives ClickEvent if handler accepts a parameter
- `on_change`: callable - for input_text, textarea, select, checkbox, switch. Receives ChangeEvent (SwitchEvent for switch).
- `on_submit`: callable - form only. Receives SubmitEvent(data={"input_id": "value", ...}) with all child input values. Also works with 0 args.
- `type`: str - button only. Use `type="submit"` inside a form to trigger the form's `on_submit`.
- `highlight_style`: dict - hover style e.g. {"background_color": "444444"}. Keys: background_color, border_color, color, fill, stroke
- `disabled`: bool - disables interactivity
- `disabled_style`: dict - style when disabled
- `draggable`: bool - makes element draggable
- `drag_handle`: bool - makes this element the drag handle for a draggable ancestor
- `autofocus`: bool - auto-focus input_text or textarea on mount

## Animation

- `transition`: dict - {"prop": duration_ms} or {"prop": (duration_ms, "easing")}
- `mount_style`: dict - initial style when element mounts (animates FROM these values)
- `unmount_style`: dict - style to animate TO before element unmounts

Easing: "linear", "ease_in", "ease_out", "ease_in_out", "ease_out_bounce"

## Identity

- `id`: str - unique identifier. Required for input_text, textarea, select. Used by refs.
- `key`: str - reconciliation key for dynamic lists
- `class_name`: str - for style block matching
- `z_index`: int = 0 - stacking order

## Other

- `drop_shadow`: tuple - (x_offset, y_offset, blur_x, blur_y, color) e.g. (0, 4, 8, 8, "00000088")
