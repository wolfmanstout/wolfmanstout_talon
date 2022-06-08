from talon import Context, Module, actions

mod = Module()
mod.apps.google_docs = r"""
tag: browser
title: /<docs.google.com>/
"""

ctx = Context()
ctx.matches = r"""
app: google_docs
"""


@ctx.action_class("edit")
class EditActions:
    def extend_word_right():
        # Without this hack, docs may select a single whitespace character
        # instead of the next word.
        actions.key("ctrl-left ctrl-right ctrl-shift-right")
