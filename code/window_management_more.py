from talon import Context, actions, ui, Module, app, clip

mod = Module()
mod.list("docked_apps", desc="The indices of apps docked on the taskbar")
mod.list("known_window_names", desc="Known window substrings")

@mod.capture(rule="{self.known_window_names}")
def known_windows(m) -> ui.Window:
    if "::" in m.known_window_names:
        win, exe = m.known_window_names.split("::")
    else:
        win = m.known_window_names
        exe = None
    for app in ui.apps(background=False):
        for window in app.windows():
            if win in window.title and (not exe or exe in app.exe):
                return window

home_ctx = Context()
home_ctx.matches = r"""
hostname: Player-One
"""

home_ctx.lists["self.docked_apps"] = {
    "explorer": "1",
    "terminal": "2",
    "home terminal": "2",
    "firefox": "3",
    "browser": "3",
    "code": "4",
}

home_ctx.lists["self.known_window_names"] = {
    "rebel": "Talon - REPL",
    "emacs": "- Emacs editor (Ubuntu)",
    "dos": "system32\\cmd.exe",
}

work_ctx = Context()
work_ctx.matches = r"""
hostname: /jwstout/
"""

work_ctx.lists["self.docked_apps"] = {
    "explorer": "1",
    "home chrome": "2",
    "home browser": "2",
    "home emacs": "3",
    "emacs": "3",
    "work chrome": "4",
    "work browser": "4",
    "chrome": "4",
    "browser": "4",
    "code": "5",
}

work_ctx.lists["self.known_window_names"] = {
    "rebel": "Talon - REPL",
    "dos": "system32\\cmd.exe",
    "terminal": " - Terminal::Xpra-Launcher.exe",
    "work terminal": " - Terminal::Xpra-Launcher.exe",
    "work emacs": " - Emacs editor::Xpra-Launcher.exe",
    "studio": " - Android Studio::Xpra-Launcher.exe",
}
