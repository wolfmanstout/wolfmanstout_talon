mode: command
mode: user.dictation_command
app: gmail
-
[suggest] keep: key(tab)

touch expand (all | al):
    user.mouse_helper_position_save()
    user.mouse_helper_move_image_relative("2023-09-26_12.58.32.898292.png", 0)
    sleep(0.05)
    mouse_click(0)
    sleep(0.05)
    user.mouse_helper_position_restore()

touch collapse (all | al):
    user.mouse_helper_position_save()
    user.mouse_helper_move_image_relative("2023-08-12_16.01.41.668613.png", 0)
    sleep(0.05)
    mouse_click(0)
    sleep(0.05)
    user.mouse_helper_position_restore()

touch discard:
    user.mouse_helper_position_save()
    user.mouse_helper_move_image_relative("2023-08-25_11.31.37.425605.png", 0, 0, 0, user.mouse_helper_calculate_relative_rect("0 -200 -0 -0"))
    sleep(0.05)
    mouse_click(0)
    sleep(0.05)
    user.mouse_helper_position_restore()

touch message options:
    user.mouse_helper_position_save()
    user.mouse_helper_move_image_relative("2023-10-09_17.20.54.079391.png", 0, 0, 0, user.mouse_helper_calculate_relative_rect("0 -200 -0 -0"))
    sleep(0.05)
    mouse_click(0)
    sleep(0.05)
    user.mouse_helper_position_restore()
