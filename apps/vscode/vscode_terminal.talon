app: vscode
# Looks for special string in window title.
# NOTE: This requires you to add a special setting to your VSCode settings.json
# See [our vscode docs](./README.md#terminal)
win.title: /focus:\[Terminal\]/
-
tag(): terminal
screen up: key(shift-pgup)
screen down: key(shift-pgdown)
last | preev: key(ctrl-r)
next: key(ctrl-s)
