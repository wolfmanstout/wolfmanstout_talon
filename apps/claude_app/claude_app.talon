app: claude_app
-

tag(): user.command_search
tag(): user.splits
tag(): terminal

# General
settings open: key(cmd-,)
folder open | file open folder: key(cmd-shift-o)
file open: key(cmd-o)
shortcuts open: key(cmd-/)
go back: key(cmd-[)
go forward: key(cmd-])
bar (open | close | switch): key(cmd-b)
bar tab next: key(alt-cmd-right)
bar tab last: key(alt-cmd-left)
find: key(cmd-f)
tab (close | clothes): key(cmd-w)
transcript view switch: key(ctrl-o)

# Panes
(diff | review) open: key(cmd-shift-d)
file list (open | close | switch): key(cmd-shift-y)
file hunt: key(cmd-p)
files open: key(cmd-shift-f)
selection attach: key(cmd-shift-l)
browser open: key(cmd-shift-b)
browser select: key(cmd-shift-s)
browser annotate: key(cmd-shift-x)
browser tab new: key(cmd-t)
browser tab reopen: key(cmd-shift-t)
browser address: key(cmd-l)
browser reload: key(cmd-r)
(terminal | shell) open | panel (open | close | switch | terminal | shell): key(cmd-j)
panel close: key(cmd-\)
panel (expand | collapse): key(cmd-shift-\)
side chat open: key(cmd-;)

# Composer
(mode | permission) menu: key(cmd-shift-m)
model menu: key(cmd-shift-i)
effort menu: key(cmd-shift-e)
fast mode switch: key(alt-cmd-f)
file attach: key(cmd-u)

# Thread
thread new: key(cmd-n)
thread new same: key(cmd-shift-n)
thread hunt: key(cmd-shift-k)
thread recent: key(ctrl-q)
thread close: key(cmd-w)
thread reopen: key(cmd-shift-t)
thread last: key(cmd-shift-[)
thread next: key(cmd-shift-])
thread <number_small>: key("cmd-{number_small}")
thread pin: key(alt-cmd-p)
thread rename: key(alt-cmd-r)
thread archive: key(alt-cmd-a)
thread (read | unread): key(alt-cmd-u)
thread copy link: key(alt-cmd-l)
thread pull request: key(alt-cmd-g)
thread fork: key(alt-cmd-o)
