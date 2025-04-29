mode: dictation
mode: command
mode: user.dictation_command
-
now do [<phrase>]$:
    user.command_mode()
    user.parse_phrase(phrase or "")

now do [<phrase>] prose:
    user.command_mode()
    user.parse_phrase(phrase or "")
    user.dictation_mode()

(pace | paste) auto: user.dictation_insert(clip.text())
(pace | paste) auto (quoted | string): 
    user.dictation_insert('“')
    user.dictation_insert(clip.text())
    user.dictation_insert('”')
