from talon import Module

mod = Module()
mod.tag("ui_elements_typing", desc="Active when typing in a custom canvas text input")

mod.setting("ui_elements_scale", type=float, default=1.0, desc="Global UI scale multiplier")
mod.setting("ui_elements_hints_show", type=bool, default=True)
mod.setting("ui_elements_hints_size", type=int, default=12)
mod.setting("ui_elements_hints_button_first_char", type=str, default="b")
mod.setting("ui_elements_hints_input_text_first_char", type=str, default="i")
mod.setting("ui_elements_hints_link_first_char", type=str, default="l")
mod.setting("ui_elements_text_subpixel", type=bool, default=True, desc="Place glyphs at fractional x positions instead of snapping them to whole pixels. Evens out letter spacing")
mod.setting("ui_elements_text_hinting", type=str, default="", desc="Glyph hinting. Empty keeps Skia's default: stems snap to the pixel grid, crisp but uneven in weight. 'none' disables snapping: softer, but every letter renders alike")
mod.setting("ui_elements_scroll_speed", type=int, default=45)
mod.setting("ui_elements_smooth_scroll_duration", type=int, default=80, desc="Smooth scroll duration in ms (0 to disable)")
