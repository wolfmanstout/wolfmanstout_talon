tag: browser
title: /<docs.google.com>/
-
settings():
    user.clipboard_delay = "10ms"

please [<user.text>]$:
    key(alt-/)
    insert(user.text or "")
    sleep(100ms)
    key(enter)
