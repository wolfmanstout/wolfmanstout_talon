mode: command
mode: user.dictation_command
app: emacs_org
-
new heading above: key(ctrl-a alt-enter)
new heading: key(ctrl-c c ctrl-e alt-enter)
brand new heading: key(ctrl-c c ctrl-e alt-enter ctrl-c c alt-left)
new heading below: key(ctrl-c c ctrl-e ctrl-enter)
subheading: key(ctrl-c c ctrl-e alt-enter alt-right)
split heading: key(alt-enter)
new to do above: key(ctrl-a alt-shift-enter)
new to do: key(ctrl-c c ctrl-e alt-shift-enter)
brand new to do: key(ctrl-c c ctrl-e alt-shift-enter ctrl-c c alt-left)
new to do below: key(ctrl-c c ctrl-e ctrl-shift-enter)
sub to do: key(ctrl-c c ctrl-e alt-shift-enter alt-right)
split to do: key(alt-shift-enter)
toggle heading: key(ctrl-c *)
to do: key(ctrl-1 ctrl-c ctrl-t)
done: key(ctrl-2 ctrl-c ctrl-t)
clear to do: key(ctrl-3 ctrl-c ctrl-t)
tree indent: key(alt-shift-right)
tree dedent: key(alt-shift-left)
tree move down: key(alt-shift-down)
tree move up: key(alt-shift-up)
tree select: key(alt-h)
tree paste: key(ctrl-c ctrl-x ctrl-y)
tree delete: key(alt-h ctrl-c c ctrl-w)
<number_small> tree [select]: user.mark_lines(number_small, -1, 0, 1)
<number_small> tree (bring | copy) here:
    user.use_lines(number_small, -1, "alt-w", "ctrl-c ctrl-x ctrl-y", 0, 0, 1)
<number_small> tree move here:
    user.use_lines(number_small, -1, "ctrl-w", "ctrl-c ctrl-x ctrl-y", 0, 0, 1)
other <number_small> tree (bring | copy) here:
    user.use_lines(number_small, -1, "alt-w", "ctrl-c ctrl-x ctrl-y", 0, 1, 1)
other <number_small> tree move here:
    user.use_lines(number_small, -1, "ctrl-w", "ctrl-c ctrl-x ctrl-y", 0, 1, 1)
open org link: key(ctrl-c ctrl-o)
show todos: key(ctrl-c / t)
archive: key(ctrl-c ctrl-x ctrl-a)
(org | heading) (west | start): key(ctrl-c c ctrl-a)
clear heading: key(ctrl-c c ctrl-a ctrl-k)
heading (last | preev): key(ctrl-c ctrl-b)
heading next: key(ctrl-c ctrl-f)
heading up: key(ctrl-c ctrl-u)
