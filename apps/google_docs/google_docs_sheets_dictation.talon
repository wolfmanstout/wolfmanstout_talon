mode: command
mode: user.dictation_command
app: google_docs
browser.path: /^\/spreadsheets/
-
settings():
    # TODO: Adjust this to the minimal value that works in Google Sheets on Windows.
    # key_wait = 10

select column: user.select_column()
select row: user.select_row()
row up: user.move_row_up()
row down: user.move_row_down()
column left: user.move_column_left()
column right: user.move_column_right()
(new | insert) row above: user.insert_row_above()
(new | insert) row [below]: user.insert_row_below()
dupe row: user.duplicate_row()
delete row: user.delete_row()
