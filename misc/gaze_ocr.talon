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

<user.onscreen_text> move: user.move_cursor_to_word(onscreen_text)
<user.onscreen_text> (touch | click) [left]:
    user.move_cursor_to_word(onscreen_text)
    mouse_click(0)
<user.onscreen_text> (touch | click) right:
    user.move_cursor_to_word(onscreen_text)
    mouse_click(1)
<user.onscreen_text> (touch | click) middle:
    user.move_cursor_to_word(onscreen_text)
    mouse_click(2)
<user.onscreen_text> control (touch | click):
    user.move_cursor_to_word(onscreen_text)
    key(ctrl:down)
    mouse_click(0)
    key(ctrl:up)
go before <user.onscreen_text>: user.move_text_cursor_to_word(onscreen_text, "before")
go after <user.onscreen_text>: user.move_text_cursor_to_word(onscreen_text, "after")
words before <user.onscreen_text> delete:
    key(shift:down)
    user.move_text_cursor_to_word(onscreen_text, "before")
    key(shift:up)
    key(backspace)
words after <user.onscreen_text> delete:
    key(shift:down)
    user.move_text_cursor_to_word(onscreen_text, "after")
    key(shift:up)
    key(backspace)
words <user.onscreen_text> [through <user.onscreen_text>] delete:
    user.select_text(onscreen_text_1, onscreen_text_2 or "", 1)
    key(backspace)
words before <user.onscreen_text>:
    key(shift:down)
    user.move_text_cursor_to_word(onscreen_text, "before")
    key(shift:up)
words after <user.onscreen_text>:
    key(shift:down)
    user.move_text_cursor_to_word(onscreen_text, "after")
    key(shift:up)
words <user.onscreen_text> [through <user.onscreen_text>]:
    user.select_text(onscreen_text_1, onscreen_text_2 or "")
replace <user.onscreen_text> with <user.onscreen_text>:
    user.select_text(onscreen_text_1)
    insert(onscreen_text_2)
