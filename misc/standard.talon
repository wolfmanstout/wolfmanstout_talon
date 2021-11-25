mode: command
mode: dictation
-
zoom in: edit.zoom_in()
zoom out: edit.zoom_out()
screen up: edit.page_up()
screen down: edit.page_down()
copy that: edit.copy()
cut that: edit.cut()
paste that: edit.paste()
^undo [that]$: edit.undo()
^redo [that]$: edit.redo()
paste (match | raw): edit.paste_match_style()
[file] save: edit.save()
wipe: key(backspace)
slap: edit.line_insert_down()