from talon import Context, Module, actions, clip
from typing import Optional

ctx = Context()
ctx.matches = r"""
title: /Emacs editor/
"""

ctx.tags = ['user.find_and_replace', 'user.line_commands', 'user.splits', 'user.snippets']

ctx.lists["user.snippets"] = {
    "beginend": "beginend",
    "car": "car",
    "catch": "catch",
    "doc": "doc",
    "field declaration": "field_declaration",
    "field definition": "field_definition",
    "field initialize": "field_initialize",
    "finally": "finally",
    "class": "class",
    "const ref": "const_ref",
    "const pointer": "const_pointer",
    "def": "function",
    "each": "each",
    "else": "else",
    "entry": "entry",
    "error": "error",
    "eval": "eval",
    "fatal": "fatal",
    "for": "for",
    "fun declaration": "fun_declaration",
    "function": "function",
    "if": "if",
    "info": "info",
    "inverse if": "inverse_if",
    "key": "key",
    "lambda": "lambda",
    "list": "list",
    "map": "map",
    "method": "method",
    "namespace": "namespace",
    "new": "new",
    "override": "override",
    "ref": "ref",
    "set": "set",
    "shared pointer": "shared_pointer",
    "test": "test",
    "ternary": "ternary",
    "text": "text",
    "to do": "todo",
    "try": "try",
    "unique pointer": "unique_pointer",
    "var": "vardef",
    "vector": "vector",
    "warning": "warning",
    "while": "while",
}

@ctx.action_class('edit')
class EditActions:
    def copy():
        actions.key('alt-w')
    def cut():
        actions.key('ctrl-w')
    def selected_text() -> str:
        # Reimplemented to add sleep.
        with clip.capture() as s:
            actions.sleep("100ms")
            actions.edit.copy()
            actions.sleep("100ms")
        try:
            return s.get()
        except clip.NoChange:
            return ""
    def find(text: str=None):
        actions.key('ctrl-s')
        actions.actions.insert(text)
    def find_next():
        actions.key('ctrl-s')
    def indent_more():
        actions.key('ctrl-x tab shift-right')
    def indent_less():
        actions.key('ctrl-x tab shift-left')
    def line_swap_up():
        actions.key("alt-up")
    def line_swap_down():
        actions.key("alt-down")
    def line_clone():
        actions.key("shift-alt-down")
    def paste():
        actions.key('ctrl-y')
    def paste_match_style():
        actions.key('ctrl-y')
    def redo():
        actions.key('ctrl-shift-/')
    def save():
        actions.key('ctrl-x ctrl-s')
    def save_all():
        actions.key('ctrl-x ctrl-shift-s')
    def select_all():
        actions.key('ctrl-x h')
    def select_none():
        actions.key('ctrl-g')
    def undo():
        actions.key('ctrl-/')

    def jump_line(n: int):
        actions.key("alt-g alt-g")
        actions.insert(str(n))
        actions.key("enter")
        # actions.key("ctrl-u")
        # actions.insert(str(n))
        # actions.key("ctrl-c c g")

@ctx.action_class("code")
class CodeActions:
    def toggle_comment():
        actions.key("alt-;")

@ctx.action_class("win")
class WinActions:
    def filename():
        title = actions.win.title()
        result = title.split(" - ")[0]
        if "." in result:
            return result
        return ""

@ctx.action_class("user")
class UserActions:
    # splits.py support begin
    def split_clear_all():
        actions.key("ctrl-x 1")

    def split_clear():
        actions.key("ctrl-x 1")

    def split_flip():
        pass

    def split_last():
        actions.key("ctrl-- ctrl-x o")

    def split_next():
        actions.key("ctrl-x o")

    def split_window_down():
        actions.key("ctrl-x 2 ctrl-x b enter ctrl-x o")

    def split_window_horizontally():
        actions.key("ctrl-x 2")

    def split_window_left():
        actions.key("ctrl-x 3 ctrl-x o ctrl-x b enter ctrl-x o")

    def split_window_right():
        actions.key("ctrl-x 3 ctrl-x b enter ctrl-x o")

    def split_window_up():
        actions.key("ctrl-x 2 ctrl-x o ctrl-x b enter ctrl-x o")

    def split_window_vertically():
        actions.key("ctrl-x 3")

    def split_window():
        actions.key("ctrl-x 3")

    # splits.py support end

    # snippet.py support begin
    def snippet_search(text: str):
        actions.key("ctrl-c & ctrl-s")
        actions.insert(text)

    def snippet_insert(text: str):
        actions.key("ctrl-c & ctrl-s")
        actions.insert(text)
        actions.key("enter")

    def snippet_create():
        actions.key("ctrl-c & ctrl-n")

    # snippet.py support end

    # dictation.py support start

    def dictation_peek_left(clobber: bool = False) -> Optional[str]:
        # Get rid of the selection if it exists.
        if clobber: actions.user.clobber_selection_if_exists()
        # Otherwise, if there's a selection, fail.
        elif "" != actions.edit.selected_text(): return None

        # In principle the previous word should suffice, but some applications
        # have a funny concept of what the previous word is (for example, they
        # may only take the "`" at the end of "`foo`"). To be double sure we
        # take two words left. I also tried taking a line up + a word left, but
        # edit.extend_up() = key(shift-up) doesn't work consistently in the
        # Slack webapp (sometimes escapes the text box).
        actions.edit.extend_word_left()
        actions.edit.extend_word_left()
        text = actions.edit.selected_text()
        # if we're at the beginning of the document/text box, we may not have
        # selected any text, in which case we shouldn't move the cursor.
        if text: actions.key("ctrl-u ctrl-space")
        return text

    def dictation_peek_right() -> Optional[str]:
        # We grab two characters because I think that's what no_space_before
        # needs in the worst case. An example where the second character matters
        # is inserting before (1) "' hello" vs (2) "'hello". In case (1) we
        # don't want to add space, in case (2) we do.
        actions.edit.extend_right()
        actions.edit.extend_right()
        after = actions.edit.selected_text()
        if after: actions.key("ctrl-u ctrl-space")
        return after

    # dictation.py support end

mod = Module()

@mod.action_class
class Actions:
    def jump_modulo_line(n: int):
        """Jumps to the nearest line number modulo 100."""
        actions.key("ctrl-u")
        actions.insert(str(n))
        actions.key("ctrl-c c g")

    def mark_lines(n1: int, n2: int=-1, tight: bool=False, tree: bool=False):
        """Marks the lines from n1 to n2."""
        actions.user.jump_modulo_line(n1)
        if tree:
            actions.key("alt-h")
            return
        if tight:
            actions.key("alt-m")
        actions.key("ctrl-space")
        if n2 != -1:
            actions.user.jump_modulo_line(n2)
        if tight:
            actions.key("ctrl-e")
        else:
            actions.key("down")

    def use_lines(n1: int, n2: int=-1,
                  pre_key: str="", post_key: str="",
                  tight: bool=False, other_buffer: bool=False, tree: bool=False):
        """Uses the lines from n1 to n2."""
        if other_buffer:
            actions.key("ctrl-x o")
        else:
            # Set mark without activating.
            actions.key("ctrl-\\")
        actions.user.mark_lines(n1, n2, tight, tree)
        if pre_key:
            actions.key(pre_key)
        # Jump back to the beginning of the selection.
        actions.key("ctrl-<")
        if other_buffer:
            actions.key("ctrl-x o")
        else:
            # Jump back to the original position.
            actions.key("ctrl-<")
        if not tight and not tree:
            actions.key("ctrl-a")
        if post_key:
            actions.key(post_key)
