# These are available globally (in command mode)
mode: command
-

^draft open:
    # Do this toggle so we can have focus when saying 'draft open'
    user.draft_hide()
    user.draft_show()

^draft open <user.draft_window_position>:
    # Do this toggle so we can have focus when saying 'draft open'
    user.draft_hide()
    user.draft_show()
    user.draft_named_move(draft_window_position)

^draft open small:
    # Do this toggle so we can have focus when saying 'draft open'
    user.draft_hide()
    user.draft_show()
    user.draft_resize(600, 200)

^draft open large:
    # Do this toggle so we can have focus when saying 'draft open'
    user.draft_hide()
    user.draft_show()
    user.draft_resize(800, 500)

^draft empty: user.draft_show("")

^draft edit:
    text = edit.selected_text()
    key(backspace)
    user.draft_show(text)

^draft edit all:
    edit.select_all()
    text = edit.selected_text()
    key(backspace)
    user.draft_show(text)
