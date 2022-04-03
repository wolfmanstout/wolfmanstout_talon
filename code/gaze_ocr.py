from dataclasses import dataclass
from typing import Dict, Iterable, Sequence, Union

from talon import Context, Module, actions, app
from talon.grammar import Phrase

import gaze_ocr
import screen_ocr  # dependency of gaze-ocr
from gaze_ocr import _talon_wrappers as talon_wrappers

from .keys import punctuation_words
from .numbers import digits_map

mod = Module()
ctx = Context()

setting_ocr_logging_dir = mod.setting(
    "ocr_logging_dir",
    type=str,
    default=None,
    desc="If specified, log OCR'ed images to this directory.",
)
setting_ocr_click_offset_right = mod.setting(
    "ocr_click_offset_right",
    type=int,
    default=1,  # Windows biases towards the left of whatever is clicked.
    desc="Adjust the X-coordinate when clicking around OCR text.",
)


def add_homophones(homophones: Dict[str, Sequence[str]],
                   to_add: Iterable[Iterable[str]]):
    for words in to_add:
        merged_words = set(words)
        for word in words:
            old_words = homophones.get(word.lower(), [])
            merged_words.update(old_words)
        merged_words = sorted(merged_words)
        for word in merged_words:
            homophones[word.lower()] = merged_words


def on_ready():
    # Initialize eye tracking and OCR. See installation instructions:
    # https://github.com/wolfmanstout/gaze-ocr
    global tracker, ocr_reader, gaze_ocr_controller
    tracker = gaze_ocr.eye_tracking.TalonEyeTracker()
    homophones = actions.user.homophones_get_all()
    add_homophones(homophones,
                   [(str(num), spoken) for spoken, num in digits_map.items()])
    add_homophones(homophones,
                   [(punctuation, spoken) 
                    for spoken, punctuation in punctuation_words.items()
                    if " " not in spoken])
    add_homophones(homophones, [
        # 0k is not actually a homophone but is frequently produced by OCR.
        ("ok", "okay", "0k"),
    ])
    ocr_reader = screen_ocr.Reader.create_fast_reader(
        radius=200, homophones=homophones)
    gaze_ocr_controller = gaze_ocr.Controller(
        ocr_reader,
        tracker,
        save_data_directory=setting_ocr_logging_dir.get(),
        mouse=talon_wrappers.Mouse(),
        keyboard=talon_wrappers.Keyboard())

app.register("ready", on_ready)

@dataclass
class TimestampedText:
    text: str
    start: float
    end: float

# "edit" is frequently misrecognized as "at it", and is common in UIs.
@mod.capture(rule="(<phrase> | {user.vocabulary} | {user.punctuation} | {user.prose_snippets})+ | edit")
def timestamped_prose(m) -> TimestampedText:
    """Dictated text appearing onscreen."""
    words = []
    start = None
    end = None
    for item in m:
        if isinstance(item, Phrase):
            words.extend(actions.dictate.replace_words(actions.dictate.parse_words(item)))
            if not start:
                start = item.words[0].start
            end = item.words[-1].end
        else:
            words.append(str(item))
            if not start:
                start = item.start
            end = item.end
    assert start
    assert end
    return TimestampedText(text=" ".join(words), start=start, end=end)

@mod.capture(rule="{self.homophones_canonicals}")
def timestamped_homophone(m) -> TimestampedText:
    """Timestamped homophone."""
    return TimestampedText(text=" ".join(m), start=m[0].start, end=m[-1].end)

mod.list("ocr_actions", desc="Actions to perform on selected text.")
mod.list("ocr_modifiers", desc="Modifiers to perform on selected text.")
ctx.lists["self.ocr_actions"] = {
    "take": "select",
    "copy": "copy",
    "carve": "cut",
    "paste to": "paste",
    "clear": "delete",
    "cap": "capitalize",
}
ctx.lists["self.ocr_modifiers"] = {
    "all": "selectAll",
}

@mod.action_class
class GazeOcrActions:
    def move_cursor_to_word(text: TimestampedText):
        """Moves cursor to onscreen word."""
        if not gaze_ocr_controller.move_cursor_to_words(
            text.text, timestamp=text.start, 
            click_offset_right=setting_ocr_click_offset_right.get()):
            raise RuntimeError("Unable to find: \"{}\"".format(text))

    def move_text_cursor_to_word(text: TimestampedText, position: str):
        """Moves text cursor near onscreen word."""
        if not gaze_ocr_controller.move_text_cursor_to_words(
            text.text, position, timestamp=text.start, 
            click_offset_right=setting_ocr_click_offset_right.get()):
            raise RuntimeError("Unable to find: \"{}\"".format(text))

    def move_text_cursor_to_word_ignore_errors(text: TimestampedText, position: str):
        """Moves text cursor near onscreen word, ignoring errors (log only)."""
        if not gaze_ocr_controller.move_text_cursor_to_words(
                text.text, position, timestamp=text.start, 
                click_offset_right=setting_ocr_click_offset_right.get()):
            print("Unable to find: \"{}\"".format(text))

    def select_text(start: TimestampedText, end: Union[TimestampedText, str]="",
                    for_deletion: bool=False):
        """Selects text near onscreen word at phrase timestamps."""
        start_text = start.text
        end_text = end.text if end else None
        if not gaze_ocr_controller.select_text(
                start_text, end_text, for_deletion,
                start.start,
                end.start if end else start.end,
                click_offset_right=setting_ocr_click_offset_right.get()):
            raise RuntimeError("Unable to select \"{}\" to \"{}\"".format(start, end))

    def move_cursor_to_gaze_point(offset_right: int=0, offset_down: int=0):
        """Moves mouse cursor to gaze location."""
        tracker.move_to_gaze_point((offset_right, offset_down))

    def perform_ocr_action(ocr_action: str,
                           ocr_modifier: str,
                           start: TimestampedText,
                           end: Union[TimestampedText, str] = ""):
        """Selects text and performs an action."""
        for_deletion = ocr_action in ("cut", "delete")
        actions.user.select_text(start, end, for_deletion)
        if ocr_modifier == "":
            pass
        elif ocr_modifier == "selectAll":
            actions.edit.select_all()
        else:
            raise RuntimeError(f"Modifier not supported: {ocr_modifier}")
        
        if ocr_action == "select":
            pass
        elif ocr_action == "copy":
            actions.edit.copy()
        elif ocr_action == "cut":
            actions.edit.cut()
        elif ocr_action == "paste":
            actions.edit.paste()
        elif ocr_action == "delete":
            actions.key("backspace")
        elif ocr_action == "capitalize":
            text = actions.edit.selected_text()
            actions.insert(text[0].capitalize() + text[1:] if text else "")
        else:
            raise RuntimeError(f"Action not supported: {ocr_action}")
