app: vscode
win.title: /\[WSL:.*focus:\[Terminal\]/
-
settings():
    # Selection does not work properly here.
    user.context_sensitive_dictation = false
    # Needed for Claude Code "scratch that" (at least)
    key_wait = 10.0
