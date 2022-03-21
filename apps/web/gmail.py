from talon import Context, actions

ctx = Context()
ctx.matches = r"""
tag: browser
title: /Gmail/
title: /Google.com Mail/
title: /<mail.google.com>/
title: /<inbox.google.com>/
"""

@ctx.action_class('edit')
class EditActions:
    def indent_more():
        actions.key('ctrl-]')
    def indent_less():
        actions.key('ctrl-]')

@ctx.action_class("user")
class Actions:
    def dictation_insert(text: str, auto_cap: bool=True) -> str:
        # "Peek right" after insertion to avoid breaking autosuggest.
        actions.user.dictation_insert_with_options(text, auto_cap, peek_right_after=True)
