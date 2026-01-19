os: mac
app: iterm2
-
settings():
    user.accessibility_dictation = 1

tag(): terminal
# todo: filemanager support
#tag(): user.file_manager
tag(): user.generic_unix_shell
tag(): user.git
tag(): user.kubectl
tag(): user.tabs
# tag(): user.readline

screen up: key(shift-pageup)
screen down: key(shift-pagedown)
last | preev: key(ctrl-r)
next: key(ctrl-s)
cancel: key(ctrl-g)
go tab (last | preev) | tab back: key(ctrl-tab)
