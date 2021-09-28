<user.text> touch:
    user.move_cursor_to_word(text)
    mouse_click(0)
scroll down:
    user.move_cursor_to_gaze_point(0, -40)
    mouse_scroll(20)

# (I\pronoun|eye) move: 'move_to_gaze_point'()
# (I\pronoun|eye) (touch|click) [left]: 'move_to_gaze_point'()+<left>
# (I\pronoun|eye) (touch|click) right: 'move_to_gaze_point'()+<right>
# (I\pronoun|eye) (touch|click) middle: 'move_to_gaze_point'()+<middle>
# (I\pronoun|eye) (touch|click) [left] twice: 'move_to_gaze_point'()+<left:2>
# (I\pronoun|eye) (touch|click) hold: 'move_to_gaze_point'()+<left:down>
# (I\pronoun|eye) (touch|click) release: 'move_to_gaze_point'()+<left:up>
# (I\pronoun|eye) control (touch|click): 'move_to_gaze_point'()+['ctrl:down']+<left>+['ctrl:up']
# (I\pronoun|eye) connect: 'connect'()
# (I\pronoun|eye) disconnect: 'disconnect'()
# (I\pronoun|eye) print position: 'print_gaze_point'()
# scroll up: '"scroll up": Function(lambda: tracker.move_to_gaze_point((0, 40))) + Mouse("wheelup:7"),'()+<wheelup:7>
# scroll up half: '"scroll up half": Function(lambda: tracker.move_to_gaze_point((0, 40))) + Mouse("wheelup:4"),'()+<wheelup:4>
# scroll down: '"scroll down": Function(lambda: tracker.move_to_gaze_point((0, -40))) + Mouse("wheeldown:7"),'()+<wheeldown:7>
# scroll down half: '"scroll down half": Function(lambda: tracker.move_to_gaze_point((0, -40))) + Mouse("wheeldown:4"),'()+<wheeldown:4>
# scroll left: '"scroll left": Function(lambda: tracker.move_to_gaze_point((40, 0))) + Mouse("wheelleft:7"),'()+<wheelleft:7>
# scroll right: '"scroll right": Function(lambda: tracker.move_to_gaze_point((-40, 0))) + Mouse("wheelright:7"),'()+<wheelright:7>
# scroll start: '"scroll start": Function(lambda: scroller.start()),'()
# [scroll] stop: '"[scroll] stop": Function(lambda: scroller.stop()),'()
# scroll reset: '"scroll reset": Function(lambda: reset_scroller()),'()
# <text> move: MoveCursorToWordAction()
# <text> (touch|click) [left]: MoveCursorToWordAction()+<left>
# <text> (touch|click) right: MoveCursorToWordAction()+<right>
# <text> (touch|click) middle: MoveCursorToWordAction()+<middle>
# <text> (touch|click) [left] twice: MoveCursorToWordAction()+<left:2>
# <text> (touch|click) hold: MoveCursorToWordAction()+<left:down>
# <text> (touch|click) release: MoveCursorToWordAction()+<left:up>
# <text> control (touch|click): MoveCursorToWordAction()+['ctrl:down']+<left>+['ctrl:up']
# go before <text>: MoveTextCursorAction()
# go after <text>: MoveTextCursorAction()
# words before <text> delete: ['shift:down']+MoveTextCursorAction()+['shift:up']+['backspace']
# words after <text> delete: ['shift:down']+MoveTextCursorAction()+['shift:up']+['backspace']
# words <text> [through <text2>] delete: SelectTextAction()+['backspace']
# words before <text>: ['shift:down']+MoveTextCursorAction()+['shift:up']
# words after <text>: ['shift:down']+MoveTextCursorAction()+['shift:up']
# words <text> [through <text2>]: SelectTextAction()
# replace <text> with <replacement>: SelectTextAction()+'%(replacement)s'
