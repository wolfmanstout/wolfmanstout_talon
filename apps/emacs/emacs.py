from talon import Context, actions
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
    def find(text: str=None):
        actions.key('ctrl-s')
        actions.actions.insert(text)
    def find_next():
        actions.key('ctrl-s')
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
