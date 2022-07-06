mode: command
mode: dictation
os: windows
-
{user.docked_apps} win$: key("win-ctrl-{docked_apps}")
{user.docked_apps} admin win$: key("win-ctrl-shift-{docked_apps}")
{user.docked_apps} new win$: key("win-shift-{docked_apps}")
<user.known_windows> win$: user.switcher_focus_window(known_windows)
swap$: key(alt-tab)
show desktop$: key(win-d)
show (apps | windows)$: key(win-tab)
