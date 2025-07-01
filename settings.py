from talon import Module

mod = Module()

mod.setting("ui_elements_hints_show", type=bool, default=True)
mod.setting("ui_elements_hints_size", type=int, default=12)
mod.setting("ui_elements_hints_button_first_char", type=str, default="b")
mod.setting("ui_elements_hints_input_text_first_char", type=str, default="i")
mod.setting("ui_elements_hints_link_first_char", type=str, default="l")
mod.setting("ui_elements_scroll_speed", type=int, default=45)
