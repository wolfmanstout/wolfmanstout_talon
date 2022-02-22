from typing import Union

from talon import Context, Module, actions, app
from talon.grammar import Phrase

import gaze_ocr
import screen_ocr  # dependency of gaze-ocr
from gaze_ocr import _talon_wrappers as talon_wrappers

mod = Module()

setting_ocr_logging_dir = mod.setting(
    "ocr_logging_dir",
    type=str,
    default=None,
    desc="If specified, log OCR'ed images to this directory.",
)

def on_ready():
    # Initialize eye tracking and OCR. See installation instructions:
    # https://github.com/wolfmanstout/gaze-ocr
    global tracker, ocr_reader, gaze_ocr_controller
    tracker = gaze_ocr.eye_tracking.TalonEyeTracker()
    ocr_reader = screen_ocr.Reader.create_fast_reader(radius=200)
    gaze_ocr_controller = gaze_ocr.Controller(
        ocr_reader,
        tracker,
        save_data_directory=setting_ocr_logging_dir.get(),
        mouse=talon_wrappers.Mouse(),
        keyboard=talon_wrappers.Keyboard())

app.register("ready", on_ready)

@mod.action_class
class GazeOcrActions:
    def move_cursor_to_word(text: Phrase):
        """Moves cursor to onscreen word."""
        if not gaze_ocr_controller.move_cursor_to_word(str(text), timestamp=text.words[0].start):
            raise RuntimeError("Unable to find: \"{}\"".format(text))

    def move_text_cursor_to_word(text: Phrase, position: str):
        """Moves text cursor near onscreen word."""
        if not gaze_ocr_controller.move_text_cursor_to_word(str(text), position, timestamp=text.words[0].start):
            raise RuntimeError("Unable to find: \"{}\"".format(text))

    def move_text_cursor_to_word_ignore_errors(text: Phrase, position: str):
        """Moves text cursor near onscreen word, ignoring errors (log only)."""
        if not gaze_ocr_controller.move_text_cursor_to_word(str(text), position, timestamp=text.words[0].start):
            print("Unable to find: \"{}\"".format(text))

    def select_text(start: Phrase, end: Union[Phrase, str]=None,
                    for_deletion: bool=False):
        """Selects text near onscreen word at phrase timestamps."""
        if not gaze_ocr_controller.select_text(
                str(start), str(end), for_deletion,
                start.words[0].start,
                end.words[0].start if end else start.words[-1].end):
            raise RuntimeError("Unable to select \"{}\" to \"{}\"".format(start, end))

    def move_cursor_to_gaze_point(offset_right: int=0, offset_down: int=0):
        """Moves mouse cursor to gaze location."""
        tracker.move_to_gaze_point((offset_right, offset_down))
