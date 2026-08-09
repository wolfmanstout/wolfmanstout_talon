from talon import Context, actions

ctx = Context()
ctx.matches = r"""
tag: browser
title: /<todoist.com>/
"""


@ctx.action_class("user")
class UserActions:
    def command_search(command: str = ""):
        actions.key("ctrl-k")
        if command:
            actions.insert(command)
