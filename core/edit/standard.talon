mode: command
mode: user.dictation_command
-
zoom in: edit.zoom_in()
zoom out: edit.zoom_out()
zoom reset: edit.zoom_reset()
screen up: edit.page_up()
screen down: edit.page_down()
copy that: 
    edit.copy()
    sleep(100ms)
cut that: edit.cut()
(pace | paste) that: edit.paste()
(pace | paste) enter:
    edit.paste()
    key(enter)
^undo [that]$: edit.undo()
^redo [that]$: edit.redo()
(pace | paste) (match | raw): edit.paste_match_style()
(pace | paste) link: 
    user.hyperlink()
    sleep(100ms)
    edit.paste()
[file] save: edit.save()
bold this: user.bold()
italics this: user.italic()
strike through this: user.strikethrough()
number this: user.number_list()
bullet this: user.bullet_list()
link this: user.hyperlink()
kill: key(ctrl-k)

((hey | OK) google | hey Siri) [<phrase>]$: skip()
