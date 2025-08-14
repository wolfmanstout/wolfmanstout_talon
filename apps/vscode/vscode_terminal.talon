app: vscode
# Looks for special string in window title.
# NOTE: This requires you to add a special setting to your VSCode settings.json
# See [our vscode docs](./README.md#terminal)
win.title: /focus:\[Terminal\]/
-
settings():
    # Selection does not work properly here, at least in Claude Code.
    user.context_sensitive_dictation = false
    # Needed for Claude Code "scratch that" (at least)
    key_wait = 10.0

tag(): terminal
screen up: key(shift-pgup)
screen down: key(shift-pgdown)
last | preev: key(ctrl-r)
next: key(ctrl-s)
