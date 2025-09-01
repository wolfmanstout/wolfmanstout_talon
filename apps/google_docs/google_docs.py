import importlib

from talon import Context, Module, actions

timestamped_captures = importlib.import_module(
    "user.talon-gaze-ocr.timestamped_captures"
)
TextRange = timestamped_captures.TextRange

mod = Module()
mod.apps.google_docs = r"""
tag: browser
title: /<docs.google.com>/
"""
mod.apps.google_docs = r"""
tag: browser
browser.host: docs.google.com
"""

ctx = Context()
ctx.matches = r"""
app: google_docs
"""

win_ctx = Context()
win_ctx.matches = r"""
app: google_docs
os: windows
"""

mac_ctx = Context()
mac_ctx.matches = r"""
app: google_docs
os: mac
"""


@mod.action_class
class Actions:
    def select_column():
        """Select column."""
        actions.key("ctrl-space:2")

    def select_row():
        """Select row."""
        actions.key("shift-space:2")

    def move_row_up():
        """Move row up."""

    def move_row_down():
        """Move row down."""

    def move_column_left():
        """Move column left."""

    def move_column_right():
        """Move column right."""

    def add_comment():
        """Add a comment."""

    def previous_comment():
        """Go to previous comment."""

    def next_comment():
        """Go to next comment."""

    def enter_comment():
        """Enter current comment."""

    def insert_row_above():
        """Insert row above."""

    def insert_row_below():
        """Insert row below."""

    def duplicate_row():
        """Duplicate current row."""
        actions.user.select_row()
        actions.edit.copy()
        actions.sleep("100ms")
        actions.user.insert_row_below()
        actions.sleep("100ms")
        actions.edit.paste()
        actions.sleep("100ms")
        actions.key("up down")

    def delete_row():
        """Delete current row."""

    def rename_document():
        """Rename the document."""

    def duplicate_selection():
        """Duplicate the selected object."""

    def google_docs_title():
        """Set style to title"""
        actions.key("alt-/")
        actions.insert("apply title")
        actions.sleep("500ms")
        actions.key("enter")

    def google_docs_subtitle():
        """Set style to subtitle"""
        actions.key("alt-/")
        actions.insert("apply subtitle")
        actions.sleep("500ms")
        actions.key("enter")

    def google_docs_heading(level: int):
        """Set style to heading"""

    def google_docs_normal_text():
        """Set style to normal text"""

    def google_docs_comment_on_text(ocr_modifier: str, text_range: TextRange):
        """Adds comment to onscreen text."""
        actions.user.select_text_and_do(
            text_range=text_range,
            for_deletion=False,
            ocr_modifier=ocr_modifier,
            action=lambda: actions.user.add_comment(),
        )


@mac_ctx.action_class("self")
class MacActions:
    def move_row_up():
        actions.user.select_row()
        actions.key("ctrl-alt-e m k")

    def move_row_down():
        actions.user.select_row()
        actions.key("ctrl-alt-e m j")

    def move_column_left():
        actions.user.select_column()
        actions.key("ctrl-alt-e m m")

    def move_column_right():
        actions.user.select_column()
        actions.key("ctrl-alt-e m i")

    def add_comment():
        actions.key("cmd-alt-m")

    def previous_comment():
        actions.key("cmd-ctrl-p cmd-ctrl-c")

    def next_comment():
        actions.key("cmd-ctrl-n cmd-ctrl-c")

    def enter_comment():
        actions.key("cmd-ctrl-e cmd-ctrl-c")

    def insert_row_above():
        actions.key("ctrl-alt-i r r")

    def insert_row_below():
        actions.key("ctrl-alt-i r b")

    def delete_row():
        actions.key("ctrl-alt-e d d")

    def rename_document():
        actions.key("ctrl-alt-f r")

    def duplicate_selection():
        actions.key("cmd-d")

    def google_docs_heading(level: int):
        actions.key(f"cmd-alt-{level}")

    def google_docs_normal_text():
        actions.key("cmd-alt-0")


@win_ctx.action_class("self")
class WinActions:
    def move_row_up():
        actions.user.select_row()
        actions.key("alt-e m k")

    def move_row_down():
        actions.user.select_row()
        actions.key("alt-e m j")

    def move_column_left():
        actions.user.select_column()
        actions.key("alt-e m m")

    def move_column_right():
        actions.user.select_column()
        actions.key("alt-e m i")

    def add_comment():
        actions.key("ctrl-alt-m")

    def previous_comment():
        actions.key("ctrl-alt-p ctrl-alt-c")

    def next_comment():
        actions.key("ctrl-alt-n ctrl-alt-c")

    def enter_comment():
        actions.key("ctrl-alt-e ctrl-alt-c")

    def insert_row_above():
        actions.key("alt-i r r")

    def insert_row_below():
        actions.key("alt-i r b")

    def delete_row():
        actions.key("alt-e d d")

    def rename_document():
        actions.key("alt-shift-f r")

    def duplicate_selection():
        actions.key("ctrl-d")

    def google_docs_heading(level: int):
        actions.key(f"ctrl-alt-{level}")

    def google_docs_normal_text():
        actions.key("ctrl-alt-0")
