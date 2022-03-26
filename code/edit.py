import time
from talon import Context, Module, actions, clip, ui

ctx = Context()
mod = Module()
setting_clipboard_delay = mod.setting(
    "clipboard_delay",
    type=str,
    default="",
    desc="Delay before and after accessing clipboard contents.",
)


@ctx.action_class("edit")
class EditActions:
    def selected_text() -> str:
        with clip.capture() as s:
            if setting_clipboard_delay.get():
                actions.sleep(setting_clipboard_delay.get())
            actions.edit.copy()
            if setting_clipboard_delay.get():
                actions.sleep(setting_clipboard_delay.get())
        try:
            return s.get()
        except clip.NoChange:
            return ""
    def line_insert_down():
        actions.edit.line_end()
        actions.key("enter")


@mod.action_class
class Actions:
    def paste(text: str):
        """Pastes text and preserves clipboard"""

        with clip.revert():
            clip.set_text(text)
            actions.edit.paste()
            # sleep here so that clip.revert doesn't revert the clipboard too soon
            actions.sleep("150ms")

    def words_left(n: int):
        """Moves left by n words."""
        for _ in range(n):
            actions.edit.word_left()

    def words_right(n: int):
        """Moves right by n words."""
        for _ in range(n):
            actions.edit.word_right()
