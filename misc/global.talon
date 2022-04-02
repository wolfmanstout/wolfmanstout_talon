# my <text> (click|touch): '"<text> (click|touch)": Function(lambda text: accessibility.click(text)),'()
# my go before <text_position_query>: '"go before <text_position_query>": Function(lambda text_position_query: accessibility.move_cursor(\n        text_position_query, CursorPosition.BEFORE)),'()
# my go after <text_position_query>: '"go after <text_position_query>": Function(lambda text_position_query: accessibility.move_cursor(\n        text_position_query, CursorPosition.AFTER)),'()
# my words <text_query> delete: '"words <text_query> delete": Function(lambda text_query: accessibility.replace_text(text_query, "")),'()
# my words <text_query>: 'select_text'()
# my replace <text_query> with <replacement>: 'replace_text'()
not equals: insert("!=")
padded not equals: insert(" != ")
greater equals: insert(">=")
padded greater equals: insert(" >= ")
less equals: insert("<=")
padded less equals: insert(" <= ")
(window | win) (restore | minimize | min): key(win:down down down win:up)
(window | win) (maximize | max): key(win:down up up win:up)
windows search: key(win-s)
windows run: key(win-r)
windows desktop: key(win-d)
windows explorer: key(win-e)
# webdriver open: 'create_driver'()
# webdriver close: 'quit_driver'()
((hey | OK) google | hey Siri) [<phrase>]$: skip()
cancel: key(escape)
