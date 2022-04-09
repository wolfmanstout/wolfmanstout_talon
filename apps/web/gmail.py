from talon import Context, actions

ctx = Context()
ctx.matches = r"""
tag: browser
title: /Gmail/
title: /Google.com Mail/
title: /<mail.google.com>/
title: /<inbox.google.com>/
title: /messaged you - Chat/
"""

@ctx.action_class('edit')
class EditActions:
    def indent_more():
        actions.key('ctrl-]')
    def indent_less():
        actions.key('ctrl-[')
