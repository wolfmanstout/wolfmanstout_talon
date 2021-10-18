not mode: sleep
-
^dictation mode$:
    mode.disable("sleep")
    mode.disable("command")
    mode.enable("dictation")
    user.code_clear_language_mode()
    mode.disable("user.gdb")
    user.dictation_format_reset()
^command mode$:
    mode.disable("sleep")
    mode.disable("dictation")
    mode.enable("command")
