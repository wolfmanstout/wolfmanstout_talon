mode: dictation
experiment: anchor-file
-
settings(): speech.timeout = 0.5

# Everything here should call auto_insert to preserve the state to correctly auto-capitalize/auto-space.
<user.raw_prose>: auto_insert(raw_prose)
new line: "\n"
new paragraph: "\n\n"
spacebar: " "
cap <user.word>:
    result = user.formatted_text(word, "CAPITALIZE_FIRST_WORD")
    auto_insert(result)
no caps <user.word>: user.dictation_insert_raw(word)

# Formatting
formatted <user.format_text>:
    auto_insert(format_text)

# Corrections
spell that <user.letters>: auto_insert(letters)
spell that <user.formatters> <user.letters>:
    result = user.formatted_text(letters, formatters)
    user.dictation_insert_raw(result)

numb <user.number_string>: "{number_string}"
numb <user.number_string> (dot | point) <digit_string>: "{number_string}.{digit_string}"

halt [<phrase>]$:
    mode.disable("sleep")
    mode.enable("command")
    mode.disable("dictation")
    user.parse_phrase(phrase or "")
