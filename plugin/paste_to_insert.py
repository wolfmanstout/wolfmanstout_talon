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


@ctx.action_class("main")
class MainActions:
    def insert(text: str):
        threshold: int = settings.get("user.paste_to_insert_threshold")  # type: ignore
        # If paste_to_insert is available, always paste newlines to avoid editor
        # handling of enter key (which could submit a form, for example).
        if 0 <= threshold and (threshold < len(text) or "\n" in text):
            actions.user.paste(text)
            return
        actions.next(text)
