toggle game keys: user.toggle_game_keys()
test jump:
    user.ui_elements_highlight_briefly("space")
    key(space)

test dash:
    user.ui_elements_highlight_briefly("q")
    key(q)

test heal:
    user.ui_elements_highlight_briefly("e")
    key(e)

# Hold highlight while shift is pressed
test sprint:
    user.ui_elements_highlight("shift")
    key(shift:down)

test sprint release:
    user.ui_elements_unhighlight("shift")
    key(shift:up)