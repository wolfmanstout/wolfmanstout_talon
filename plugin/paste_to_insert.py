from talon import Context, Module, actions, settings

mod = Module()
ctx = Context()

mod.setting(
    "paste_to_insert_threshold",
    type=int,
    default=-1,
    desc="""Use paste to insert text longer than this many characters.
Zero means always paste; -1 means never paste.
""",
)

mod.setting(
    "paste_to_insert_newlines",
    type=bool,
    default=True,
    desc="""Always paste text containing newlines to avoid editor handling of enter key.
This prevents unwanted form submission or other enter key behaviors.
""",
)


def is_horizontal_whitespace(char: str) -> bool:
    return char.isspace() and char not in "\r\n"


def split_surrounding_horizontal_whitespace(text: str) -> tuple[str, str, str]:
    start = 0
    while start < len(text) and is_horizontal_whitespace(text[start]):
        start += 1

    end = len(text)
    while end > start and is_horizontal_whitespace(text[end - 1]):
        end -= 1

    return text[:start], text[start:end], text[end:]


def should_paste_to_insert(text: str, threshold: int, paste_newlines: bool) -> bool:
    _, text_to_paste, _ = split_surrounding_horizontal_whitespace(text)
    if not text_to_paste:
        return False
    return 0 <= threshold and (
        threshold < len(text_to_paste) or (paste_newlines and "\n" in text_to_paste)
    )


@ctx.action_class("main")
class MainActions:
    def insert(text: str):
        threshold: int = settings.get("user.paste_to_insert_threshold")  # type: ignore
        paste_newlines: bool = settings.get("user.paste_to_insert_newlines")  # type: ignore
        # If paste_to_insert is available, paste newlines to avoid editor
        # handling of enter key (which could submit a form, for example).
        if should_paste_to_insert(text, threshold, paste_newlines):
            leading, text_to_paste, trailing = split_surrounding_horizontal_whitespace(
                text
            )
            if leading:
                actions.next(leading)
            actions.user.paste(text_to_paste)
            if trailing:
                actions.next(trailing)
            return
        actions.next(text)
