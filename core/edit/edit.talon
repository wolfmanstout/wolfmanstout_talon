mode: command
mode: user.dictation_command
-

# Compound of action(select, clear, copy, cut, paste, etc.) and modifier(word,
# line, etc.) commands for editing text.
# eg: "select line", "clear all"
# For overriding or creating aliases for specific actions, this function will
# also accept strings, e.g. `user.edit_command("delete", "wordLeft")`.
# See edit_command_modifiers.py to discover the correct string for the modify argument,
# and `edit_command_actions.py` `simple_action_callbacks` to find strings for the action argument.
<user.edit_action> <user.edit_modifier>: user.edit_command(edit_action, edit_modifier)

# Zoom
zoom in: edit.zoom_in()
zoom out: edit.zoom_out()
zoom reset: edit.zoom_reset()

# Searching
find [it]: edit.find()
next one: edit.find_next()

# Navigation

# The reason for these spoken forms is that "page up" and "page down" are globally defined as keys.
screen up: edit.page_up()
screen down: edit.page_down()

# go left, go left left down, go 5 left 2 down
# go word left, go 2 words right
go <user.navigation_step>+: user.perform_navigation_steps(navigation_step_list)

go (line start | head): edit.line_start()
go (line end | tail): edit.line_end()

go (way left | west):
    edit.line_start()
    edit.line_start()
go (way right | east): edit.line_end()
go (way up | north): edit.file_start()
go (way down | south): edit.file_end()

go top: edit.file_start()
go bottom: edit.file_end()

go page up: edit.page_up()
go page down: edit.page_down()

# Indentation
indent [more]: edit.indent_more()
indent less | out dent | dedent: edit.indent_less()

# Copy
copy (that | this):
    edit.copy()
    sleep(100ms)

# Cut
cut (that | this): edit.cut()

# Paste
(pace | paste) (that | it): edit.paste()
(pace | paste) enter:
    edit.paste()
    key(enter)
(pace | paste) (match | raw): edit.paste_match_style()
(pace | paste) link: user.link_selection_from_clipboard()
(pace | paste) html: user.paste_html()
(pace | paste) markdown: user.paste_markdown()
(pace | paste) clean: user.paste_clean()

# Duplication
clone (that | this): edit.selection_clone()
clone line: edit.line_clone()

# Insert new line
new line above: edit.line_insert_up()
new line below: edit.line_insert_down()

# Insert padding with optional symbols
padding: user.insert_between(" ", " ")
(pad | padding) <user.symbol_key>+:
    insert(" ")
    user.insert_many(symbol_key_list)
    insert(" ")

# Undo/redo
^undo that$: edit.undo()
^redo that$: edit.redo()

# Save
file save: edit.save()
file save all: edit.save_all()

[go] line mid: user.line_middle()

# Additions
bold this: user.bold()
(italic | italics) this: user.italic()
strike through this: user.strikethrough()
number this: user.number_list()
bullet this: user.bullet_list()
link this: user.hyperlink()
kill: key(ctrl-k)

((hey | OK) google | hey Siri) [<phrase>]$: skip()
