import importlib

from talon import Context

timestamped_captures = importlib.import_module(
    "user.talon-gaze-ocr.timestamped_captures"
)
TimestampedText = timestamped_captures.TimestampedText


ctx = Context()


@ctx.capture(rule="<user.timestamped_phrase_default> | <user.prose_contact>")
def timestamped_phrase(m) -> TimestampedText:
    item = m[0]
    # HACK: check the name because the class object might be different due to a separate import.
    if type(item).__name__ == "TimestampedText":
        return item
    else:
        return TimestampedText(text=str(item), start=item.start, end=item.end)
