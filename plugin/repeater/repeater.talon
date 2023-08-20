mode: command
mode: user.dictation_command
-
# -1 because we are repeating, so the initial command counts as one
<number_small> times: core.repeat_command(number_small - 1)
(repeat that | twice): core.repeat_command(1)
thrice: core.repeat_command(2)
once: skip()
repeat that <number_small> [times]: core.repeat_command(number_small)
