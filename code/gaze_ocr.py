from talon import Module, actions

import gaze_ocr
import screen_ocr  # dependency of gaze-ocr

# See installation instructions:
# https://github.com/wolfmanstout/gaze-ocr
DLL_DIRECTORY = "c:/Users/james/Downloads/tobii.interaction.0.7.3/"

# Initialize eye tracking and OCR.
tracker = gaze_ocr.eye_tracking.EyeTracker.get_connected_instance(DLL_DIRECTORY)
ocr_reader = screen_ocr.Reader.create_fast_reader()
gaze_ocr_controller = gaze_ocr.Controller(ocr_reader, tracker, save_data_directory=r"C:\Users\james\Documents\OCR\logs")
 
mod = Module()

@mod.action_class
class GazeOcrActions:
    def move_cursor_to_word(text: str):
        """Moves cursor to onscreen word."""
        gaze_ocr_controller.start_reading_nearby()
        if not gaze_ocr_controller.move_cursor_to_word(text):
            raise RuntimeError("Unable to find: " + text)

    def move_cursor_to_gaze_point(offset_right: int=0, offset_down: int=0):
        """Moves mouse cursor to gaze location."""
        tracker.move_to_gaze_point((offset_right, offset_down))
