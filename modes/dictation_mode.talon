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
formatted <user.format_text> [over]:
    user.dictation_insert_raw(format_text)

# Corrections
spell that <user.letters> [over]: auto_insert(letters)
spell that <user.formatters> <user.letters> [over]:
    result = user.formatted_text(letters, formatters)
    user.dictation_insert_raw(result)

now do [<phrase>]$:
    user.command_mode()
    user.parse_phrase(phrase or "")

now do [<phrase>] prose:
    user.command_mode()
    user.parse_phrase(phrase or "")
    user.dictation_mode()

# Ignore accidental usage of "prose" in dictation mode.
^prose: skip()
