# Properties

Properties go inside parentheses after the element name. For example, `div(width="100%", background_color="red")[...]`. If there are no properties, use an empty call `div()[...]`.

See [properties.py](../src/properties.py) for the full list of properties per element.

Properties mostly match standard CSS properties.

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| align_items | "center", "flex_start", "flex_end", "stretch" | "stretch" | How items are aligned in the cross axis |
| align_self | "center", "flex_start", "flex_end", "stretch" | "stretch" | Align self in the cross axis |
| autofocus | bool | False | Autofocus for `input_text` or `button` |
| background_color | str | None | Background color - 3, 4, 6 char hex or word. You can also use 8 chars where the last 2 refer to opacity. |
| border_color | str | "555555" | Border color |
| border_left | int | None | Left border width |
| border_right | int | None | Right border width |
| border_top | int | None | Top border width |
| border_bottom | int | None | Bottom border width |
| border_radius | int | 0 | For rounded corners |
| border_width | int | None | Uniform border width value |
| bottom | Union[int, str] | None | Used with `"position"` property. Inset from the bottom. e.g. `0`, `50`, `"25%"`, `"100%"` |
| color | str | "FFFFFF" | Text color - Cascades to children |
| draggable | bool | False | Draggable for `div` |
| drag_handle | bool | False | Treat this area as the drag handle for a parent draggable |
| flex_direction | "row" or "column" | "column" | "row" to align items horizontally, "column" to align items vertically. Note that the default is "column", which is different than HTML/CSS which defaults to "row". |
| flex | int | None | `1` to stretch fully. |
| focus_outline_color | str | None | Focus outline color - for keyboard accessibility and after you have interacted with an element. |
| focus_outline_width | int | 2 | Focus outline width - for keyboard accessibility and after you have interacted with an element. |
| font_family | str | "" | Font family |
| font_size | int | 16 | Font size |
| font_weight | "normal", "bold" | "normal" | Font weight |
| gap | int | 0 or 16 | Gap between children - `16` if two texts are stacked vertically. Always applicable since every element is flex |
| height | Union[int, str] | 0 | int value, or you can specify "100%" as a string. |
| highlight_color | str | None | Highlight color - Cascades to children |
| id | str | None | ID |
| justify_content | "center", "flex_start", "flex_end", "space_between", "space_evenly" | "flex_start" | Justify content in the main axis |
| key | str | None | Key |
| left | Union[int, str] | None | Used with `"position"` property. Inset from the left. e.g. `0`, `50`, `"25%"`, `"100%"` |
| margin | Margin | 0 | Uniform margin width |
| margin_bottom | int | 0 | Bottom margin |
| margin_left | int | 0 | Left margin |
| margin_right | int | 0 | Right margin |
| margin_top | int | 0 | Top margin |
| max_height | int | None | Max height |
| max_width | int | None | Max width |
| min_height | int | None | Min height |
| min_width | int | None | Min width |
| on_change | callable | None | On change callback, for `input_text`. Accepts 1 event argument. |
| on_click | callable | None | On click callback, for `button`. Accepts 1 event argument. |
| opacity | float | None | For example `0.7`. Affects children as well. To only affect one node, use the alpha on the color or background_color instead by specifiying 8 digits instead of 6. |
| overflow | "visible", "scroll", "auto" | "visible" | Behavior of content that exceeds bounds |
| overflow_y | "visible", "scroll", "auto" | "visible" | Behavior of content that exceeds bounds in y direction |
| overflow_x | "visible", "scroll", "auto" | "visible" | Behavior of content that exceeds bounds in x direction |
| padding | Padding | 0 | Uniform padding width |
| padding_bottom | int | 0 | Bottom padding |
| padding_left | int | 0 | Left padding |
| padding_right | int | 0 | Right padding |
| padding_top | int | 0 | Top padding |
| position | "static", "relative", "absolute", "fixed" | "static" | Positioning of element. |
| right | Union[int, str] | None | Used with `"position"` property. Inset from the right. e.g. `0`, `50`, `"25%"`, `"100%"` |
| screen | int | 0 | Specify the screen index, only applicable to `screen` element |
| top | Union[int, str] | None | Used with `"position"` property. Inset from the top. e.g. `0`, `50`, `"25%"`, `"100%"` |
| text_align | "left", "center", "right" | "left" | Text alignment |
| value | str | None | Value of `input_text` |
| width | Union[int, str] | 0 | int value, or you can specify "100%" as a string. |
| z_index | int | 0 | higher value will render on top of lower values |

# SVG specific properties
| Property | Type | Default | Description |
| -- | -- | -- | -- |
| fill | str | None | Fill color |
| stroke | str | None | Stroke color |
| stroke_width | int | None | Stroke width |
| stroke_linecap | "butt", "round", "square" | "round" | Stroke line cap |
| stroke_linejoin | "miter", "round", "bevel" | "round" | Stroke line join |
| size | int | 24 | affects both width and height |
| view_box | str | "0 0 24 24" | View box |