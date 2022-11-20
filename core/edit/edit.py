from talon import Context, Module, actions, clip

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
            return s.text()
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

    def cut_word_left():
        """Cuts the word to the left."""
        actions.edit.extend_word_left()
        actions.edit.cut()

    def cut_word_right():
        """Cuts the word to the right."""
        actions.edit.extend_word_right()
        actions.edit.cut()

    def cut_line():
        """Cuts the current line."""
        actions.edit.select_line()
        actions.edit.cut()

    def copy_word_left():
        """Copies the word to the left."""
        actions.edit.extend_word_left()
        actions.edit.copy()

    def copy_word_right():
        """Copies the word to the right."""
        actions.edit.extend_word_right()
        actions.edit.copy()

    def bold():
        """Toggles bold formatting."""

    def italic():
        """Toggles italic formatting."""

    def strikethrough():
        """Toggles strikethrough formatting."""

    def number_list():
        """Toggles numbered list."""

    def bullet_list():
        """Toggles bullet list."""

    def hyperlink():
        """Inserts a hyperlink."""
