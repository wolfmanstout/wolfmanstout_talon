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
zoom in: edit.zoom_in()
zoom out: edit.zoom_out()
screen up: edit.page_up()
screen down: edit.page_down()
[file] save: edit.save()
slap: edit.line_insert_down()

prose [<phrase>]$:
    # Copied from modes.talon.
    mode.disable("sleep")
    mode.disable("command")
    mode.enable("dictation")
    user.code_clear_language_mode()
    mode.disable("user.gdb")
    user.dictation_format_reset()
    user.parse_phrase(phrase or "")
