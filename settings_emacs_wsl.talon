os: windows
app: emacs
title: /\(Ubuntu\)$/
-
settings():
    # Clipboard appears to cause hangs on WSL in Windows 11.
    user.context_sensitive_dictation = 0