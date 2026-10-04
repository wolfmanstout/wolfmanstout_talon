mode: dictation
-

settings():
    speech.timeout = 0.5

# Everything here should call `user.dictation_insert()` instead of `insert()`, to correctly auto-capitalize/auto-space.
<user.raw_prose>: user.dictation_insert(raw_prose)
cap: user.dictation_format_cap()
# Hyphenated variants are for Dragon.
no-caps | no caps: user.dictation_format_no_cap()
no-space | no space: user.dictation_format_no_space()

# Formatting
formatted {user.rich_text_format}+ <user.format_text> [over]:
    user.dictation_insert_rich_text(format_text, rich_text_format_list)
formatted {user.rich_text_format}+ <user.raw_prose> [over]:
    user.dictation_insert_rich_text(raw_prose, rich_text_format_list)
formatted <user.format_text> [over]: user.dictation_insert_raw(format_text)

# Corrections
spell that <user.letters> [over]: user.dictation_insert(letters)
spell that <user.formatters> <user.letters> [over]:
    result = user.formatted_text(letters, formatters)
    user.dictation_insert_raw(result)

# Ignore accidental usage of "prose" in dictation mode.
^prose: skip()
