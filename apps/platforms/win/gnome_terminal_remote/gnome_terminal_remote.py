from talon import Context, Module, actions

mod = Module()
mod.apps.gnome_terminal_remote = r"""
title: / - Terminal/
and not app: windows_terminal
"""

ctx = Context()
ctx.matches = r"""
app: gnome_terminal_remote
"""


@ctx.action_class("app")
class AppActions:
    def tab_close():
        actions.key("ctrl-shift-w")

    def tab_open():
        actions.key("ctrl-shift-t")

    def tab_next():
        actions.key("ctrl-shift-right")

    def tab_previous():
        actions.key("ctrl-shift-left")


@ctx.action_class("edit")
class EditActions:
    def copy():
        actions.key("ctrl-shift-c")

    def cut():
        actions.key("ctrl-shift-x")

    def paste():
        actions.key("ctrl-shift-v")


@ctx.action_class("user")
class UserActions:
    def tab_jump(number: int):
        actions.key(f"alt-{number}")

    def tab_final():
        actions.key("alt-1 ctrl-shift-left")
