# Icons and SVGs

The "icon" ui_element defaults to 24 "size" property, and are built using `actions.user.ui_elements_svg` behind the scenes, based on HTML from https://iconsvg.xyz/, so if you don't find an icon you like, you can make one yourself.

- [Icons and SVGs](#icons-and-svgs)
  - [Icons](#icons)
  - [Default properties](#default-properties)
  - [Available icons](#available-icons)
  - [SVGs](#svgs)
  - [Convert HTML SVG to ui\_elements code](#convert-html-svg-to-ui_elements-code)

## Icons

You can see some available icons by saying "elements test".

Usage:
```py
screen, div, icon = actions.user.ui_elements(["screen", "div", "icon"])

return screen()[
    div()[
        icon("arrow_down")
    ]
]
```

## Default properties
| Property | Default |
| -- | -- |
| `size` | 24 |
| `stroke_width` | 2 |
| `color` | "FFFFFF" |

## Available icons
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
file
folder
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
upload

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
Based on a standard `view_box="0 0 24 24"`. You can use `size` on the `svg` element to resize the whole thing, and `stroke_width` to change the stroke width.

Usage:
```py
screen = actions.user.ui_elements("screen")
svg, path, rect = actions.user.ui_elements(["svg", "path", "rect"])

Usage:
```py
# copy icon
screen(align_items="center", justify_content="center")[
    svg()[
        rect(x=9, y=9, width=13, height=13, rx=2, ry=2),
        path(d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"),
    ]
]
```

## Convert HTML SVG to ui_elements code

You can convert HTML SVG code to ui_elements code by changing properties to snake case, and omitting most of the svg properties.
For example, here's the HTML SVG "copy" icon from https://iconsvg.xyz/:
```html
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
</svg>
```