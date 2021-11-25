#(jay son | jason ): "json"
#(http | htp): "http"
#tls: "tls"
#M D five: "md5"
#word (regex | rejex): "regex"
#word queue: "queue"
#word eye: "eye"
#word iter: "iter"
#word no: "NULL"
#word cmd: "cmd"
#word dup: "dup"
#word shell: "shell".

prose [<phrase>]$:
    user.dictation_mode()
    user.parse_phrase(phrase or "")

prose [<phrase>] halt:
    user.dictation_mode()
    user.parse_phrase(phrase or "")
    user.command_mode()

# Ignore accidental usage of halt in command mode.
^halt: skip()
