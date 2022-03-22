mode: command
mode: dictation
title: /Emacs editor/
-
# General
cancel: key(ctrl-g)

# Movement
start: key(alt-m)
line <number_small> [short]:
    key(ctrl-u)
    insert("{number_small}")
    key(ctrl-c c g)
here scroll: key(ctrl-l)
mark set: key(ctrl-space)
mark save: key(ctrl-\)
go mark: key(ctrl-<)
go change: key(ctrl-c c c)
go symbol: key(alt-i)
go mark switch: key(ctrl-c ctrl-x)
go before [preev] <user.any_alphanumeric_key>: key("ctrl-c c b {any_alphanumeric_key}")
go after [next] <user.any_alphanumeric_key>: key("ctrl-c c f {any_alphanumeric_key}")
go before next <user.any_alphanumeric_key>: key("ctrl-c c s {any_alphanumeric_key}")
go after preev <user.any_alphanumeric_key>: key("ctrl-c c e {any_alphanumeric_key}")
other screen up: key(ctrl-- ctrl-alt-v)
other screen down: key(ctrl-alt-v)
# go eye <char>: ['c-c, c, j']+'%(char)s'+'"go eye <char>": Key("c-c, c, j") + Text(u"%(char)s") + Function(lambda: tracker.type_gaze_point("%d\\n%d\\n")),'()

# Editing
delete: key(ctrl-c c ctrl-w)
this select: key(ctrl-x ctrl-x)
<number_small> (through | until) [<number_small>] [select]: user.mark_lines(number_small_1, number_small_2 or -1)
<number_small> (through | until) [<number_small>] short [select]: user.mark_lines(number_small_1, number_small_2 or -1, 1)
<number_small> (through | until) [<number_small>] copy here: user.use_lines(number_small_1, number_small_2 or -1, "alt-w", "ctrl-y")
<number_small> (through | until) [<number_small>] short copy here: user.use_lines(number_small_1, number_small_2 or -1, "alt-w", "ctrl-y", 1)
<number_small> (through | until) [<number_small>] move here: user.use_lines(number_small_1, number_small_2 or -1, "ctrl-w", "ctrl-y")
<number_small> (through | until) [<number_small>] short move here: user.use_lines(number_small_1, number_small_2 or -1, "ctrl-w", "ctrl-y", 1)
other <number_small> (through | until) [<number_small>] copy here: user.use_lines(number_small_1, number_small_2 or -1, "alt-w", "ctrl-y", 0, 1)
other <number_small> (through | until) [<number_small>] short copy here: user.use_lines(number_small_1, number_small_2 or -1, "alt-w", "ctrl-y", 1, 1)
other <number_small> (through | until) [<number_small>] move here: user.use_lines(number_small_1, number_small_2 or -1, "ctrl-w", "ctrl-y", 0, 1)
other <number_small> (through | until) [<number_small>] short move here: user.use_lines(number_small_1, number_small_2 or -1, "ctrl-w", "ctrl-y", 1, 1)
