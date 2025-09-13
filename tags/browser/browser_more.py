from urllib.parse import quote_plus

from talon import Context, Module, actions

mod = Module()
mod.list(
    "browser_search_engine", desc="A browser built-in search engine accessible via tab"
)


@mod.action_class
class Actions:
    def browser_match_next():
        """Go to next match."""

    def browser_match_previous():
        """Go to previous match."""

    def browser_search_with_search_engine(search_template: str, search_text: str):
        """Search using a search engine by constructing and entering the URL in the address bar"""
        url = search_template.replace("%s", quote_plus(search_text))
        actions.browser.focus_address()
        actions.insert(url)
        actions.key("enter")


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
os: windows
"""


@win_ctx.action_class("user")
class WinActions:
    def browser_match_next():
        actions.key("ctrl-g")

    def browser_match_previous():
        actions.key("ctrl-shift-g")
