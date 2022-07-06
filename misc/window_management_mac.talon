mode: command
mode: dictation
os: mac
-
<user.running_applications> win$: user.switcher_focus(running_applications)
running list: user.switcher_toggle_running()
running close: user.switcher_hide_running()
launch <user.launch_applications>$: user.switcher_launch(launch_applications)
swap$: key(cmd-tab)
show desktop$: key(f11)
