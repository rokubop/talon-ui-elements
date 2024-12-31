# Icons and SVGs

All icons use `actions.user.ui_elements_svg` behind the scenes, meaning it's also very easy for you to make your own svg icons if this list doesn't cover your needs.

- [Icons and SVGs](#icons-and-svgs)
  - [Icons](#icons)
  - [SVGs](#svgs)

## Icons

You can checkout some example icons by saying "elements test".

Usage:
```py
div, icon = actions.user.ui_elements(["div", "icon"])

div()[
    icon("arrow_down")
]
```

Defaults to `size=24`, `stroke_width=2`, `color="FFFFFF"`.

| Icon name |
| -- |
arrow_down
arrow_left
arrow_right
arrow_up
chevron_down
chevron_left
chevron_right
chevron_up
close
download
edit
external_link
menu
mic
play
plus
check
copy
home
minus
more_horizontal
more_vertical
plus
settings
star

## SVGs

The following elements are supported for SVGs.

| Element | Description |
|---------|-------------|
| `svg` | Wrapper for SVG elements. |
| `path` | Accepts `d` attribute. |
| `circle` | Accepts `cx`, `cy`, and `r` attributes. |
| `rect` | Accepts `x`, `y`, `width`, `height`, `rx`, and `ry` attributes. |
| `line` | Accepts `x1`, `y1`, `x2`, and `y2` attributes. |
| `polyline` | Accepts `points` attribute. |
| `polygon` | Accepts `points` attribute. |

For the most part it matches the HTML SVG spec.
Based on a standard `view_box="0 0 24 24"`. You can use `size` to resize, and `stroke_width` to change the stroke width.

Usage:
```py
div = actions.user.ui_elements("div")
svg, path, rect = actions.user.ui_elements(["svg", "path", "rect"])

Usage:
```py
# copy icon
div()[
    svg()[
        rect(x=9, y=9, width=13, height=13, rx=2, ry=2),
        path(d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"),
    ]
]
```