mode: command
mode: dictation
-
control mouse: user.mouse_toggle_control_mouse()
zoom mouse: user.mouse_toggle_zoom_mouse()
camera overlay: user.mouse_toggle_camera_overlay()
run calibration: user.mouse_calibrate()
here [left] touch:
    mouse_click(0)
    # close the mouse grid if open
    user.grid_close()
    # End any open drags
    # Touch automatically ends left drags so this is for right drags specifically
    user.mouse_drag_end()

here right touch:
    mouse_click(1)
    # close the mouse grid if open
    user.grid_close()

here middle touch:
    mouse_click(2)
    # close the mouse grid
    user.grid_close()

#see keys.py for modifiers.
#defaults
#command
#control
#option = alt
#shift
#super = windows key
here <user.modifiers> touch:
    key("{modifiers}:down")
    mouse_click(0)
    key("{modifiers}:up")
    # close the mouse grid
    user.grid_close()
here <user.modifiers> right touch:
    key("{modifiers}:down")
    mouse_click(1)
    key("{modifiers}:up")
    # close the mouse grid
    user.grid_close()
here double touch:
    mouse_click()
    mouse_click()
    # close the mouse grid
    user.grid_close()
here triple touch:
    mouse_click()
    mouse_click()
    mouse_click()
    # close the mouse grid
    user.grid_close()
here [left] drag:
    user.mouse_drag(0)
    # close the mouse grid
    user.grid_close()
here right drag:
    user.mouse_drag(1)
    # close the mouse grid
    user.grid_close()
end drag: user.mouse_drag_end()
wheel down: user.mouse_scroll_down()
wheel down here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_down()
wheel tiny [down]: user.mouse_scroll_down(0.2)
wheel tiny [down] here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_down(0.2)
wheel downer: user.mouse_scroll_down_continuous()
wheel downer here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_down_continuous()
wheel up: user.mouse_scroll_up()
wheel up here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_up()
wheel tiny up: user.mouse_scroll_up(0.2)
wheel tiny up here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_up(0.2)
wheel upper: user.mouse_scroll_up_continuous()
wheel upper here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_up_continuous()
wheel gaze: user.mouse_gaze_scroll()
wheel gaze here:
    user.mouse_move_center_active_window()
    user.mouse_gaze_scroll()
wheel stop: user.mouse_scroll_stop()
wheel stop here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_stop()
wheel left: user.mouse_scroll_left()
wheel left here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_left()
wheel tiny left: user.mouse_scroll_left(0.5)
wheel tiny left here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_left(0.5)
wheel right: user.mouse_scroll_right()
wheel right here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_right()
wheel tiny right: user.mouse_scroll_right(0.5)
wheel tiny right here:
    user.mouse_move_center_active_window()
    user.mouse_scroll_right(0.5)
copy mouse position: user.copy_mouse_position()
curse no:
    # Command added 2021-12-13, can remove after 2022-06-01
    app.notify("Please activate the user.mouse_cursor_commands_enable tag to enable this command")

scroll up:
    user.move_cursor_to_gaze_point(0, 40)
    user.mouse_scroll_up()
scroll up half:
    user.move_cursor_to_gaze_point(0, 40)
    user.mouse_scroll_up(0.5)
scroll down:
    user.move_cursor_to_gaze_point(0, -40)
    user.mouse_scroll_down()
scroll down half:
    user.move_cursor_to_gaze_point(0, -40)
    user.mouse_scroll_down(0.5)
scroll left:
    user.move_cursor_to_gaze_point(40, 0)
    user.mouse_scroll_left()
scroll left half:
    user.move_cursor_to_gaze_point(40, 0)
    user.mouse_scroll_left(0.5)
scroll right:
    user.move_cursor_to_gaze_point(-40, 0)
    user.mouse_scroll_right()
scroll right half:
    user.move_cursor_to_gaze_point(-40, 0)
    user.mouse_scroll_right(0.5)
