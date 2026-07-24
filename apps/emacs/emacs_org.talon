mode: command
mode: user.dictation_command
app: emacs_org
-

new heading above:
    user.emacs("move-beginning-of-line")
    user.emacs("org-meta-return")
new heading:
    user.emacs("move-end-of-line")
    user.emacs("org-meta-return")
brand new heading:
    user.emacs("move-end-of-line")
    user.emacs("org-meta-return")
    user.emacs("my-org-dedent-to-top-level")
new heading below:
    user.emacs("move-end-of-line")
    user.emacs("org-insert-heading-respect-content")
subheading:
    user.emacs("move-end-of-line")
    user.emacs("org-meta-return")
    user.emacs("org-metaright")
split heading: user.emacs("org-meta-return")
new to do above:
    user.emacs("move-beginning-of-line")
    user.emacs("org-insert-todo-heading")
new to do:
    user.emacs("move-end-of-line")
    user.emacs("org-insert-todo-heading")
brand new to do:
    user.emacs("move-end-of-line")
    user.emacs("org-insert-todo-heading")
    user.emacs("my-org-dedent-to-top-level")
new to do below:
    user.emacs("move-end-of-line")
    user.emacs("org-insert-todo-heading-respect-content")
sub to do:
    user.emacs("move-end-of-line")
    user.emacs("org-insert-todo-heading")
    user.emacs("org-metaright")
split to do: user.emacs("org-insert-todo-heading")
toggle heading: user.emacs("org-ctrl-c-star")
to do: user.emacs("org-todo", 1)
done: user.emacs("org-todo", 2)
clear to do: user.emacs("org-todo", 3)
tree indent: user.emacs("org-shiftmetaright")
tree dedent: user.emacs("org-shiftmetaleft")
tree move down: user.emacs("org-shiftmetadown")
tree move up: user.emacs("org-shiftmetaup")
tree select: user.emacs("org-mark-element")
tree paste: user.emacs("org-paste-special")
tree delete:
    user.emacs("org-mark-element")
    user.emacs("delete-region")
<number_small> tree [select]: user.mark_lines(number_small, -1, false, true)
<number_small> tree (bring | copy) here:
    user.use_lines(number_small, -1, true, false, false, true)
<number_small> tree move here:
    user.use_lines(number_small, -1, false, false, false, true)
other <number_small> tree (bring | copy) here:
    user.use_lines(number_small, -1, true, false, true, true)
other <number_small> tree move here:
    user.use_lines(number_small, -1, false, false, true, true)
open org link: user.emacs("org-open-at-point")
todos open: user.emacs("org-show-todo-tree")
archive: user.emacs("org-archive-subtree-default")
(org | heading) (west | start): user.emacs("my-org-beginning-of-line")
clear heading:
    user.emacs("my-org-beginning-of-line")
    user.emacs("safe-kill-line")
heading (last | preev): user.emacs("org-backward-heading-same-level")
heading next: user.emacs("org-forward-heading-same-level")
heading up: user.emacs("outline-up-heading")
