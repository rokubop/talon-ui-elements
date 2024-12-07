# Properties

Properties go inside parentheses after the element name. For example, `div(width="100%", background_color="red")[...]`. If there are no properties, use an empty call `div()[...]`.

Properties mostly match standard CSS properties.

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| align_items | "center", "flex_start", "flex_end", "stretch" | "stretch" | How items are aligned in the cross axis |
| align_self | "center", "flex_start", "flex_end", "stretch" | "stretch" | Align self in the cross axis |
| background_color | str | None | Background color - 3, 4, 6 char hex or word. You can also use 8 chars where the last 2 refer to opacity. |
| border_color | str | "555555" | Border color |
| border_left | int | None | Left border width |
| border_right | int | None | Right border width |
| border_top | int | None | Top border width |
| border_bottom | int | None | Bottom border width |
| border_radius | int | 0 | For rounded corners |
| border_width | int | None | Uniform border width value |
| color | str | "FFFFFF" | Text color |
| flex_direction | "row" or "column" | "column" | "row" to align items horizontally, "column" to align items vertically. Note that the default is "column", which is different than HTML/CSS which defaults to "row". |
| flex | int | None | `1` to stretch fully. |
| font_family | str | "" | Font family |
| font_size | int | 16 | Font size |
| font_weight | "normal", "bold" | "normal" | Font weight |
| gap | int | None | Gap between children |
| height | Union[int, str] | 0 | Height |
| highlight_color | str | None | Highlight color |
| id | str | None | ID |
| justify_content | "center", "flex_start", "flex_end", "justify_between" | "flex_start" | Justify content in the main axis |
| key | str | None | Key |
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
| opacity | float | None | Opacity |
| padding | Padding | 0 | Uniform padding width |
| padding_bottom | int | 0 | Bottom padding |
| padding_left | int | 0 | Left padding |
| padding_right | int | 0 | Right padding |
| padding_top | int | 0 | Top padding |
| value | str | None | Value of `input_text` |
| width | Union[int, str] | 0 | Width |