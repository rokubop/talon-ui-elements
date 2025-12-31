# Icons

Icons default to 24 size and are built using SVG elements behind the scenes.

- [Preview](#preview)
- [Available Icons](#available-icons)
- [Icon Properties](#icon-properties)
- [Usage](#usage)
- [Make Your Own Icons](#make-your-own-icons)

## Preview

![Icons Preview](../examples/icons_svgs/icons_svgs_preview.png)

You can see available icons by saying "elements test".

## Available Icons

| Icon Name | Description |
| -- | -- |
| `arrow_down` | Down arrow |
| `arrow_left` | Left arrow |
| `arrow_right` | Right arrow |
| `arrow_up` | Up arrow |
| `check` | Checkmark |
| `chevron_down` | Down chevron |
| `chevron_left` | Left chevron |
| `chevron_right` | Right chevron |
| `chevron_up` | Up chevron |
| `clock` | Clock with hands |
| `close` | Close/X icon |
| `copy` | Copy/duplicate icon |
| `delta` | Delta/triangle symbol |
| `diamond` | Diamond shape |
| `download` | Download arrow |
| `edit` | Edit/pencil icon |
| `external_link` | External link arrow |
| `file` | File document |
| `file_text` | Text file with lines |
| `folder` | Folder icon |
| `home` | Home/house icon |
| `maximize` | Maximize window |
| `menu` | Hamburger menu (3 lines) |
| `mic` | Microphone |
| `minimize` | Minimize window |
| `minus` | Minus/subtract icon |
| `more_horizontal` | Three horizontal dots |
| `more_vertical` | Three vertical dots |
| `multiply` | Multiply/X icon |
| `pause` | Pause button (two bars) |
| `play` | Play button (triangle) |
| `plus` | Plus/add icon |
| `rotate_left` | Rotate counter-clockwise |
| `settings` | Settings/gear icon |
| `shrink` | Shrink/compress arrows |
| `star` | Star icon |
| `stop` | Stop button (square) |
| `trash` | Trash/delete icon |
| `upload` | Upload arrow |

## Icon Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| `name` | str | Required | Icon name (see available icons above) |
| `size` | Union[int, float] | 24 | Icon size (affects both width and height) |
| `color` | str | "#FFFFFF" | Icon color. Use 8-char hex for opacity (e.g., "#FFFFFF80" for 50% opacity) |
| `stroke_width` | Union[int, float] | 2 | Stroke width for the icon paths |
| `fill` | Union[str, bool] | None | Fill color. Use `False` for no fill. Some icons use fill by default |
| `stroke` | Union[str, bool] | None | Stroke color (overrides `color` if set). Use `False` for no stroke |
| `stroke_linecap` | "butt", "round", "square" | "round" | Stroke line cap style |
| `stroke_linejoin` | "miter", "round", "bevel" | "round" | Stroke line join style |

Icons also support all standard layout and positioning properties like `margin`, `padding`, `position`, etc.
## Usage

```py
screen, div, icon = actions.user.ui_elements(["screen", "div", "icon"])

return screen()[
    div()[
        # Basic icons
        icon("arrow_down"),
        icon("check"),

        # Custom size and color
        icon("settings", size=32, color="#FF0000"),

        # With transparency
        icon("star", color="#FFFF0080"),

        # Thicker stroke
        icon("arrow_right", stroke_width=3),

        # Filled icon
        icon("play", fill="#00FF00"),

        # With layout properties
        icon("menu", margin=10, padding=5)
    ]
]
```

## Make Your Own Icons

If you don't find an icon you need, you can create custom icons using SVG elements. See the [SVG documentation](concepts/svgs.md) for detailed information on creating custom graphics.

```py
svg, path = actions.user.ui_elements(["svg", "path"])

# Custom icon using SVG path
svg(size=24)[
    path(d="M12 2 L22 12 L12 22 L2 12 Z", fill="#FF0000")
]
```

You can also find SVG code for thousands of icons at:
- https://iconsvg.xyz/
- https://lucide.dev/icons

Then convert the SVG code to ui_elements syntax following the guide in [svgs.md](concepts/svgs.md#convert-html-svg-to-ui_elements-code).
