mode: command
mode: dictation
tag: user.splits
-
split right: user.split_window_right()
split left: user.split_window_left()
split down: user.split_window_down()
split up: user.split_window_up()
split (vertically | vertical): user.split_window_vertically()
split (horizontally | horizontal): user.split_window_horizontally()
split flip: user.split_flip()
split max: user.split_maximize()
split reset: user.split_reset()
split window | buff split: user.split_window()
split clear: user.split_clear()
split clear all | buff focus: user.split_clear_all()
split next: user.split_next()
split (last | preev): user.split_last()
go split <number_small>: user.split_number(number_small)
