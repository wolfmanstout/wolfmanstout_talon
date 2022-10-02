mode: command
mode: dictation
-
# -1 because we are repeating, so the initial command counts as one
<number_small> times: core.repeat_command(number_small - 1)
(repeat that | twice): core.repeat_command(1)
thrice: core.repeat_command(2)
repeat that <number_small> [times]: core.repeat_command(number_small)
