from talon import Module

mod = Module()

mod.setting("ui_elements_hints_show", type=bool, default=True)
mod.setting("ui_elements_hints_size", type=int, default=12)
mod.setting("ui_elements_color", type=str, default="FFFFFF")
mod.setting("ui_elements_font_size", type=int, default=16)
mod.setting("ui_elements_border_color", type=str, default="555555")

# Requires Talon restart
mod.setting("ui_elements_highlight_color", type=str, default="FFFFFF66")
mod.setting("ui_elements_click_color", type=str, default="FFFFFF88")