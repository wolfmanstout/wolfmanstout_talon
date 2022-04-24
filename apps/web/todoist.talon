tag: browser
title: /<todoist.com>/
-
go inbox: key(g i)
go today: key(g t)
go upcoming: key(g u)
go search: key(/)
go task project: key(G)
go inside: 
    key(g p)
    insert("inside")
    key(down enter)
go outside: 
    key(g p)
    insert("outside")
    key(down enter)
go computer: 
    key(g p)
    insert("computer")
    key(down enter)
go mom: 
    key(g p)
    insert("mom")
    key(down enter)
project open | go project: key(g p)
task select: key(x)
task done: key(e)
task edit: key(E)
please [<user.text>]$:
    key(ctrl-k)
    insert(user.text or "")
task new: key(q)
task add [bottom] | add task [bottom]: key(a)
task add top | add task top: key(A)
