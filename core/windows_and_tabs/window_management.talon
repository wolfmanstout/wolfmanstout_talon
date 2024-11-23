mode: command
mode: user.dictation_command
-
(window | win) (new | open): app.window_open()
(window | win) next: app.window_next()
(window | win) last: app.window_previous()
(window | win) close: app.window_close()
(window | win) hide: app.window_hide()
swap$: user.switcher_focus_last()

snap <user.window_snap_position>: user.snap_window(window_snap_position)
snap next [screen]: user.move_window_next_screen()
snap last [screen]: user.move_window_previous_screen()
snap screen <number_small>: user.move_window_to_screen(number_small)
snap <user.running_applications> <user.window_snap_position>:
    user.snap_app(running_applications, window_snap_position)
# <user.running_applications> is here twice to require at least two applications.
snap <user.window_split_position> <user.running_applications> <user.running_applications>+:
    user.snap_layout(window_split_position, running_applications_list)
snap <user.running_applications> [screen] <number_small>:
    user.move_app_to_screen(running_applications, number_small)
