from talon import Context, Module, actions

ctx = Context()
mod = Module()

mod.apps.claude_app = r"""
os: mac
and app.bundle: com.anthropic.claudefordesktop
"""

ctx.matches = r"""
app: claude_app
"""


@ctx.action_class("user")
class UserActions:
    def command_search(command: str = ""):
        actions.key("cmd-k")
        if command:
            actions.sleep("200ms")
            actions.insert(command)

    def split_window_right():
        actions.key("ctrl-cmd-\\")

    def split_window_down():
        actions.key("ctrl-cmd--")

    def split_window_vertically():
        actions.key("ctrl-cmd-\\")

    def split_window_horizontally():
        actions.key("ctrl-cmd--")

    def split_window():
        actions.key("ctrl-cmd-\\")

    def split_clear():
        actions.key("ctrl-cmd-w")

    def split_next():
        actions.key("ctrl-]")

    def split_last():
        actions.key("ctrl-[")
