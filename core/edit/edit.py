import logging
import os
import platform
import subprocess
from typing import Optional

from talon import Context, Module, actions, clip, settings

ctx = Context()
mod = Module()

mod.setting(
    "selected_text_timeout",
    type=float,
    default=0.25,
    desc="Time in seconds to wait for the clipboard to change when trying to get selected text",
)

mod.setting(
    "markitdown_path",
    type=str,
    default="markitdown",
    desc="Path to the markitdown CLI executable for HTML to markdown conversion",
)

mod.setting(
    "strip_tags_path",
    type=str,
    default="strip-tags",
    desc="Path to the strip-tags CLI executable for HTML cleanup",
)

END_OF_WORD_SYMBOLS = ".!?;:—_/\\|@#$%^&*()[]{}<>=+-~`"


def extract_clip_html() -> str:
    """Extract HTML content from clipboard"""
    html_data = clip.mime().html
    if not html_data:
        return ""

    # Windows uses a special HTML clipboard format with headers and offsets
    if platform.system() == "Windows":
        # Parse the header to find StartFragment and EndFragment offsets
        lines = html_data.split("\r\n")
        start_fragment = None
        end_fragment = None

        for line in lines:
            if line.startswith("StartFragment:"):
                start_fragment = int(line.split(":")[1])
            elif line.startswith("EndFragment:"):
                end_fragment = int(line.split(":")[1])

        if start_fragment is None or end_fragment is None:
            return ""

        # Extract the HTML fragment using the offsets
        html_fragment = html_data[start_fragment:end_fragment]
        return html_fragment
    else:
        # On Mac and other platforms, HTML mime data is the raw HTML
        return html_data


def set_mime_html(html_content: str):
    """Set HTML content to clipboard"""
    mime = clip.mime()

    # Windows uses a special HTML clipboard format with headers and offsets
    if platform.system() == "Windows":
        # Wrap the content in a proper HTML document with fragment markers
        html_doc = f"""<html>
<body>
<!--StartFragment-->{html_content}<!--EndFragment-->
</body>
</html>"""

        # Calculate byte offsets for the header
        version = "Version:0.9\r\n"
        start_html_marker = "StartHTML:"
        end_html_marker = "EndHTML:"
        start_fragment_marker = "StartFragment:"
        end_fragment_marker = "EndFragment:"
        source_url_marker = "SourceURL:about:blank\r\n"

        # Build header with placeholder offsets to calculate positions
        header_template = f"{version}{start_html_marker}0000000000\r\n{end_html_marker}0000000000\r\n{start_fragment_marker}0000000000\r\n{end_fragment_marker}0000000000\r\n{source_url_marker}"

        # Calculate actual offsets
        header_length = len(header_template)
        start_html = header_length
        start_fragment = (
            start_html
            + html_doc.find("<!--StartFragment-->")
            + len("<!--StartFragment-->")
        )
        end_fragment = start_html + html_doc.find("<!--EndFragment-->")
        end_html = start_html + len(html_doc)

        # Build final header with correct offsets (10 digits, zero-padded)
        header = f"{version}{start_html_marker}{start_html:010d}\r\n{end_html_marker}{end_html:010d}\r\n{start_fragment_marker}{start_fragment:010d}\r\n{end_fragment_marker}{end_fragment:010d}\r\n{source_url_marker}"

        # Combine header and HTML
        clipboard_data = header + html_doc
        mime.html = clipboard_data
    else:
        # On Mac and other platforms, set raw HTML directly
        mime.html = html_content

    clip.set_mime(mime)


def convert_html_to_markdown(html: str) -> Optional[str]:
    """Convert HTML to markdown using markitdown CLI"""
    # Configure output encoding
    process_env = os.environ.copy()
    if platform.system() == "Windows":
        process_env["PYTHONUTF8"] = "1"  # For Python 3.7+ to enable UTF-8 mode
    # On other platforms, UTF-8 is also the common/expected encoding.
    text_encoding = "utf-8"

    try:
        markitdown_path: str = settings.get("user.markitdown_path")  # type: ignore
        markdown = subprocess.check_output(
            [markitdown_path, "-x", "html"],
            input=html,
            encoding=text_encoding,
            stderr=subprocess.PIPE,
            creationflags=(
                subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0  # type: ignore
            ),
            env=process_env if platform.system() == "Windows" else None,
        ).strip()
        return markdown
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        logging.error(f"Error converting HTML to markdown: {error_msg}")
        return None
    except Exception as e:
        logging.error(f"Error converting HTML to markdown: {str(e)}")
        return None


