from talon import Context, Module, actions
ctx = Context()
ctx.matches = r"""
title: /Emacs editor/
and title: /- Org -/
"""

@ctx.action_class('edit')
class EditActions:
    def indent_more():
        actions.key('alt-right')
    def indent_less():
        actions.key('alt-left')
