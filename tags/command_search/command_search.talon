mode: command
and not mode: dictation
tag: user.command_search
-

^please [<user.prose>]$: user.command_search(user.prose or "")
^please <user.prose> (enter | slap)$:
    user.command_search(user.prose)
    sleep(500ms)
    key(enter)
