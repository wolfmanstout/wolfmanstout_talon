mode: command
mode: dictation
-
zoom in: edit.zoom_in()
zoom out: edit.zoom_out()
zoom reset: edit.zoom_reset()
screen up: edit.page_up()
screen down: edit.page_down()
copy that: edit.copy()
cut that: edit.cut()
(pace | paste) that: edit.paste()
(pace | paste) enter:
  edit.paste()
  key(enter)
^undo [that]$: edit.undo()
^redo [that]$: edit.redo()
paste (match | raw): edit.paste_match_style()
[file] save: edit.save()
this bold: key(ctrl-b)
this italics: key(ctrl-i)
this strikethrough: key(alt-shift-5)
this numbers: key(ctrl-shift-7)
this bullets: key(ctrl-shift-8)
this link: key(ctrl-k)
kill: key(ctrl-k)

# Repeated from dictation_mode.talon so these can be chained with commands outside that file.
# For some reason, Talon does not prefer this parse if used in dictation_commands.talon.
now do [<phrase>]$:
    user.command_mode()
    user.parse_phrase(phrase or "")

now do [<phrase>] prose:
    user.command_mode()
    user.parse_phrase(phrase or "")
    user.dictation_mode()
