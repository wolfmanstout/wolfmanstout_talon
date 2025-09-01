from talon import Context, Module, actions

mod = Module()
mod.apps.gmail = r"""
tag: browser
title: /Gmail/
title: /Google.com Mail/
title: /<mail.google.com>/
title: /<inbox.google.com>/
title: / - Chat/
"""
mod.apps.gmail = r"""
tag: browser
browser.host: mail.google.com
"""

ctx = Context()
ctx.matches = r"""
app: gmail
"""


@ctx.action_class("edit")
class EditActions:
    def indent_more():
        actions.key("ctrl-]")

    def indent_less():
        actions.key("ctrl-[")
