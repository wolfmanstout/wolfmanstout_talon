import logging

from talon import Module

mod = Module()


@mod.action_class
class Actions:
    def log_tracker_disconnect():
        """Log when the tracker disconnects."""
        logging.debug("Eye tracker disconnected")
