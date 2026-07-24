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
    def extend_word_left():
        actions.user.emacs("org-shiftcontrolleft")

    def extend_word_right():
        actions.user.emacs("org-shiftcontrolright")

    def indent_more():
        actions.user.emacs("org-metaright")

    def indent_less():
        actions.user.emacs("org-metaleft")

    def word_left():
        actions.user.emacs("backward-symbol")

    def word_right():
        actions.user.emacs("forward-symbol")
