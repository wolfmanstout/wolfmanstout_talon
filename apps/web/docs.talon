mode: command
mode: dictation
tag: browser
title: /<docs.google.com>/
-
settings():
    user.clipboard_delay = "10ms"

select column: key(ctrl-space:2)
select row: key(shift-space:2)
row up: key(alt-e k)
row down: key(alt-e j)
column left: key(alt-e m)
column right: key(alt-e m)
add comment: key(ctrl-alt-m)
preev comment: key(ctrl-alt-p ctrl-alt-c)
next comment: key(ctrl-alt-n ctrl-alt-c)
enter comment: key(ctrl-alt-e ctrl-alt-c)
(new|insert) row above: key(alt-i r)
(new|insert) row [below]: key(alt-i b)
dupe row: key(shift-space:2 ctrl-c alt-i b ctrl-v up down)
delete row: key(alt-e d)
# (click|touch) present: ClickElementAction("//*[@aria-label='Start presentation (Ctrl+F5)']")
file rename: key(alt-shift-f r)
please [<user.text>]$:
    key(alt-/)
    insert(user.text or "")
    sleep(100ms)
    key(enter)
