app: google_docs
-

settings():
    user.accessibility_dictation = true

please [<user.prose>]$:
    key(alt-/)
    insert(prose or "")

please <user.prose> enter$:
    key(alt-/)
    insert(prose)
    sleep(500ms)
    key(enter)
