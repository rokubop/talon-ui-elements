# Properties

Properties go inside parentheses after the element name. For example, `div(width="100%", background_color="red")[...]`. If there are no properties, use an empty call `div()[...]`.

Properties mostly match standard CSS properties.

- [Properties](#properties)
  - [Layout Properties](#layout-properties)
  - [Sizing Properties](#sizing-properties)
  - [Spacing Properties](#spacing-properties)
  - [Border Properties](#border-properties)
  - [Color \& Visual Properties](#color--visual-properties)
  - [Positioning Properties](#positioning-properties)
  - [Overflow \& Scrolling Properties](#overflow--scrolling-properties)
  - [Text \& Font Properties](#text--font-properties)
  - [Interaction Properties](#interaction-properties)
  - [Focus \& Highlight Properties](#focus--highlight-properties)
  - [Identification Properties](#identification-properties)
  - [Window-Specific Properties](#window-specific-properties)
  - [Checkbox-Specific Properties](#checkbox-specific-properties)
  - [Link-Specific Properties](#link-specific-properties)
  - [Table-Specific Properties](#table-specific-properties)
  - [Icon-Specific Properties](#icon-specific-properties)
  - [Cursor-Specific Properties](#cursor-specific-properties)
  - [Screen-Specific Properties](#screen-specific-properties)
  - [SVG-Specific Properties](#svg-specific-properties)

## Layout Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| align_items | "center", "flex_start", "flex_end", "stretch" | "stretch" | How items are aligned in the cross axis |
| align_self | "center", "flex_start", "flex_end", "stretch" | None | Align self in the cross axis |
| flex | int | None | `1` to stretch fully. |
| flex_direction | "row", "column" | "column" | "row" to align items horizontally, "column" to align items vertically. Note that the default is "column", which is different than HTML/CSS which defaults to "row". |
| gap | int | None | Gap between children. Always applicable since every element is flex |
| justify_content | "center", "flex_start", "flex_end", "space_between", "space_evenly" | "flex_start" | Justify content in the main axis |

## Sizing Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| height | Union[int, str, float] | 0 | int/float value, or you can specify "100%" as a string. |
| max_height | int | None | Max height |
| max_width | int | None | Max width |
| min_height | int | None | Min height |
| min_width | int | None | Min width |
| width | Union[int, str, float] | 0 | int/float value, or you can specify "100%" as a string. |

## Spacing Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| margin | int | 0 | Uniform margin width |
| margin_bottom | int | 0 | Bottom margin |
| margin_left | int | 0 | Left margin |
| margin_right | int | 0 | Right margin |
| margin_top | int | 0 | Top margin |
| padding | int | 0 | Uniform padding width |
| padding_bottom | int | 0 | Bottom padding |
| padding_left | int | 0 | Left padding |
| padding_right | int | 0 | Right padding |
| padding_top | int | 0 | Top padding |

## Border Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| border_color | str | "#555555" | Border color. Use 6-char hex ("#FFFFFF") or 8-char with opacity ("#FFFFFFFF" for fully visible, "#FFFFFF00" for invisible) |
| border_bottom | int | 0 | Bottom border width |
| border_left | int | 0 | Left border width |
| border_radius | Union[int, float, tuple] | 0 | For rounded corners. Can be a single int for uniform radius, or a tuple of 4 values `(top_left, top_right, bottom_right, bottom_left)` for per-corner radii. Example: `border_radius=20` or `border_radius=(30, 10, 30, 10)` |
| border_right | int | 0 | Right border width |
| border_top | int | 0 | Top border width |
| border_width | int | None | Uniform border width value (shorthand) |

## Color & Visual Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| background_color | str | None | Background color. Use 6-char hex ("#FFFFFF") or 8-char with opacity ("#FFFFFFFF" for fully visible, "#FFFFFF00" for invisible). Also supports color names like "red", "blue", etc. |
| color | str | "#FFFFFF" | Text color - Cascades to children. Use 6-char hex ("#FFFFFF") or 8-char with opacity ("#FFFFFFFF" for fully visible, "#FFFFFF00" for invisible) |
| drop_shadow | tuple[int, int, int, int, str] | None | Drop shadow as `(x_offset, y_offset, blur_x, blur_y, color)` |
| opacity | float | None | For example `0.7`. Affects children as well. To only affect one node, use 8-char hex color with opacity instead (e.g., "#FFFFFF80" for 50% opacity) |

## Positioning Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| bottom | Union[int, str, float] | None | Used with `"position"` property. Inset from the bottom. e.g. `0`, `50`, `"25%"`, `"100%"` |
| left | Union[int, str, float] | None | Used with `"position"` property. Inset from the left. e.g. `0`, `50`, `"25%"`, `"100%"` |
| position | "static", "relative", "absolute", "fixed" | "static" | Positioning of element. |
| right | Union[int, str, float] | None | Used with `"position"` property. Inset from the right. e.g. `0`, `50`, `"25%"`, `"100%"` |
| top | Union[int, str, float] | None | Used with `"position"` property. Inset from the top. e.g. `0`, `50`, `"25%"`, `"100%"` |
| z_index | int | 0 | higher value will render on top of lower values. Cascades to children |

## Overflow & Scrolling Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| overflow | "visible", "hidden", "scroll", "auto" | "visible" | Behavior of content that exceeds bounds |
| overflow_x | "visible", "hidden", "scroll", "auto" | "visible" | Behavior of content that exceeds bounds in x direction |
| overflow_y | "visible", "hidden", "scroll", "auto" | "visible" | Behavior of content that exceeds bounds in y direction |

## Text & Font Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| font_family | str | "" | Font family |
| font_size | Union[int, float] | 16 | Font size |
| font_weight | "normal", "bold" | "normal" | Font weight |
| for_id | str | None | Associates a label with an input (for `text` element) |
| stroke_color | str | None | Text stroke/outline color (for `text` element) |
| stroke_width | Union[int, float] | None | Text stroke/outline width (for `text` element) |
| text_align | "left", "center", "right" | "left" | Text alignment |

## Interaction Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| autofocus | bool | False | Autofocus for `input_text` or `button` |
| disabled | bool | False | Whether element is disabled (for interactive elements) |
| disabled_style | dict | None | Style overrides when disabled |
| draggable | bool | False | Whether element can be dragged |
| drag_handle | bool | False | Treat this area as the drag handle for a parent draggable |
| on_change | callable | None | On change callback, for `input_text`, `checkbox`, `switch`. Accepts 1 event argument. |
| on_click | callable | None | On click callback, for `button`. Accepts 1 event argument. |
| on_drag_end | callable | None | Callback when drag ends. Accepts 1 event argument. |
| value | str | None | Value of `input_text` |

## Focus & Highlight Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| focus_outline_color | str | "#FFFFFF" | Focus outline color - for keyboard accessibility and after you have interacted with an element. Cascades to children. Use 8-char hex for opacity |
| focus_outline_width | Union[int, float] | 1.5 | Focus outline width - for keyboard accessibility and after you have interacted with an element. Cascades to children |
| highlight_color | str | `{color}33` | Highlight color (on hover/interaction). Cascades to children. Defaults to text color with 20% opacity |
| highlight_style | dict | None | Style overrides when highlighted. Valid keys: `background_color`, `border_color`, `color`, `fill`, `stroke`. Animates smoothly when `transition` is also set. Auto-generated for interactive nodes with `transition` + color properties |

## Identification Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| class_name | str | None | CSS-like class name for styling/identification |
| id | str | None | Unique identifier for the element |
| key | str | None | Key for element identity in lists (for reconciliation) |

## Window-Specific Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| drag_title_bar_only | bool | True | Whether window can only be dragged by title bar |
| minimized | bool | False | Whether window is minimized |
| minimized_body | callable | None | Function that returns alternate body when minimized |
| minimized_style | dict | None | Style overrides when minimized |
| on_close | callable | None | Callback when window is closed |
| on_minimize | callable | None | Callback when window is minimized |
| on_restore | callable | None | Callback when window is restored from minimized state |
| show_close | bool | True | Whether to show close button |
| show_minimize | bool | True | Whether to show minimize button |
| show_title_bar | bool | True | Whether to show title bar |
| title | str | None | Window title text |
| title_bar_style | dict | None | Style overrides for title bar |

## Checkbox-Specific Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| checked | bool | False | Whether checkbox is checked |
| on_change | callable | None | Callback when checked state changes |

## Link-Specific Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| close_on_click | bool | False | Whether to close UI when link is clicked |
| minimize_on_click | bool | False | Whether to minimize UI when link is clicked |
| url | str | None | URL to open when clicked |

## Table-Specific Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| colspan | int | 1 | Number of columns cell should span (for `td`, `th`) |

## Icon-Specific Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| name | str | Required | Icon name (see icons documentation for available icons) |
| size | Union[int, float] | 24 | Icon size (affects both width and height) |
| fill | Union[str, bool] | None | Fill color. Use `False` for no fill. Use 8-char hex for opacity |
| stroke | Union[str, bool] | None | Stroke color. Use `False` for no stroke. Use 8-char hex for opacity |
| stroke_width | Union[int, float] | None | Stroke width |
| stroke_linecap | "butt", "round", "square" | None | Stroke line cap |
| stroke_linejoin | "miter", "round", "bevel" | None | Stroke line join |

## Cursor-Specific Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| refresh_rate | int | 16 | Update frequency in milliseconds for `cursor` element (16ms ≈ 60fps) |

## Screen-Specific Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| screen | int | 0 | Specify the screen index, only applicable to `screen` element |

## SVG-Specific Properties

| Property | Type | Default | Description |
| -- | -- | -- | -- |
| fill | Union[str, bool] | None | Fill color. Use `False` for no fill. Use 8-char hex for opacity |
| size | Union[int, float] | 24 | affects both width and height (for `svg` element) |
| stroke | Union[str, bool] | None | Stroke color. Use `False` for no stroke. Use 8-char hex for opacity |
| stroke_linecap | "butt", "round", "square" | "round" | Stroke line cap |
| stroke_linejoin | "miter", "round", "bevel" | "round" | Stroke line join |
| stroke_width | Union[int, float] | 2 | Stroke width |
| view_box | str | "0 0 24 24" | View box |