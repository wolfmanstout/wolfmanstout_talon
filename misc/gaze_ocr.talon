eye move: user.move_cursor_to_gaze_point()
eye (touch | click) [left]:
    user.move_cursor_to_gaze_point()
    mouse_click(0)
eye (touch | click) right:
    user.move_cursor_to_gaze_point()
    mouse_click(1)
eye (touch | click) middle:
    user.move_cursor_to_gaze_point()
    mouse_click(2)
eye control (touch | click):
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

<user.text> move: user.move_cursor_to_word(text)
<user.text> (touch | click) [left]:
    user.move_cursor_to_word(text)
    mouse_click(0)
<user.text> (touch | click) right:
    user.move_cursor_to_word(text)
    mouse_click(1)
<user.text> (touch | click) middle:
    user.move_cursor_to_word(text)
    mouse_click(2)
<user.text> control (touch | click):
    user.move_cursor_to_word(text)
    key(ctrl:down)
    mouse_click(0)
    key(ctrl:up)
go before <user.text>: user.move_text_cursor_to_word(text, "before")
go after <user.text>: user.move_text_cursor_to_word(text, "after")
words before <user.text> delete:
    key(shift:down)
    user.move_text_cursor_to_word(text, "before")
    key(shift:up)
    key(backspace)
words after <user.text> delete:
    key(shift:down)
    user.move_text_cursor_to_word(text, "after")
    key(shift:up)
    key(backspace)
words <user.text> [through <user.text>] delete:
    user.select_text(text_1, text_2 or "", 1)
    key(backspace)
words before <user.text>:
    key(shift:down)
    user.move_text_cursor_to_word(text, "before")
    key(shift:up)
words after <user.text>:
    key(shift:down)
    user.move_text_cursor_to_word(text, "after")
    key(shift:up)
words <user.text> [through <user.text>]:
    user.select_text(text_1, text_2 or "")
replace <user.text> with <user.text>:
    user.select_text(text_1)
    insert(text_2)
