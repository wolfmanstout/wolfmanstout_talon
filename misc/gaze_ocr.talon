(eye | I) move: user.move_cursor_to_gaze_point()
(eye | I) (touch | click) [left]:
    user.move_cursor_to_gaze_point()
    mouse_click(0)
(eye | I) (touch | click) right:
    user.move_cursor_to_gaze_point()
    mouse_click(1)
(eye | I) (touch | click) middle:
    user.move_cursor_to_gaze_point()
    mouse_click(2)
(eye | I) control (touch | click):
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
# scroll left: '"scroll left": Function(lambda: tracker.move_to_gaze_point((40, 0))) + Mouse("wheelleft:7"),'()+<wheelleft:7>
# scroll right: '"scroll right": Function(lambda: tracker.move_to_gaze_point((-40, 0))) + Mouse("wheelright:7"),'()+<wheelright:7>
# scroll start: '"scroll start": Function(lambda: scroller.start()),'()
# [scroll] stop: '"[scroll] stop": Function(lambda: scroller.stop()),'()
# scroll reset: '"scroll reset": Function(lambda: reset_scroller()),'()

<user.onscreen_word> move: user.move_cursor_to_word(onscreen_word)
<user.onscreen_word> (touch | click) [left]:
    user.move_cursor_to_word(onscreen_word)
    mouse_click(0)
<user.onscreen_word> (touch | click) right:
    user.move_cursor_to_word(onscreen_word)
    mouse_click(1)
<user.onscreen_word> (touch | click) middle:
    user.move_cursor_to_word(onscreen_word)
    mouse_click(2)
<user.onscreen_word> control (touch | click):
    user.move_cursor_to_word(onscreen_word)
    key(ctrl:down)
    mouse_click(0)
    key(ctrl:up)
go before <user.onscreen_word>: user.move_text_cursor_to_word(onscreen_word, "before")
go after <user.onscreen_word>: user.move_text_cursor_to_word(onscreen_word, "after")
words <user.onscreen_text> [through <user.onscreen_word>] delete:
    user.select_text(onscreen_text, onscreen_word or "", 1)
    key(backspace)
words before <user.onscreen_word>:
    key(shift:down)
    user.move_text_cursor_to_word(onscreen_word, "before")
    key(shift:up)
words after <user.onscreen_word>:
    key(shift:down)
    user.move_text_cursor_to_word(onscreen_word, "after")
    key(shift:up)
words <user.onscreen_text> [through <user.onscreen_word>]:
    user.select_text(onscreen_text, onscreen_word or "")
replace <user.onscreen_word> with <user.onscreen_word>:
    user.select_text(onscreen_word_1)
    insert(onscreen_word_2)
