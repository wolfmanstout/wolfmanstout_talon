not mode: sleep
-
^dictation mode$: user.dictation_mode()
^command mode$: user.command_mode()
^(private | privacy) mode$: mode.enable("user.private")
^(recording | recorded) mode$: mode.disable("user.private")
