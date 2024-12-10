# Defaults

## Flexbox
Everything is `display: flex`. There is no other option currently.

All elements default to `flex_direction: column` and `align_items: stretch` to mimic `display: block` behavior. If you specify `flex_direction: row`, the `align_items` will default to `flex_start`.

## Box model
The box model is based on `box-sizing: border-box`, meaning if you define width or height, the border and padding are included in the size, not added in addition to the size.

## Gap
`gap` is `0` by default, but if two text elements are vertically aligned, the default gap is `16`.

## Default Properties
| Property | Default |
| --- | --- |
| `color` | `FFFFFF` |
| `border_color` | `555555` |
| `font_size` | `16` |
| `flex_direction` | `column` |
| `align_items` | `stretch` |
| `justify_content` | `flex_start` |