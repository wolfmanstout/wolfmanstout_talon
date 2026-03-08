import logging

from talon import Module, ui

mod = Module()


@mod.action_class
class Actions:
    def log_tracker_disconnect():
        """Log when the tracker disconnects."""
        logging.debug("Eye tracker disconnected")


ui.register("screen_wake", lambda *a: print(f"SCREEN WAKE {a}"))
