from talon import Context, Module, actions

mod = Module()
mod.apps.emacs_org = r"""
app: emacs
title: /- Org -/
"""

ctx = Context()
ctx.matches = r"""
app: emacs_org
"""


@ctx.action_class("edit")
class EditActions:
    def indent_more():
        actions.key("alt-right")

    def indent_less():
        actions.key("alt-left")
