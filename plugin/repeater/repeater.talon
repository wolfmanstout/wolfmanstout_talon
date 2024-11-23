mode: command
mode: user.dictation_command
-
# -1 because we are repeating, so the initial command counts as one
<number_small> times: core.repeat_command(number_small - 1)
once: skip()
twice: core.repeat_command(1)
thrice: core.repeat_command(2)
^repeat (that | phrase) [<number_small> times]$:
    core.repeat_partial_phrase(number_small or 1)
