from talon import Context

from ...talon_gaze_ocr.timestamped_captures import TimestampedText

ctx = Context()


@ctx.capture(rule="<user.timestamped_phrase_default> | <user.prose_contact>")
def timestamped_phrase(m) -> TimestampedText:
    item = m[0]
    if isinstance(item, TimestampedText):
        return item
    else:
        return TimestampedText(text=str(item), start=item.start, end=item.end)
