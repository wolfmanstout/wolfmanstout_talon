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
