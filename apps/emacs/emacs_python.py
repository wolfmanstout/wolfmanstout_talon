from talon import Context, Module, actions
ctx = Context()
ctx.matches = r"""
app: emacs
title: /- Python -/
"""

@ctx.action_class('edit')
class EditActions:
    def indent_more():
        actions.key('ctrl-c >')
    def indent_less():
        actions.key('ctrl-c <')
