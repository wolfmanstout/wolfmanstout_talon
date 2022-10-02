(window | win) (new | open): app.window_open()
(window | win) next: app.window_next()
(window | win) last: app.window_previous()
(window | win) close: app.window_close()

snap <user.window_snap_position>: user.snap_window(window_snap_position)
snap next [screen]: user.move_window_next_screen()
snap last [screen]: user.move_window_previous_screen()
snap screen <number_small>: user.move_window_to_screen(number_small)
snap <user.running_applications> <user.window_snap_position>:
    user.snap_app(running_applications, window_snap_position)
snap <user.running_applications> [screen] <number_small>:
    user.move_app_to_screen(running_applications, number_small)
