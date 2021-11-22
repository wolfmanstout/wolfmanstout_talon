mode: command
mode: dictation
-
copy that: edit.copy()
cut that: edit.cut()
paste that: edit.paste()
^undo [that]$: edit.undo()
^redo [that]$: edit.redo()
paste (match | raw): edit.paste_match_style()
