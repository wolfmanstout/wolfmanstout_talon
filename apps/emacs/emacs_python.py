from talon import Context, actions

ctx = Context()
ctx.matches = r"""
app: emacs
title: /- Python -/
"""


@ctx.action_class("edit")
class EditActions:
    def indent_more():
        actions.user.emacs("python-indent-shift-right")

    def indent_less():
        actions.user.emacs("python-indent-shift-left")
