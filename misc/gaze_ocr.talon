# Override other global commands (e.g. scrolling).
mode:command
-
<user.text> touch:
    user.move_cursor_to_word(text)
    mouse_click(0)
scroll down:
    user.move_cursor_to_gaze_point(0, -40)
    mouse_scroll(20)
