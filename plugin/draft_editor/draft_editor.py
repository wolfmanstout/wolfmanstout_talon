from talon import Context, Module, actions, app, settings, ui

mod = Module()
mod.tag("draft_editor_active", "Indicates whether the draft editor has been activated")
mod.tag(
    "draft_editor_app_running",
    "Indicates that the draft editor app currently is running",
)
mod.tag(
    "draft_editor_app_focused",
    "Indicates that the draft editor app currently has focus",
)

ctx = Context()
tags: set[str] = set()


def add_tag(tag: str):
    if tag not in tags:
        tags.add(tag)
        ctx.tags = list(tags)


def remove_tag(tag: str):
    if tag in tags:
        tags.discard(tag)
        ctx.tags = list(tags)


default_names = ["Visual Studio Code", "Code", "VSCodium", "Codium", "code-oss"]

mod.setting(
    "draft_editor",
    type=str,
    default=None,
    desc="List of application names to use for draft editor",
)


def get_editor_names():
    names_csv = settings.get("user.draft_editor")
    return names_csv.split(", ") if names_csv else default_names


def handle_app_running(_app):
    editor_names = get_editor_names()
    for app in ui.apps(background=False):
        if app.name in editor_names:
            add_tag("user.draft_editor_app_running")
            return
    remove_tag("user.draft_editor_app_running")


def handle_app_activate(app):
    if app.name in get_editor_names():
        add_tag("user.draft_editor_app_focused")
    else:
        remove_tag("user.draft_editor_app_focused")


def on_ready():
    ui.register("app_launch", handle_app_running)
    ui.register("app_close", handle_app_running)
    ui.register("app_activate", handle_app_activate)

    handle_app_running(None)
    handle_app_activate(ui.active_app())


app.register("ready", on_ready)

original_window = None

last_draft = None

diff_mode = False


@mod.action_class
class Actions:
    def draft_editor_open(contents: str = ""):
        """Open draft editor. If contents is not provided, use selected text."""
        global original_window, diff_mode
        original_window = ui.active_window()
        diff_mode = False
        editor_app = get_editor_app()
        selected_text = actions.edit.selected_text()
        actions.user.switcher_focus_app(editor_app)
        # Wait additional time for talon context to update.
        actions.sleep("200ms")
        actions.app.tab_open()
        if contents:
            actions.user.paste(contents)
        elif selected_text:
            actions.user.paste(selected_text)
        add_tag("user.draft_editor_active")

    def draft_editor_open_diff(old: str = "", new: str = ""):
        """Open draft editor with diff view. If old or new is not provided, use selected
        text."""
        global original_window, diff_mode
        original_window = ui.active_window()
        diff_mode = True
        editor_app = get_editor_app()
        selected_text = actions.edit.selected_text()
        actions.user.switcher_focus_app(editor_app)
        # Wait additional time for talon context to update.
        actions.sleep("200ms")
        actions.user.vscode_and_wait(
            "workbench.files.action.compareNewUntitledTextFiles"
        )
        actions.user.vscode_and_wait("diffEditor.switchSide")
        if old:
            actions.user.paste(old)
        elif selected_text != "":
            actions.user.paste(selected_text)
        actions.user.vscode_and_wait("diffEditor.switchSide")
        if new:
            actions.user.paste(new)
        elif selected_text:
            actions.user.paste(selected_text)
        add_tag("user.draft_editor_active")

    def draft_editor_submit():
        """Submit/save draft editor"""
        close_editor(submit_draft=True)

    def draft_editor_discard():
        """Discard draft editor"""
        close_editor(submit_draft=False)

    def draft_editor_paste_last():
        """Paste last submitted draft"""
        if last_draft:
            actions.user.paste(last_draft)


def get_editor_app() -> ui.App:
    editor_names = get_editor_names()

    for app in ui.apps(background=False):
        if app.name in editor_names:
            return app

    raise RuntimeError("Draft editor is not running")


def close_editor(submit_draft: bool) -> None:
    global last_draft

    actions.edit.select_all()

    if submit_draft:
        actions.sleep("50ms")
        last_draft = actions.edit.selected_text()

        if not last_draft:
            actions.app.notify("Failed to get draft document text")
            return

    remove_tag("user.draft_editor_active")

    actions.edit.delete()
    if diff_mode:
        actions.user.vscode("diffEditor.switchSide")
        actions.edit.select_all()
        actions.edit.delete()
    actions.app.tab_close()

    if submit_draft:
        try:
            actions.user.switcher_focus_window(original_window)
        except Exception:
            app.notify(
                "Failed to focus on window to submit draft, manually focus intended destination and use 'draft submit' again"
            )
        else:
            actions.sleep("300ms")
            actions.user.paste(last_draft)
    else:
        try:
            actions.user.switcher_focus_window(original_window)
        except Exception:
            app.notify("Failed to focus previous window, leaving editor open")
