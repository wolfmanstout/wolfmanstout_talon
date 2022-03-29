mode: command
mode: dictation
-
(eye | i) [cursor] move: user.move_cursor_to_gaze_point()
(eye | i) [left] (touch | click):
    user.move_cursor_to_gaze_point()
    mouse_click(0)
(eye | i) [left] double (touch | click):
    user.move_cursor_to_gaze_point()
    mouse_click(0)
    mouse_click(0)
(eye | i) right (touch | click):
    user.move_cursor_to_gaze_point()
    mouse_click(1)
(eye | i) middle (touch | click):
    user.move_cursor_to_gaze_point()
    mouse_click(2)
(eye | i) control (touch | click):
    user.move_cursor_to_gaze_point()
    key(ctrl:down)
    mouse_click(0)
    key(ctrl:up)

scroll up:
    user.move_cursor_to_gaze_point(0, 40)
    user.mouse_scroll_up()
    user.mouse_scroll_up()
    user.mouse_scroll_up()
    user.mouse_scroll_up()
    user.mouse_scroll_up()
    user.mouse_scroll_up()
    user.mouse_scroll_up()
scroll up half:
    user.move_cursor_to_gaze_point(0, 40)
    user.mouse_scroll_up()
    user.mouse_scroll_up()
    user.mouse_scroll_up()
    user.mouse_scroll_up()
scroll down:
    user.move_cursor_to_gaze_point(0, -40)
    user.mouse_scroll_down()
    user.mouse_scroll_down()
    user.mouse_scroll_down()
    user.mouse_scroll_down()
    user.mouse_scroll_down()
    user.mouse_scroll_down()
    user.mouse_scroll_down()
scroll down half:
    user.move_cursor_to_gaze_point(0, -40)
    user.mouse_scroll_down()
    user.mouse_scroll_down()
    user.mouse_scroll_down()
    user.mouse_scroll_down()
# parrot(shush):
#     user.move_cursor_to_gaze_point(0, -40)
#     user.power_momentum_scroll_down()
#     user.power_momentum_start(ts, 2.0)
# parrot(shush:repeat):
#     user.power_momentum_add(ts, power)
# parrot(shush:stop):
#     user.power_momentum_decaying()

# parrot(fff):
#     user.move_cursor_to_gaze_point(0, 40)
#     user.power_momentum_scroll_up()
#     user.power_momentum_start(ts, 2.0)
# parrot(fff:repeat):
#     user.power_momentum_add(ts, power)
# parrot(fff:stop):
#     user.power_momentum_decaying()

# scroll left: '"scroll left": Function(lambda: tracker.move_to_gaze_point((40, 0))) + Mouse("wheelleft:7"),'()+<wheelleft:7>
# scroll right: '"scroll right": Function(lambda: tracker.move_to_gaze_point((-40, 0))) + Mouse("wheelright:7"),'()+<wheelright:7>
# scroll start: '"scroll start": Function(lambda: scroller.start()),'()
# [scroll] stop: '"[scroll] stop": Function(lambda: scroller.stop()),'()
# scroll reset: '"scroll reset": Function(lambda: reset_scroller()),'()

cursor move <user.timestamped_prose>$: user.move_cursor_to_word(timestamped_prose)
[left] (touch | click) <user.timestamped_prose>$:
    user.move_cursor_to_word(timestamped_prose)
    mouse_click(0)
[left] double (touch | click) <user.timestamped_prose>$:
    user.move_cursor_to_word(timestamped_prose)
    mouse_click(0)
    mouse_click(0)
right (touch | click) <user.timestamped_prose>$:
    user.move_cursor_to_word(timestamped_prose)
    mouse_click(1)
middle (touch | click) <user.timestamped_prose>$:
    user.move_cursor_to_word(timestamped_prose)
    mouse_click(2)
control (touch | click) <user.timestamped_prose>$:
    user.move_cursor_to_word(timestamped_prose)
    key(ctrl:down)
    mouse_click(0)
    key(ctrl:up)
go before <user.timestamped_prose>$: user.move_text_cursor_to_word(timestamped_prose, "before")
go after <user.timestamped_prose>$: user.move_text_cursor_to_word(timestamped_prose, "after")
delete (word | words) <user.timestamped_prose> [through <user.timestamped_prose>]$:
    user.select_text(timestamped_prose_1, timestamped_prose_2 or "", 1)
    key(backspace)
select before <user.timestamped_prose>$:
    key(shift:down)
    user.move_text_cursor_to_word_ignore_errors(timestamped_prose, "before")
    key(shift:up)
select after <user.timestamped_prose>$:
    key(shift:down)
    user.move_text_cursor_to_word_ignore_errors(timestamped_prose, "after")
    key(shift:up)
select <user.timestamped_prose> [through <user.timestamped_prose>]$:
    user.select_text(timestamped_prose_1, timestamped_prose_2 or "")
replace <user.timestamped_prose> with <user.prose>$:
    user.select_text(timestamped_prose)
    insert(prose)
phones word <user.timestamped_prose>$:
    user.select_text(timestamped_prose)
    user.homophones_show_selection()
