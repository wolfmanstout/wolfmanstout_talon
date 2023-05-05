mode: command
mode: user.dictation_command
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
bold this: user.bold()
italics this: user.italic()
strikethrough this: user.strikethrough()
number this: user.number_list()
bullet this: user.bullet_list()
link this: user.hyperlink()
kill: key(ctrl-k)

# Repeated from dictation_mode.talon so these can be chained with commands outside that file.
# For some reason, Talon does not prefer this parse if used in user.dictation_commands.talon.
now do [<phrase>]$:
    user.command_mode()
    user.parse_phrase(phrase or "")

now do [<phrase>] prose:
    user.command_mode()
    user.parse_phrase(phrase or "")
    user.dictation_mode()

((hey | OK) google | hey Siri) [<phrase>]$: skip()