def clean_html(html: str) -> Optional[str]:
    """Clean HTML using strip-tags CLI with allowlist for links, lists, and headings"""
    # Configure output encoding
    process_env = os.environ.copy()
    if platform.system() == "Windows":
        process_env["PYTHONUTF8"] = "1"  # For Python 3.7+ to enable UTF-8 mode
    # On other platforms, UTF-8 is also the common/expected encoding.
    text_encoding = "utf-8"

    try:
        strip_tags_path: str = settings.get("user.strip_tags_path")  # type: ignore

        # Define allowed tags and tag categories
        allowed_tags = [
            "hs",  # All heading levels (h1, h2, etc.)
            "lists",  # List tags (ul, ol, li)
            "a",  # Links
            "b",
            "strong",  # Bold
            "i",
            "em",  # Italics
            "s",
            "strike",
            "del",  # Strikethrough
            "u",  # Underline
        ]

        # Build command arguments
        cmd_args = [strip_tags_path]
        for tag in allowed_tags:
            cmd_args.extend(["-t", tag])

        cleaned_html = subprocess.check_output(
            cmd_args,
            input=html,
            encoding=text_encoding,
            stderr=subprocess.PIPE,
            creationflags=(
                subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0  # type: ignore
            ),
            env=process_env if platform.system() == "Windows" else None,
        ).strip()
        return cleaned_html
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else str(e)
        logging.error(f"Error cleaning HTML: {error_msg}")
        return None
    except Exception as e:
        logging.error(f"Error cleaning HTML: {str(e)}")
        return None


@ctx.action_class("edit")
class EditActions:
    def selected_text() -> str:
        timeout = settings.get("user.selected_text_timeout")
        with clip.capture(timeout) as s:
            actions.edit.copy()
        try:
            return s.text()
        except clip.NoChange:
            return ""

    def line_insert_down():
        actions.edit.line_end()
        actions.key("enter")

    def selection_clone():
        actions.edit.copy()
        actions.edit.select_none()
        actions.edit.paste()

    def line_clone():
        # This may not work if editor auto-indents. Is there a better way?
        actions.edit.line_start()
        actions.edit.extend_line_end()
        actions.edit.copy()
        actions.edit.right()
        actions.key("enter")
        actions.edit.paste()

    # # This simpler implementation of select_word mostly works, but in some apps it doesn't.
    # # See https://github.com/talonhub/community/issues/1084.
    # def select_word():
    #     actions.edit.right()
    #     actions.edit.word_left()
    #     actions.edit.extend_word_right()

    def select_word():
        actions.edit.extend_right()
        character_to_right_of_initial_caret_position = actions.edit.selected_text()

        # Occasionally apps won't let you edit.extend_right()
        # and therefore won't select text if your caret is on the rightmost character
        # such as in the Chrome URL bar
        did_select_text = character_to_right_of_initial_caret_position != ""

        if did_select_text:
            # .strip() turns newline & space characters into empty string; the empty
            # string is in any other string, so this works.
            if (
                character_to_right_of_initial_caret_position.strip()
                in END_OF_WORD_SYMBOLS
            ):
                # Come out of the highlight in the initial position.
                actions.edit.left()
            else:
                # Come out of the highlight one character
                # to the right of the initial position.
                actions.edit.right()

        actions.edit.word_left()
        actions.edit.extend_word_right()


@mod.action_class
class Actions:
    def paste(text: str):
        """Pastes text and preserves clipboard"""

        with clip.revert():
            clip.set_text(text)
            actions.edit.paste()
            # sleep here so that clip.revert doesn't revert the clipboard too soon
            actions.sleep("150ms")

    def paste_html():
        """Paste HTML content from clipboard"""
        html_content = extract_clip_html()
        if html_content:
            actions.user.paste(html_content)

    def paste_markdown():
        """Paste HTML content from clipboard converted to markdown"""
        html_content = extract_clip_html()
        if html_content:
            markdown_content = convert_html_to_markdown(html_content)
            if markdown_content:
                actions.user.paste(markdown_content)

    def paste_clean():
        """Paste HTML content from clipboard after cleaning it up"""
        html_content = extract_clip_html()
        if html_content:
            cleaned_html = clean_html(html_content)
            if cleaned_html:
                with clip.revert():
                    set_mime_html(cleaned_html)
                    actions.edit.paste()
                    # sleep here so that clip.revert doesn't revert the clipboard too soon
                    actions.sleep("150ms")

    def delete_right():
        """Delete character to the right"""
        actions.key("delete")

    def delete_all():
        """Delete all text in the current document"""
        actions.edit.select_all()
        actions.edit.delete()

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

    def copy_word_left():
        """Copies the word to the left."""
        actions.edit.extend_word_left()
        actions.edit.copy()

    def copy_word_right():
        """Copies the word to the right."""
        actions.edit.extend_word_right()
        actions.edit.copy()

    # ----- Start / End of line -----
    def select_line_start():
        """Select to start of current line"""
        if actions.edit.selected_text():
            actions.edit.left()
        actions.edit.extend_line_start()

    def select_line_end():
        """Select to end of current line"""
        if actions.edit.selected_text():
            actions.edit.right()
        actions.edit.extend_line_end()

    def line_middle():
        """Go to the middle of the line"""
        actions.edit.select_line()
        half_line_length = int(len(actions.edit.selected_text()) / 2)
        actions.edit.left()
        for i in range(0, half_line_length):
            actions.edit.right()

    def cut_line():
        """Cut current line"""
        actions.edit.select_line()
        actions.edit.cut()

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
