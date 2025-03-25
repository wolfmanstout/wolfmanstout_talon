mode: command
mode: user.dictation_command
os: windows
-
{user.docked_apps} win$: key("win-{docked_apps}")
{user.docked_apps} admin win$: key("win-ctrl-shift-{docked_apps}")
{user.docked_apps} new win$: key("win-shift-{docked_apps}")
<user.known_windows> win$: user.switcher_focus_window(known_windows)
show desktop$: key(win-d)
show (apps | windows)$: key(win-tab)

(window | win) (restore | minimize | min): key(win:down down down win:up)
(window | win) (maximize | max): key(win:down up up win:up)
windows search: key(win-s)
windows run: key(win-r)
windows desktop: key(win-d)
windows explorer: key(win-e)
