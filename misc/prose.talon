prose [<phrase>]$:
    user.dictation_mode()
    user.parse_phrase(phrase or "")

prose [<phrase>] (halt | now do):
    user.dictation_mode()
    user.parse_phrase(phrase or "")
    user.command_mode()

# Ignore accidental usage of halt in command mode.
^(halt | now do): skip()
