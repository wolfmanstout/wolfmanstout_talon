mode: user.dictation_command
-
format selection <user.formatters>: user.formatters_reformat_selection(formatters)

cap that: user.dictation_reformat_cap()
(no-caps | no caps) that: user.dictation_reformat_no_cap()
(no-space | no space) that: user.dictation_reformat_no_space()

# Corrections
scratch that: user.clear_last_phrase()
select that: user.select_last_phrase()

# Escape, type things that would otherwise be commands
type <user.text>: user.dictation_insert(user.text)
