setting mouse: user.ui_elements_set_state("active_tab", "mouse")
setting settings: user.ui_elements_set_state("active_tab", "game_settings")
setting tracking: user.ui_elements_set_state("active_tab", "eye_tracking")
setting actions: user.ui_elements_set_state("active_tab", "actions")
setting noises: user.ui_elements_set_state("active_tab", "noises")
setting face: user.ui_elements_set_state("active_tab", "face_actions")

frog test : user.test_frog()
frog refresh : user.test_frog_refresh()