tag: user.ui_elements_hints_active
and win.title: /ui_elements/
-
^<user.ui_elements_hint_target>$: user.ui_elements_hint_action("click", ui_elements_hint_target)
focus <user.ui_elements_hint_target>: user.ui_elements_hint_action("focus", ui_elements_hint_target)

key(tab:down): user.ui_elements_key_action("focus_next", true)
key(tab:up): user.ui_elements_key_action("focus_next", false)
key(shift-tab:down): user.ui_elements_key_action("focus_previous", true)
key(shift-tab:up): user.ui_elements_key_action("focus_previous", false)
key(up:down): user.ui_elements_key_action("focus_previous", true)
key(up:up): user.ui_elements_key_action("focus_previous", false)
key(down:down): user.ui_elements_key_action("focus_next", true)
key(down:up): user.ui_elements_key_action("focus_next", false)
key(escape): user.ui_elements_key_action("close")
scroll down: user.ui_elements_scroll_action("down")
scroll up: user.ui_elements_scroll_action("up")
scroll [to] top: user.ui_elements_scroll_action("top")
scroll [to] bottom: user.ui_elements_scroll_action("bottom")
window close: user.ui_elements_key_action("close")

# other key code in /nodes/tree.py in on_key