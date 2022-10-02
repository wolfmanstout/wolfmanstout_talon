mode: command
mode: dictation
app: google_docs
-
select column: user.select_column()
select row: user.select_row()
row up: user.move_row_up()
row down: user.move_row_down()
column left: user.move_column_left()
column right: user.move_column_right()
add comment: user.add_comment()
preev comment: user.previous_comment()
next comment: user.next_comment()
enter comment: user.enter_comment()
(new | insert) row above: user.insert_row_above()
(new | insert) row [below]: user.insert_row_below()
dupe row: user.duplicate_row()
delete row: user.delete_row()
# (click|touch) present: ClickElementAction("//*[@aria-label='Start presentation (Ctrl+F5)']")
file rename: user.rename_document()
