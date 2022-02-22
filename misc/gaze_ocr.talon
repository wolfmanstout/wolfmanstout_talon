mode: command
mode: dictation
-
(eye | i) move: user.move_cursor_to_gaze_point()
(eye | i) (touch | click) [left]:
    user.move_cursor_to_gaze_point()
    mouse_click(0)
(eye | i) (touch | click) right:
    user.move_cursor_to_gaze_point()
    mouse_click(1)
(eye | i) (touch | click) middle:
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

<phrase> move: user.move_cursor_to_word(phrase)
<phrase> (touch | click) [left]:
    user.move_cursor_to_word(phrase)
    mouse_click(0)
<phrase> (touch | click) right:
    user.move_cursor_to_word(phrase)
    mouse_click(1)
<phrase> (touch | click) middle:
    user.move_cursor_to_word(phrase)
    mouse_click(2)
<phrase> control (touch | click):
    user.move_cursor_to_word(phrase)
    key(ctrl:down)
    mouse_click(0)
    key(ctrl:up)
go before <phrase>: user.move_text_cursor_to_word(phrase, "before")
go after <phrase>: user.move_text_cursor_to_word(phrase, "after")
words <phrase> [through <phrase>] delete:
    user.select_text(phrase_1, phrase_2 or "", 1)
    key(backspace)
words before <phrase>:
    key(shift:down)
    user.move_text_cursor_to_word_ignore_errors(phrase, "before")
    key(shift:up)
words after <phrase>:
    key(shift:down)
    user.move_text_cursor_to_word_ignore_errors(phrase, "after")
    key(shift:up)
words <phrase> [through <phrase>]:
    user.select_text(phrase_1, phrase_2 or "")
replace <phrase> with <user.prose>:
    user.select_text(phrase)
    insert(prose)
