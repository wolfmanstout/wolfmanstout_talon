tag: browser
title: /Gmail/
title: /Google.com Mail/
title: /<mail.google.com>/
title: /<inbox.google.com>/
-
settings():
    user.peek_right_after_insertion = 1

tag(): user.emoji
open: key(+ o)
archive: key(+ {)
done: key(+ [)
this unread: key(+ _)
gmail undo: key(+ z)
list: key(+ u)
compose: key(+ c)
reply: key(+ r)
reply all: key(+ a)
forward: key(+ f)
important: key(+ +)
this star: key(+ s)
this important: key(+ +)
this not important: key(+ -)
label waiting:
    key(+ l)
    sleep(500ms)
    insert("waiting")
    sleep(500ms)
    key(enter)
label snooze:
    key(+ l)
    sleep(500ms)
    insert("snooze")
    sleep(500ms)
    key(enter)
snooze:
    key(+ l)
    sleep(500ms)
    insert("snooze")
    sleep(500ms)
    key(enter)
    sleep(500ms)
    key(+ [)
label vacation:
    key(+ l)
    sleep(500ms)
    insert("vacation")
    sleep(500ms)
    key(enter)
label house:
    key(+ l)
    sleep(500ms)
    insert("house")
    sleep(500ms)
    key(enter)
label taxes:
    key(+ l)
    sleep(500ms)
    insert("taxes")
    sleep(500ms)
    key(enter)
label: key(+ l)
this select: key(+ x)
# <n> select: {['plus, x, plus, j']}n
(message|messages) reload: key(+ N)
go inbox|going box: key(+ g i)
go starred: key(+ g s)
go sent: key(+ g t)
go drafts: key(+ g d)
# expand all: ClickElementAction("//*[@aria-label='Expand all']")
# collapse all: ClickElementAction("//*[@aria-label='Collapse all']")
# go field to: ClickElementAction("//*[@aria-label='To']")
go field cc: key(ctrl-shift-c)
chat open: key(+ q)
this send: key(ctrl-enter)
go search: key(+ /)
preev: key(+ k)
next: key(+ j)
message preev: key(+ p)
message next: key(+ n)
section next: key(+ `)
section preev: key(+ ~)
