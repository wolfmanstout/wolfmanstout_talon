mode: command
mode: dictation
tag: user.tabs
-
tab (open | new): app.tab_open()
tab (last | previous | left): app.tab_previous()
tab (next | right): app.tab_next()
tab close: user.tab_close_wrapper()
tab (reopen|restore): app.tab_reopen()
go tab <number_small>: user.tab_jump(number_small)
go tab (final | last): user.tab_final()
tab duplicate: user.tab_duplicate()
