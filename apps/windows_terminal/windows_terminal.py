import os
from typing import Optional

from talon import Context, Module, actions, ui

ctx = Context()
mod = Module()
ctx.matches = r"""
app: windows_terminal
"""

wsl_ctx = Context()
wsl_ctx.matches = r"""
app: windows_terminal
title: / - Terminal/
"""

user_path = os.path.expanduser("~")
directories_to_remap = {}
directories_to_exclude = {}


@ctx.action_class("app")
class AppActions:
    def tab_close():
        actions.key("ctrl-shift-w")

    def tab_open():
        actions.key("ctrl-shift-t")


@ctx.action_class("edit")
class EditActions:
    def paste():
        actions.key("ctrl-shift-v")

    def copy():
        actions.key("ctrl-shift-c")

    def find(text: str = None):
        actions.key("ctrl-shift-f")
        if text:
            actions.insert(text)


@ctx.action_class("user")
class UserActions:
    def file_manager_current_path():
        path = ui.active_window().title
        path = (
            path.replace("Administrator:  ", "")
            .replace("Windows PowerShell: ", "")
            .replace("Command Prompt: ", "")
        )

        if path in directories_to_remap:
            path = directories_to_remap[path]

        if path in directories_to_exclude:
            path = ""
        return path

    # def file_manager_terminal_here():
    #     actions.key("ctrl-l")
    #     actions.insert("cmd.exe")
    #     actions.key("enter")

    # def file_manager_show_properties():
    #     """Shows the properties for the file"""
    #     actions.key("alt-enter")

    def file_manager_open_directory(path: str):
        """opens the directory that's already visible in the view"""
        actions.insert(f'cd "{path}"')
        actions.key("enter")
        actions.user.file_manager_refresh_title()

    def file_manager_select_directory(path: str):
        """selects the directory"""
        actions.insert(f'"{path}"')

    def file_manager_new_folder(name: str):
        """Creates a new folder in a gui filemanager or inserts the command to do so for terminals"""
        actions.insert(f'mkdir "{name}"')

    def file_manager_open_file(path: str):
        """opens the file"""
        actions.insert(path)
        # actions.key("enter")

    def file_manager_select_file(path: str):
        """selects the file"""
        actions.insert(path)

    def file_manager_open_volume(volume: str):
        """file_manager_open_volume"""
        actions.user.file_manager_open_directory(volume)
        actions.user.file_manager_refresh_title()

    def tab_jump(number: int):
        actions.key(f"ctrl-alt-{number}")

    # user.splits implementation:

    def split_window_right():
        """Move active tab to right split"""
        # TODO: decide whether this notification is good style
        actions.app.notify(
            '"Split right" is not possible in windows terminal without special configuration. Use "split vertically" instead.'
        )

    def split_window_left():
        """Move active tab to left split"""
        # TODO: decide whether this notification is good style
        actions.app.notify(
            '"Split left" is not possible in windows terminal without special configuration. Use "split vertically" instead.'
        )

    def split_window_down():
        """Move active tab to lower split"""
        # TODO: decide whether this notification is good style
        actions.app.notify(
            '"Split down" is not possible in windows terminal without special configuration. Use "split horizontally" instead.'
        )

    def split_window_up():
        """Move active tab to upper split"""
        # TODO: decide whether this notification is good style
        actions.app.notify(
            '"Split up" is not possible in windows terminal without special configuration. Use "split horizontally" instead.'
        )

    def split_window_vertically():
        """Splits window vertically"""
        actions.key("shift-alt-plus")

    def split_window_horizontally():
        """Splits window horizontally"""
        actions.key("shift-alt-minus")

    def split_flip():
        """Flips the orietation of the active split"""
        # TODO: decide whether this notification is good style
        actions.app.notify(
            '"Split flip" is not possible in windows terminal in default configuration.'
        )

    def split_window():
        """Splits the window"""
        # in this implementation an alias for split vertically
        actions.key("shift-alt-plus")

    def split_clear():
        """Clears the current split"""
        # also closes tab, because shortcut is the same
        # and closing a split does mean something differnent that in a code editor like vs code
        actions.key("ctrl-shift-w")

    def split_clear_all():
        """Clears all splits"""
        # TODO: decide whether to implement it at all since it either doesn't makes sense or closes the window/whole tab

    def split_next():
        """Goes to next split"""
        # TODO: decide whether this notification is good style
        actions.app.notify(
            '"Split next" is not possible in windows terminal without special configuration. Use "focus left/right/up/down" instead.'
        )

    def split_last():
        """Goes to last split"""
        # TODO: decide whether this notification is good style
        actions.app.notify(
            '"Split last" is not possible in windows terminal without special configuration. Use "focus left/right/up/down" instead.'
        )

    def split_number(index: int):
        """Navigates to a the specified split"""
        actions.app.notify(
            '"Split_number" is not possible in windows terminal in default configuration.'
        )

    def tab_final():
        actions.key("ctrl-alt-9")


@wsl_ctx.action_class("user")
class WslUserActions:
    def dictation_peek(left: bool, right: bool) -> tuple[Optional[str], Optional[str]]:
        if not (left or right):
            return None, None
        before, after = None, None
        # Inserting a character ensures we select something even if we're at
        # document start; some editors 'helpfully' copy the current line if we
        # edit.copy() while nothing is selected. We use "." instead of " "
        # because Gmail Chat merges adjacent whitespace in the clipboard.
        actions.insert(".")
        if left:
            actions.key("ctrl-shift-m")
            actions.edit.left()
            # In principle the previous word should suffice, but some applications
            # have a funny concept of what the previous word is (for example, they
            # may only take the "`" at the end of "`foo`"). To be double sure we
            # take three words left. I also tried taking a line up + a word left, but
            # edit.extend_up() = key(shift-up) doesn't work consistently in the
            # Slack webapp (sometimes escapes the text box).
            actions.edit.extend_word_left()
            actions.edit.extend_word_left()
            actions.edit.extend_word_left()
            selected_text = actions.edit.selected_text()
            if selected_text and selected_text[-1] == ".":
                before = selected_text[:-1]
            elif (
                selected_text and selected_text[-2:] == ".\n"
            ):  # Observed in Google Docs after a bullet.
                before = selected_text[:-2]
            else:
                logging.warning(
                    f"Selected text did not contain newly-added period: {selected_text}"
                )
                before = selected_text
        if not right:
            actions.key("backspace")  # remove the space
        else:
            actions.key("ctrl-shift-m")
            actions.edit.left()  # go left before space
            # We want to select at least two characters to the right, plus the space
            # we inserted, because no_space_before needs two characters in the worst
            # case -- for example, inserting before "' hello" we don't want to add
            # space, while inserted before "'hello" we do.
            #
            # We use 3x extend_word_right() because it's fewer keypresses (lower
            # latency) than 3x extend_right(). Other options all seem to have
            # problems. For instance, extend_line_end() might not select all the way
            # to the next newline if text has been wrapped across multiple lines;
            # extend_line_down() sometimes escapes the current text box (eg. in a
            # browser address bar). 1x extend_word_right() _usually_ works, but on
            # Windows in Firefox it doesn't always select enough characters.
            actions.edit.extend_word_right()
            actions.edit.extend_word_right()
            actions.edit.extend_word_right()
            selection = actions.edit.selected_text()
            if selection:
                after = selection[1:]
            else:
                # Observed on Mac in Gmail.
                print("Unable to get selected text.")
                after = ""
            actions.edit.left()
            actions.key("delete")  # remove space
        return before, after
