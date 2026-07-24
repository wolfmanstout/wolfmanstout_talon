mode: command
mode: user.dictation_command
app: emacs
-

# Movement
start: user.emacs("back-to-indentation")
line <number_small> [short]: user.jump_modulo_line(number_small)
here scroll: user.emacs("recenter-top-bottom")
mark set: user.emacs("set-mark-command")
mark save: user.emacs("push-mark-no-activate")
go mark: user.emacs("jump-to-mark")
go change: user.emacs("goto-last-change")
go symbol: user.emacs("ido-goto-symbol")
go mark switch: user.emacs("exchange-point-and-mark-no-activate")
go before [last | preev] <user.any_alphanumeric_key>:
    user.emacs("backward-before-char")
    key("{any_alphanumeric_key}")
go after [next] <user.any_alphanumeric_key>:
    user.emacs("forward-after-char")
    key("{any_alphanumeric_key}")
go before next <user.any_alphanumeric_key>:
    user.emacs("forward-before-char")
    key("{any_alphanumeric_key}")
go after (last | preev) <user.any_alphanumeric_key>:
    user.emacs("backward-after-char")
    key("{any_alphanumeric_key}")
other screen up: user.emacs("scroll-other-window-down")
other screen down: user.emacs("scroll-other-window")

# Window manipulation
buff open: user.emacs("switch-to-buffer")
buff open split:
    user.emacs("split-window-right")
    user.emacs("other-window")
    user.emacs("switch-to-buffer")
buff switch:
    user.emacs("switch-to-buffer")
    key(enter)
buff close: user.emacs("delete-window")
buff done: user.emacs("server-edit")
buff kill:
    user.emacs("kill-buffer")
    key(enter)
buff up: user.emacs("windmove-up")
buff down: user.emacs("windmove-down")
buff left: user.emacs("windmove-left")
buff right: user.emacs("windmove-right")
buff revert: user.emacs("revert-buffer")

# Editing
delete: user.emacs("delete-region")
this select: user.emacs("exchange-point-and-mark")
<number_small> (through | until) [<number_small>] [select]:
    user.mark_lines(number_small_1, number_small_2 or -1)
<number_small> (through | until) [<number_small>] short [select]:
    user.mark_lines(number_small_1, number_small_2 or -1, true)
<number_small> (through | until) [<number_small>] (bring | copy) here:
    user.use_lines(number_small_1, number_small_2 or -1, true)
<number_small> (through | until) [<number_small>] short (bring | copy) here:
    user.use_lines(number_small_1, number_small_2 or -1, true, true)
<number_small> (through | until) [<number_small>] move here:
    user.use_lines(number_small_1, number_small_2 or -1)
<number_small> (through | until) [<number_small>] short move here:
    user.use_lines(number_small_1, number_small_2 or -1, false, true)
other <number_small> (through | until) [<number_small>] (bring | copy) here:
    user.use_lines(number_small_1, number_small_2 or -1, true, false, true)
other <number_small> (through | until) [<number_small>] short (bring | copy) here:
    user.use_lines(number_small_1, number_small_2 or -1, true, true, true)
other <number_small> (through | until) [<number_small>] move here:
    user.use_lines(number_small_1, number_small_2 or -1, false, false, true)
other <number_small> (through | until) [<number_small>] short move here:
    user.use_lines(number_small_1, number_small_2 or -1, false, true, true)
