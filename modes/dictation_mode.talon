mode: dictation
experiment: anchor-file
-
settings(): speech.timeout = 0.5

# Everything here should call `auto_insert()` (instead of `insert()`), to preserve the state to correctly auto-capitalize/auto-space.
# (Talonscript string literals implicitly call `auto_insert`, so there's no need to wrap those)
<user.raw_prose>: auto_insert(raw_prose)
cap: user.dictation_format_cap()
# Hyphenated variants are for Dragon.
(no-caps | no caps): user.dictation_format_no_cap()
(no-space | no space): user.dictation_format_no_space()

# Formatting
formatted <user.format_text>:
    user.dictation_insert_raw(format_text)

# Corrections
spell that <user.letters>: auto_insert(letters)
spell that <user.formatters> <user.letters>:
    result = user.formatted_text(letters, formatters)
    user.dictation_insert_raw(result)

(numb | num) <user.number_string>: "{number_string}"
(numb | num) <user.number_string> (dot | point) <digit_string>: "{number_string}.{digit_string}"
(numb | num) <user.number_string> colon <user.number_string>: "{number_string_1}:{number_string_2}"

(halt | now do) [<phrase>]$:
    user.command_mode()
    user.parse_phrase(phrase or "")

(halt | now do) [<phrase>] prose:
    user.command_mode()
    user.parse_phrase(phrase or "")
    user.dictation_mode()

# Ignore accidental usage of "prose" in dictation mode.
^prose: skip()
