prose [<phrase>]$:
    user.dictation_mode()
    user.parse_phrase(phrase or "")

prose [<phrase>] now do:
    user.dictation_mode()
    user.parse_phrase(phrase or "")
    user.command_mode()
