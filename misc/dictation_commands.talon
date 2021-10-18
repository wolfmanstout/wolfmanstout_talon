mode: dictation
-
format selection <user.formatters>:
    user.formatters_reformat_selection(formatters)

# Corrections
^scratch that$: user.clear_last_phrase()
^select that$: user.select_last_phrase()

# Escape, type things that would otherwise be commands
escape <user.text>:
    auto_insert(user.text)
