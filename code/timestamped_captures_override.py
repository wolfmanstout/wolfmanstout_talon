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
    if isinstance(item, TimestampedText):
        return item
    else:
        return TimestampedText(text=str(item), start=item.start, end=item.end)
