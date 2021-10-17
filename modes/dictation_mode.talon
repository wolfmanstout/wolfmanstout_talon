mode: dictation
-
settings(): speech.timeout = 0.5

^press <user.keys>$: key("{keys}")

# Everything here should call auto_insert to preserve the state to correctly auto-capitalize/auto-space.
<user.raw_prose>: auto_insert(raw_prose)
new line: "\n"
new paragraph: "\n\n"
cap <user.word>:
    result = user.formatted_text(word, "CAPITALIZE_FIRST_WORD")
    auto_insert(result)
no caps <user.word>: user.dictation_insert_raw(word)
    

# Formatting
formatted <user.format_text>:
    auto_insert(format_text)
^format selection <user.formatters>$:
    user.formatters_reformat_selection(formatters)

# Corrections
^scratch that$: user.clear_last_phrase()
^select that$: user.select_last_phrase()
spell that <user.letters>: auto_insert(letters)
spell that <user.formatters> <user.letters>:
    result = user.formatted_text(letters, formatters)
    user.dictation_insert_raw(result)
^undo [that]$: edit.undo()
^redo [that]$: edit.redo()
^backspace$: key(backspace)
^delete key$: key(delete)

# Escape, type things that would otherwise be commands
^escape <user.text>$:
    auto_insert(user.text)

numb <user.number_string>: "{number_string}"
numb <user.number_string> (dot | point) <digit_string>: "{number_string}.{digit_string}"

halt [<phrase>]$:
    mode.disable("sleep")
    mode.disable("dictation")
    mode.enable("command")
    user.parse_phrase(phrase or "")
