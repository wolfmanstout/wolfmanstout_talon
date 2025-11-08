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


@ctx.action_class("main")
class MainActions:
    def insert(text: str):
        threshold: int = settings.get("user.paste_to_insert_threshold")  # type: ignore
        paste_newlines: bool = settings.get("user.paste_to_insert_newlines")  # type: ignore
        # If paste_to_insert is available, paste newlines to avoid editor
        # handling of enter key (which could submit a form, for example).
        if 0 <= threshold and (
            threshold < len(text) or (paste_newlines and "\n" in text)
        ):
            actions.user.paste(text)
            return
        actions.next(text)
