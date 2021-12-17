from talon import Context, actions, clip
from typing import Optional

ctx = Context()
ctx.matches = r"""
tag: browser
title: /<docs.google.com>/
"""

@ctx.action_class('edit')
class EditActions:
    def selected_text() -> str:
        # Reimplemented to add sleep.
        with clip.capture() as s:
            actions.sleep("10ms")
            actions.edit.copy()
            actions.sleep("10ms")
        try:
            return s.get()
        except clip.NoChange:
            return ""
    
    def extend_word_right():
        # Without this hack, docs may select a single whitespace character 
        # instead of the next word.
        actions.key('ctrl-left ctrl-right ctrl-shift-right')
