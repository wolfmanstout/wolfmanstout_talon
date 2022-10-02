from talon import Context, Module, actions

mod = Module()


@mod.action_class
class Actions:
    def browser_match_next():
        """Go to next match."""

    def browser_match_previous():
        """Go to previous match."""


mac_ctx = Context()
mac_ctx.matches = r"""
tag: browser
os: mac
"""


@mac_ctx.action_class("user")
class MacActions:
    def browser_match_next():
        actions.key("cmd-g")

    def browser_match_previous():
        actions.key("cmd-shift-g")


@mac_ctx.action_class("edit")
class MacActions:
    def file_end():
        actions.key("cmd-down")

    def file_start():
        actions.key("cmd-up")


win_ctx = Context()
win_ctx.matches = r"""
tag: browser
os: win
"""


@win_ctx.action_class("user")
class WinActions:
    def browser_match_next():
        actions.key("ctrl-g")

    def browser_match_previous():
        actions.key("ctrl-shift-g")
