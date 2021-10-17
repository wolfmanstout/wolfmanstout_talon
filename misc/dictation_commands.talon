experiment: anchor-file
mode: dictation
-
press <user.keys>: key("{keys}")

backspace: key(backspace)
delete key: key(delete)

# Escape, type things that would otherwise be commands
escape <user.text>:
    auto_insert(user.text)

# Copied from repeater.talon
# -1 because we are repeating, so the initial command counts as one
<number_small> times: core.repeat_command(number_small-1)
(repeat that|twice): core.repeat_command(1)
thrice: core.repeat_command(2)
repeat that <number_small> [times]: core.repeat_command(number_small)

# Copied from generic_editor.talon
find [it]:
    edit.find()

next one:
    edit.find_next()

go word left | before:
    edit.word_left()

go word right | after:
    edit.word_right()

[go] left:
    edit.left()

[go] right:
    edit.right()

[go] up:
    edit.up()

[go] down:
    edit.down()

[go line] start:
    edit.line_start()

go line end:
    edit.line_end()

go way left | west:
    edit.line_start()
    edit.line_start()

go way right | east:
    edit.line_end()

go way down | south:
    edit.file_end()

go way up | north:
    edit.file_start()
    
go bottom:
    edit.file_end()
    
go top:
    edit.file_start()

go page down:
    edit.page_down()

go page up:
    edit.page_up()

# selecting
select line | line select:
    edit.select_line()

select all | all select:
    edit.select_all()

select left | lefts:
    edit.extend_left()

select right | rights:
    edit.extend_right()

select up:
    edit.extend_line_up()

select down:
    edit.extend_line_down()

select word:
    edit.select_word()

select word left | befores:
    edit.extend_word_left()

select word right | afters:
    edit.extend_word_right()

select way left:
    edit.extend_line_start()

select way right:
    edit.extend_line_end()

select way up:
    edit.extend_file_start()

select way down:
    edit.extend_file_end()

# editing
indent [more]:
    edit.indent_more()

(indent less | out dent):
    edit.indent_less()

# deleting
clear line | line clear:
    edit.delete_line()

clear left | lefts delete:
    key(backspace)

clear right | rights delete:
    key(delete)

clear up:
    edit.extend_line_up()
    edit.delete()

clear down:
    edit.extend_line_down()
    edit.delete()

clear word:
    edit.delete_word()

clear word left | befores delete:
    edit.extend_word_left()
    edit.delete()

clear word right | afters delete:
    edit.extend_word_right()
    edit.delete()

clear way left:
    edit.extend_line_start()
    edit.delete()

clear way right:
    edit.extend_line_end()
    edit.delete()

clear way up:
    edit.extend_file_start()
    edit.delete()

clear way down:
    edit.extend_file_end()
    edit.delete()

clear all:
    edit.select_all()
    edit.delete()

#copy commands
copy all:
    edit.select_all()
    edit.copy()
#to do: do we want these variants, seem to conflict
# copy left:
#      edit.extend_left()
#      edit.copy()
# copy right:
#     edit.extend_right()
#     edit.copy()
# copy up:
#     edit.extend_up()
#     edit.copy()
# copy down:
#     edit.extend_down()
#     edit.copy()

copy word:
    edit.select_word()
    edit.copy()

copy word left:
    edit.extend_word_left()
    edit.copy()

copy word right:
    edit.extend_word_right()
    edit.copy()

copy line:
    edit.select_line()
    edit.copy()

#cut commands
cut all:
    edit.select_all()
    edit.cut()
#to do: do we want these variants
# cut left:
#      edit.select_all()
#      edit.cut()
# cut right:
#      edit.select_all()
#      edit.cut()
# cut up:
#      edit.select_all()
#     edit.cut()
# cut down:
#     edit.select_all()
#     edit.cut()

cut word:
    edit.select_word()
    edit.cut()

cut word left:
    edit.extend_word_left()
    edit.cut()

cut word right:
    edit.extend_word_right()
    edit.cut()

cut line:
    edit.select_line()
    edit.cut()
