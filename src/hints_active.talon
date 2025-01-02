tag: user.ui_elements_hints_active
-
^<user.ui_elements_hint_target>$: user.ui_elements_hint_action(ui_elements_hint_target)

key(tab): user.ui_elements_hint_action("focus_next")
key(shift-tab): user.ui_elements_hint_action("focus_previous")
key(escape): user.ui_elements_hint_action("close")
key(up): user.ui_elements_hint_action("focus_previous")
key(down): user.ui_elements_hint_action("focus_next")