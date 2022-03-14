mode: command
mode: dictation
-
{user.docked_apps} win [<phrase>]: key("win-ctrl-{docked_apps}")
{user.docked_apps} admin win [<phrase>]: key("win-ctrl-shift-{docked_apps}")
{user.docked_apps} new win [<phrase>]: key("win-shift-{docked_apps}")
<user.known_windows> win [<phrase>]:
    user.switcher_focus_window(known_windows)
    sleep(400ms)
    user.parse_phrase(phrase or "")
swap$: key(alt-tab)
show desktop$: key(win-d)
