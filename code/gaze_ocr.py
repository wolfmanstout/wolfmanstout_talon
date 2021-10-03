from talon import Module, actions

import gaze_ocr
import screen_ocr  # dependency of gaze-ocr
from gaze_ocr import _talon_wrappers as talon_wrappers

# Initialize eye tracking and OCR. See installation instructions:
# https://github.com/wolfmanstout/gaze-ocr
tracker = gaze_ocr.eye_tracking.EyeTracker.get_connected_instance(None)
ocr_reader = screen_ocr.Reader.create_fast_reader()
gaze_ocr_controller = gaze_ocr.Controller(
    ocr_reader,
    tracker,
    save_data_directory=r"C:\Users\james\Documents\OCR\logs",
    mouse=talon_wrappers.Mouse(),
    keyboard=talon_wrappers.Keyboard())
 
mod = Module()

@mod.capture(rule="<user.text> | <number>")
def onscreen_text(m) -> str:
    """Either words or a number."""
    try:
        return m.text
    except AttributeError:
        return str(m.number)

@mod.action_class
class GazeOcrActions:
    def move_cursor_to_word(text: str):
        """Moves cursor to onscreen word."""
        gaze_ocr_controller.start_reading_nearby()
        if not gaze_ocr_controller.move_cursor_to_word(text):
            raise RuntimeError("Unable to find: " + text)

    def move_text_cursor_to_word(text: str, position: str):
        """Moves text cursor near onscreen word."""
        gaze_ocr_controller.start_reading_nearby()
        if not gaze_ocr_controller.move_text_cursor_to_word(text, position):
            raise RuntimeError("Unable to find: " + text)

    def select_text(start: str, end: str="", for_deletion: int=0):
        """Selects text near onscreen word."""
        gaze_ocr_controller.start_reading_nearby()
        if not gaze_ocr_controller.select_text(start, end, for_deletion):
            raise RuntimeError("Unable to select {} to {}".format(start, end))

    def move_cursor_to_gaze_point(offset_right: int=0, offset_down: int=0):
        """Moves mouse cursor to gaze location."""
        tracker.move_to_gaze_point((offset_right, offset_down))
