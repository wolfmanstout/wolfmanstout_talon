mode: user.dictation_command
-
format selection <user.formatters>: user.formatters_reformat_selection(formatters)

cap that: user.dictation_reformat_cap()
(no-caps | no caps) that: user.dictation_reformat_no_cap()
(no-space | no space) that: user.dictation_reformat_no_space()

# Corrections
scratch that: user.clear_last_phrase()
select that: user.select_last_phrase()
before that: user.before_last_phrase()

# Escape, type things that would otherwise be commands
type <user.text>: user.dictation_insert(user.text)

just do <phrase>$:
    user.command_mode()
    user.parse_phrase(phrase or "")
    user.dictation_mode()
