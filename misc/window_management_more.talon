mode: command
mode: dictation
-
{user.docked_apps} win [<phrase>]:
    # Select the first window.
    key(win:down)
    sleep(100ms)
    key("{docked_apps}")
    sleep(100ms)
    key(win:up)
    sleep(400ms)
    user.parse_phrase(phrase or "")
<user.known_windows> win [<phrase>]:
    user.switcher_focus_window(known_windows)
    sleep(400ms)
    user.parse_phrase(phrase or "")
swap$: key(alt-tab)
show desktop$: key(win-d)
