from talon import Context, Module, ui

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
    "shell": "2",
    "home terminal": "2",
    "home shell": "2",
    "firefox": "3",
    "browser": "3",
    "emacs": "4",
    "home emacs": "4",
    "code": "5",
    "studio": "6",
    "spotify": "7",
}

home_ctx.lists["self.known_window_names"] = {
    "rebel": "Talon - REPL",
    "weasel emacs": "- Emacs editor (Ubuntu)",
    "linux emacs": "- Emacs editor (Ubuntu)",
    "dos": "system32\\cmd.exe",
}

work_windows_ctx = Context()
work_windows_ctx.matches = r"""
os: windows
hostname: /jwstout/
"""

work_windows_ctx.lists["self.docked_apps"] = {
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

work_windows_ctx.lists["self.known_window_names"] = {
    "rebel": "Talon - REPL",
    "dos": "system32\\cmd.exe",
    "terminal": " - Terminal::Xpra-Launcher.exe",
    "shell": " - Terminal::Xpra-Launcher.exe",
    "work terminal": " - Terminal::Xpra-Launcher.exe",
    "work shell": " - Terminal::Xpra-Launcher.exe",
    "work emacs": " - Emacs editor::Xpra-Launcher.exe",
    "studio": " - Android Studio::Xpra-Launcher.exe",
}

work_mac_ctx = Context()
work_mac_ctx.matches = r"""
os: mac
hostname: /jwstout/
"""

work_mac_ctx.lists["self.known_window_names"] = {
    "work terminal": " - Terminal::Xpra",
    "work shell": " - Terminal::Xpra",
    "work emacs": " - Emacs editor::Xpra",
    "studio": " - Android Studio::Xpra",
}
