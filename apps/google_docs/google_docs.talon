app: google_docs
-
please [<user.text>]$:
    key(alt-/)
    insert(user.text or "")

please <user.text> enter$:
    key(alt-/)
    insert(user.text)
    sleep(500ms)
    key(enter)
