# Defaults

## Flexbox
Everything is `display: flex`. There is no other option currently.

### Layout
All elements default to `flex_direction: column` and `align_items: stretch` to mimic `display: block` behavior.
Please keep this in mind when using `justify_content` and `align_items`, as your default expectations may be different than HTML where `flex_direction` is `row` by default.

`align_items` stays `stretch` with `flex_direction: row` too, so children fill the row's height. Root elements (`screen`, `active_window`) default to `flex_start`.

## Box model
The box model is based on `box-sizing: border-box`, meaning if you define width or height, the border and padding are included in the size, not added in addition to the size.

## Text wrapping
Text wraps to its container width by default (`white_space: "normal"`), similar to web browsers. Use `white_space: "nowrap"` to prevent wrapping.

## Gap
`gap` is `0` by default, but if two text elements are vertically aligned, the default gap is `16`.

## Constants
See [constants](../../src/constants.py) for available constants.
