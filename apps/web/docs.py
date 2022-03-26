from talon import Context, actions, clip
from typing import Optional

ctx = Context()
ctx.matches = r"""
tag: browser
title: /<docs.google.com>/
"""

@ctx.action_class('edit')
class EditActions:
    def extend_word_right():
        # Without this hack, docs may select a single whitespace character 
        # instead of the next word.
        actions.key('ctrl-left ctrl-right ctrl-shift-right')
