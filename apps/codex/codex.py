from talon import Context, Module, actions

ctx = Context()
mod = Module()

mod.apps.codex = r"""
os: mac
and app.bundle: com.openai.codex
"""

ctx.matches = r"""
app: codex
"""


@ctx.action_class("user")
class UserActions:
    def command_search(command: str = ""):
        actions.key("cmd-k")
        if command:
            actions.sleep("200ms")
            actions.insert(command)
