app: google_docs
-
settings():
    user.clipboard_delay = "10ms"

please [<user.text>]$:
    key(alt-/)
    insert(user.text or "")

please <user.text> enter$:
    key(alt-/)
    insert(user.text)
    key(enter)
