# Descended from https://github.com/dwiel/talon_community/blob/master/misc/dictation.py
import logging
import re
import time
from collections.abc import Callable
from typing import Optional

from talon import Context, Module, actions, grammar, settings, speech_system, ui

from ..numbers.numbers import get_spoken_form_under_one_hundred

mod = Module()

mod.setting(
    "context_sensitive_dictation",
    type=bool,
    default=False,
    desc="Look at surrounding text to improve auto-capitalization/spacing in dictation mode. By default, this works by selecting that text & copying it to the clipboard, so it may be slow or fail in some applications.",
)
mod.setting(
    "dictation_debug_mode",
    type=bool,
    default=False,
    desc="If true, log context-sensitive dictation diagnostics for timing-sensitive peek behavior.",
)
mod.setting(
    "normalize_dictation",
    type=bool,
    default=False,
    desc="If true, normalize model-added utterance capitalization and trailing punctuation before dictation formatting.",
)
setting_peek_right_after_insertion = mod.setting(
    "peek_right_after_insertion",
    type=bool,
    default=False,
    desc="If true, context sensitive dictation will only peek right after inserting text. Useful in applications for which the default behavior causes problems.",
)

mod.setting(
    "context_sensitive_dictation_peek_character",
    type=str,
    default=".",
    desc="This is the character inserted during dictation_peek to ensure that some text is selected even if the cursor is at the start or end of the document. This should be a single character only.",
)

mod.list("prose_modifiers", desc="Modifiers that can be used within prose")
mod.list("prose_snippets", desc="Snippets that can be used within prose")
mod.list("phrase_ender", "List of commands that can be used to end a phrase")
mod.list("prose_number_punctuation", desc="Punctuation that can be used in a number")
mod.list("prose_number_suffix", desc="Suffixes that can be used after a prose number")
mod.list("hours_twelve", desc="Names for hours up to 12")
mod.list("hours", desc="Names for hours up to 24")
mod.list("minutes", desc="Names for minutes, 01 up to 59")
mod.list(
    "currency",
    desc="Currency types (e.g., dollars, euros) that can be used within prose",
)

ctx = Context()
ctx.lists["user.prose_number_punctuation"] = {
    "dot": ".",
    "point": ".",
    "colon": ":",
    "slash": "/",
    "percent": "%",
}
ctx.lists["user.prose_number_suffix"] = {
    "k": "K",
    "m": "M",
    "b": "B",
}

ctx.lists["user.hours_twelve"] = get_spoken_form_under_one_hundred(
    1,
    12,
    include_oh_variant_for_single_digits=True,
    include_default_variant_for_single_digits=True,
)
ctx.lists["user.hours"] = get_spoken_form_under_one_hundred(
    1,
    23,
    include_oh_variant_for_single_digits=True,
    include_default_variant_for_single_digits=True,
)
ctx.lists["user.minutes"] = get_spoken_form_under_one_hundred(
    1,
    59,
    include_oh_variant_for_single_digits=True,
    include_default_variant_for_single_digits=False,
)


@mod.capture(rule="{user.prose_modifiers}")
def prose_modifier(m) -> Callable:
    return getattr(DictationFormat, m.prose_modifiers)


@mod.capture(rule="letter <user.letter>")
def prose_letter(m) -> str:
    return m.letter.capitalize()


@mod.capture(rule="<user.number_string> (dot | point) <digit_string>")
def prose_number_with_dot(m) -> str:
    return m.number_string + "." + m.digit_string


@mod.capture(rule="am|pm")
def time_am_pm(m) -> str:
    return str(m)


# this matches eg "twelve thirty-four" -> 12:34 and "twelve hundred" -> 12:00. hmmmmm.
@mod.capture(
    rule="{user.hours} ({user.minutes} | o'clock | hundred hours) [<user.time_am_pm>]"
)
def prose_time_hours_minutes(m) -> str:
    t = m.hours + ":"
    if hasattr(m, "minutes"):
        t += m.minutes
    else:
        t += "00"
    if hasattr(m, "time_am_pm"):
        t += m.time_am_pm
    return t


@mod.capture(rule="{user.hours_twelve} <user.time_am_pm>")
def prose_time_hours_am_pm(m) -> str:
    return m.hours_twelve + m.time_am_pm


@mod.capture(
    rule=(
        "(numeral | numb) (<user.number_string> | <user.prose_number_with_dot>)"
        " [{user.prose_number_punctuation} | (<user.number_string> | <user.prose_number_with_dot>)]*"
        " [{user.prose_number_suffix}]"
    )
)
def prose_number(m) -> str:
    return "".join(m[1:])


@mod.capture(rule=("<user.prose_number> dollars"))
def prose_money(m) -> str:
    return f"${m.prose_number}"


@mod.capture(rule="<user.prose_time_hours_minutes> | <user.prose_time_hours_am_pm>")
def prose_time(m) -> str:
    return str(m)


@mod.capture(rule="spell <user.letters>")
def prose_spell(m) -> str:
    """Spell word phonetically"""
    return m.letters


@mod.capture(rule="ship <user.letters>")
def prose_ship(m) -> str:
    """Spell word phonetically using uppercase letters"""
    return m.letters.upper()


@mod.capture(rule="clip clip")
def prose_clipboard(m) -> str:
    """Clipboard content"""
    return actions.clip.text()


@mod.capture(
    rule="({user.vocabulary} | <user.abbreviation> | <user.prose_contact> | <word>)"
)
def word(m) -> str:
    """A single word, including user-defined vocabulary."""
    item = m[0]
    if isinstance(item, grammar.vm.Phrase):
        return " ".join(
            actions.dictate.replace_words(actions.dictate.parse_words(item))
        )
    else:
        return item


@mod.capture(
    rule="({user.vocabulary} | <user.prose_contact> | <user.prose_spell> | <user.prose_clipboard> | <phrase>)+"
)
def text(m) -> str:
    """A sequence of words, including user-defined vocabulary."""
    return format_phrase(m)


@mod.capture(
    rule=(
        "("
        "{user.vocabulary} "
        "| {user.punctuation} "
        "| {user.prose_snippets} "
        "| <user.prose_time> "
        "| <user.abbreviation> "
        "| <phrase> "
        "| <user.prose_number> "
        "| <user.prose_money> "
        "| <user.prose_letter> "
        "| <user.prose_contact> "
        "| <user.prose_spell> "
        "| <user.prose_ship> "
        "| <user.prose_clipboard> "
        "| <user.prose_modifier>"
        ")+"
    )
)
def prose(m) -> str:
    """Mixed words and punctuation, auto-spaced & capitalized."""
    # Straighten curly quotes that were introduced to obtain proper spacing.
    return apply_formatting(m).replace("“", '"').replace("”", '"')


@mod.capture(
    rule=(
        "("
        "{user.vocabulary} "
        "| {user.punctuation} "
        "| {user.prose_snippets} "
        "| <user.prose_time> "
        "| <user.abbreviation> "
        "| <phrase> "
        "| <user.prose_number> "
        "| <user.prose_money> "
        "| <user.prose_letter> "
        "| <user.prose_contact> "
        "| <user.prose_spell> "
        "| <user.prose_ship> "
        "| <user.prose_clipboard>"
        ")+"
    )
)
def raw_prose(m) -> str:
    """Mixed words and punctuation, auto-spaced & capitalized, without quote straightening and commands (for use in dictation mode)."""
    return apply_formatting(m)


# ---------- FORMATTING ---------- #
def format_phrase(m):
    words = capture_to_words(m)
    result = ""
    for i, word in enumerate(words):
        if i > 0 and actions.user.needs_space_between(words[i - 1], word):
            result += " "
        result += word
    return result


def capture_to_words(m):
    words = []
    for item in m:
        words.extend(_dictation_item_to_words(item))
    return words


def _dictation_item_to_words(item):
    if not isinstance(item, grammar.vm.Phrase):
        return [item]

    words = actions.dictate.parse_words(item)
    if settings.get("user.normalize_dictation"):
        words = normalize_dictation_words(words)
    return actions.dictate.replace_words(words)


def normalize_dictation_words(words):
    if not words:
        return words

    words = list(words)
    # Some models add sentence-ending punctuation for an utterance fragment.
    words[-1] = re.sub(r"[^\w\s]+$", "", words[-1])
    words = [word for word in words if word]
    if not words:
        return words

    words[0] = normalize_dictation_start_word(words[0])
    return words


def normalize_dictation_start_word(word):
    first_letter = re.search(r"[A-Za-z]", word)
    if not first_letter:
        return word

    i = first_letter.start()
    word_from_first_letter = word[i:]
    # Let DictationFormat decide if the utterance starts a sentence, while
    # preserving I and words with internal capitalization.
    is_first_person = re.match(
        r"^I(?:['’][A-Za-z]+)?(?:[^\w\s]+)?$", word_from_first_letter
    )
    has_internal_capitalization = any(
        char.isupper() for char in word_from_first_letter[1:]
    )
    if is_first_person or has_internal_capitalization:
        return word

    return word[:i] + word[i].lower() + word[i + 1 :]


def apply_formatting(m):
    formatter = DictationFormat()
    formatter.state = None
    result = ""
    for item in m:
        # prose modifiers (cap/no cap/no space) produce formatter callbacks.
        if isinstance(item, Callable):
            item(formatter)
        else:
            words = _dictation_item_to_words(item)
            for word in words:
                result += formatter.format(word)
    return result


# There must be a simpler way to do this, but I don't see it right now.
no_space_after = re.compile(
    r"""
  (?:
    [\s\-_/#@+([{‘“]     # characters that never need space after them
  | (?<!\w)[$£€¥₩₽₹]    # currency symbols not preceded by a word character
  # quotes preceded by beginning of string, space, opening braces, dash, or other quotes
  | (?: ^ | [\s([{\-'"] ) ['"]
  )$""",
    re.VERBOSE,
)
no_space_before = re.compile(
    r"""
  ^(?:
    [\s\-_.,!?/%)\]}’”]   # characters that never need space before them
  | [;:](?!-\)|-\()        # colon or semicolon except for smiley faces
  # quotes followed by end of string, space, closing braces, dash, other quotes, or some punctuation.
  | ['"] (?: $ | [\s)\]}\-'".,!?;:/] )
  # apostrophe s
  | 's(?!\w)
  )""",
    re.VERBOSE,
)


# # TESTS, uncomment to enable
# assert actions.user.needs_space_between("a", "break")
# assert actions.user.needs_space_between("break", "a")
# assert actions.user.needs_space_between(".", "a")
# assert actions.user.needs_space_between("said", "'hello")
# assert actions.user.needs_space_between("hello'", "said")
# assert actions.user.needs_space_between("hello.", "'John")
# assert actions.user.needs_space_between("John.'", "They")
# assert actions.user.needs_space_between("paid", "$50")
# assert actions.user.needs_space_between("50$", "payment")
# assert not actions.user.needs_space_between("", "")
# assert not actions.user.needs_space_between("a", "")
# assert not actions.user.needs_space_between("a", " ")
# assert not actions.user.needs_space_between("", "a")
# assert not actions.user.needs_space_between(" ", "a")
# assert not actions.user.needs_space_between("a", ",")
# assert not actions.user.needs_space_between("'", "a")
# assert not actions.user.needs_space_between("a", "'")
# assert not actions.user.needs_space_between("and-", "or")
# assert not actions.user.needs_space_between("mary", "-kate")
# assert not actions.user.needs_space_between("$", "50")
# assert not actions.user.needs_space_between("US", "$")
# assert not actions.user.needs_space_between("(", ")")
# assert not actions.user.needs_space_between("(", "e.g.")
# assert not actions.user.needs_space_between("example", ")")
# assert not actions.user.needs_space_between("example", '".')
# assert not actions.user.needs_space_between("example", '."')
# assert not actions.user.needs_space_between("hello'", ".")
# assert not actions.user.needs_space_between("hello.", "'")

no_cap_after = re.compile(
    r"""(
    e\.g\.
    | i\.e\.
    | vs\.
    )$""",
    re.VERBOSE,
)

sentence_end_trailers = "\"'”’)]}"


def auto_capitalize(text, state=None):
    """
    Auto-capitalizes text. Text must contain complete words, abbreviations, and
    formatted expressions. `state` argument means:

    - None: Don't capitalize initial word.
    - "sentence start": Capitalize initial word.

    Returns (capitalized text, updated state).
    """
    output = ""
    # Imagine a metaphorical "capitalization charge" travelling through the
    # string left-to-right.
    charge = state == "sentence start"
    sentence_end = False
    for c in text:
        # Sentence endings followed by space create a charge.
        if sentence_end and c.isspace():
            charge = True
        # Alphanumeric characters and commas/colons absorb charge & try to
        # capitalize (for numbers & punctuation this does nothing, which is what
        # we want).
        elif charge and (c.isalnum() or c in ",:@+"):
            charge = False
            c = c.capitalize()
        # Otherwise the charge just passes through.
        output += c
        sentence_end_now = (
            c in ".!?\n" or output.endswith("TODO")
        ) and not no_cap_after.search(output)
        sentence_end = sentence_end_now or (sentence_end and c in sentence_end_trailers)
        # A newline is both a sentence ending and whitespace, so create
        # the charge immediately.
        if c == "\n" and sentence_end:
            charge = True
    return output, ("sentence start" if charge or sentence_end else None)


# ---------- DICTATION AUTO FORMATTING ---------- #
class DictationFormat:
    def __init__(self):
        self.reset()

    def reset(self):
        self.reset_context()
        self.force_no_space = False
        self.force_capitalization = None  # Can also be "cap" or "no cap".

    def reset_context(self):
        self.before = ""
        self.state = "sentence start"

    def update_context(self, before):
        if before is None:
            return
        self.reset_context()
        self.pass_through(before)

    def pass_through(self, text):
        _, self.state = auto_capitalize(text, self.state)
        self.before = text or self.before

    def format(self, text, auto_cap=True):
        if not self.force_no_space and actions.user.needs_space_between(
            self.before, text
        ):
            text = " " + text
        self.force_no_space = False
        if auto_cap:
            text, self.state = auto_capitalize(text, self.state)
        if self.force_capitalization == "cap":
            text = format_first_letter(text, lambda s: s.capitalize())
            self.force_capitalization = None
        if self.force_capitalization == "no cap":
            text = format_first_letter(text, lambda s: s.lower())
            self.force_capitalization = None
        self.before = text or self.before
        return text

    # These are used as callbacks by prose modifiers / dictation_mode commands.
    def cap(self):
        self.force_capitalization = "cap"

    def no_cap(self):
        self.force_capitalization = "no cap"

    def no_space(self):
        self.force_no_space = True


def format_first_letter(text, formatter):
    i = -1
    for i, c in enumerate(text):  # noqa: B007
        if c.isalpha():
            break
    if i >= 0 and i < len(text):
        text = text[:i] + formatter(text[i]) + text[i + 1 :]
    return text


def log_dictation_debug(level: int, message: str, *args) -> None:
    if settings.get("user.dictation_debug_mode"):
        active_app = ui.active_app()
        app_name = active_app.name if active_app else "unknown"
        logging.log(level, "[%s] " + message, app_name, *args)


dictation_formatter = DictationFormat()
ui.register("app_deactivate", lambda app: dictation_formatter.reset())
ui.register("win_focus", lambda win: dictation_formatter.reset())

# TODO: Use a stack
phrase_timestamp = None
context_check_phrase_timestamp = None


def on_pre_phrase(d):
    global phrase_timestamp
    phrase_timestamp = time.time()


def on_post_phrase(d):
    global phrase_timestamp
    phrase_timestamp = None


speech_system.register("pre:phrase", on_pre_phrase)
speech_system.register("post:phrase", on_post_phrase)


def reformat_last_utterance(formatter):
    text = actions.user.get_last_phrase()
    actions.user.clear_last_phrase()
    text = formatter(text)
    actions.user.add_phrase_to_history(text)
    actions.insert(text)


@mod.action_class
class Actions:
    def dictation_format_reset():
        """Resets the dictation formatter"""
        return dictation_formatter.reset()

    def dictation_format_cap():
        """Sets the dictation formatter to capitalize"""
        dictation_formatter.cap()

    def dictation_format_no_cap():
        """Sets the dictation formatter to not capitalize"""
        dictation_formatter.no_cap()

    def dictation_format_no_space():
        """Sets the dictation formatter to not prepend a space"""
        dictation_formatter.no_space()

    def dictation_reformat_cap():
        """Capitalizes the last utterance"""
        reformat_last_utterance(
            lambda s: format_first_letter(s, lambda c: c.capitalize())
        )

    def dictation_reformat_no_cap():
        """Lowercases the last utterance"""
        reformat_last_utterance(lambda s: format_first_letter(s, lambda c: c.lower()))

    def dictation_reformat_no_space():
        """Removes space before the last utterance"""
        reformat_last_utterance(lambda s: s[1:] if s.startswith(" ") else s)

    def omit_space_before(text: str) -> bool:
        """Test if dictated text needs space before"""
        return bool(not text or no_space_before.search(text))

    def omit_space_after(text: str) -> bool:
        """Test if dictated text needs space after"""
        return bool(not text or no_space_after.search(text))

    def needs_space_between(before: str, after: str) -> bool:
        """Test if two text strings need a space between them"""
        return not (
            actions.user.omit_space_after(before)
            or actions.user.omit_space_before(after)
        )

    def dictation_replace(text: str) -> str:
        """Substitutions to be performed before inserting text using dictation_insert"""
        return text.replace("“", '"').replace("”", '"')

    def dictation_insert_raw(text: str):
        """Inserts text as-is, without invoking the dictation formatter."""
        actions.user.dictation_insert(text, auto_cap=False)

    def dictation_insert_rich_text(text: str, formats: list[str]):
        """Inserts dictated text, then applies rich text formats to it."""
        actions.user.dictation_insert(text)
        actions.user.select_last_phrase()
        text_toggles = []
        for format in formats:
            if format == "bold":
                actions.user.bold()
                text_toggles.append(format)
            elif format == "italic":
                actions.user.italic()
                text_toggles.append(format)
            elif format == "link":
                actions.user.link_selection_from_clipboard()
            else:
                logging.warning("Unknown rich text format: %s", format)
        actions.edit.right()
        for format in reversed(text_toggles):
            if format == "bold":
                actions.user.bold()
            elif format == "italic":
                actions.user.italic()

    def dictation_insert(text: str, auto_cap: bool = True):
        """Inserts dictated text, formatted appropriately."""
        original_text = text
        needs_check_after = False
        add_space_after = False
        if settings.get("user.context_sensitive_dictation"):
            global context_check_phrase_timestamp, phrase_timestamp
            if context_check_phrase_timestamp != phrase_timestamp:
                # Peek left if we might need leading space or auto-capitalization;
                # peek right if we might need trailing space. NB. We peek right
                # BEFORE insertion to avoid breaking the undo-chain between the
                # inserted text and the trailing space.
                need_left = not actions.user.omit_space_before(text) or (
                    auto_cap and text != auto_capitalize(text, "sentence start")[0]
                )
                if settings.get("user.peek_right_after_insertion"):
                    need_right = False
                    needs_check_after = not actions.user.omit_space_after(text)
                else:
                    need_right = not actions.user.omit_space_after(text)
                before, after = actions.user.dictation_peek(need_left, need_right)
                log_dictation_debug(
                    logging.INFO,
                    "Context-sensitive dictation peek before insertion: left=%s right=%s before=%r after=%r",
                    need_left,
                    need_right,
                    before,
                    after,
                )
                dictation_formatter.update_context(before)
                add_space_after = (
                    after is not None and actions.user.needs_space_between(text, after)
                )
                context_check_phrase_timestamp = phrase_timestamp
        text = dictation_formatter.format(text, auto_cap)
        # Straighten curly quotes that were introduced to obtain proper
        # spacing. The formatter context still has the original curly quotes
        # so that future dictation is properly formatted.
        text = actions.user.dictation_replace(text)
        actions.insert(text)
        if needs_check_after:
            # Determined experimentally in Gmail on Mac.
            time.sleep(0.2)
            _, after = actions.user.dictation_peek(False, True)
            add_space_after = after is not None and actions.user.needs_space_between(
                original_text, after
            )
            log_dictation_debug(
                logging.INFO,
                "Context-sensitive dictation peek after insertion: after=%r add_space_after=%s",
                after,
                add_space_after,
            )
        if add_space_after:
            actions.user.insert_between("", " ")
        actions.user.add_phrase_to_history(text, " " if add_space_after else "")

    def dictation_peek(left: bool, right: bool) -> tuple[Optional[str], Optional[str]]:
        """
        Gets text around the cursor to inform auto-spacing and -capitalization.
        Returns (before, after), where `before` is some text before the cursor,
        and `after` some text after it. Results are not guaranteed; `before`
        and/or `after` may be None, indicating no information. If `before` is
        the empty string, this means there is nothing before the cursor (we are
        at the beginning of the document); likewise for `after`.

        To optimize performance, pass `left = False` if you won't need
        `before`, and `right = False` if you won't need `after`.

        dictation_peek() is intended for use before inserting text, so it may
        delete any currently selected text.
        """
        if not (left or right):
            return None, None
        before, after = None, None
        # Inserting a character ensures we select something even if we're at
        # document start; some editors 'helpfully' copy the current line if we
        # edit.copy() while nothing is selected. The default marker is "."
        # because Gmail Chat merges adjacent whitespace in the clipboard.
        peek_character = settings.get("user.context_sensitive_dictation_peek_character")
        actions.insert(peek_character)
        if left:
            # In principle the previous word should suffice, but some applications
            # have a funny concept of what the previous word is (for example, they
            # may only take the "`" at the end of "`foo`"). To be double sure we
            # take three words left. I also tried taking a line up + a word left, but
            # edit.extend_up() = key(shift-up) doesn't work consistently in the
            # Slack webapp (sometimes escapes the text box).
            actions.edit.extend_word_left()
            actions.edit.extend_word_left()
            actions.edit.extend_word_left()
            # Needed to capture text in some apps (Antigravity and Google Chat).
            actions.sleep("20ms")
            selected_text = actions.edit.selected_text()
            log_dictation_debug(
                logging.INFO,
                "Context-sensitive dictation left selection: %r",
                selected_text,
            )
            if selected_text and selected_text[-1] == peek_character:
                before = selected_text[:-1]
            elif (
                selected_text and selected_text[-2:] == f"{peek_character}\n"
            ):  # Observed in Google Docs after a bullet.
                before = selected_text[:-2]
            else:
                log_dictation_debug(
                    logging.WARNING,
                    "Context-sensitive dictation left selection did not include marker: %r",
                    selected_text,
                )
                before = selected_text
            # Unfortunately, in web Slack, if our selection ends at newline,
            # this will go right over the newline. Argh.
            actions.edit.right()
        if not right:
            # Needed to avoid clobbering text in some apps (e.g. Codex).
            actions.sleep("50ms")
            actions.key("backspace")  # remove the peek character
        else:
            actions.edit.left()  # go left before the peek character
            # We want to select at least two characters to the right, plus the character
            # we inserted, because no_space_before needs two characters in the worst
            # case -- for example, inserting before "' hello" we don't want to add
            # space, while inserted before "'hello" we do.
            #
            # We use 3x extend_word_right() because it's fewer keypresses (lower
            # latency) than 3x extend_right(). Other options all seem to have
            # problems. For instance, extend_line_end() might not select all the way
            # to the next newline if text has been wrapped across multiple lines;
            # extend_line_down() sometimes escapes the current text box (eg. in a
            # browser address bar). 1x extend_word_right() _usually_ works, but on
            # Windows in Firefox it doesn't always select enough characters.
            actions.edit.extend_word_right()
            actions.edit.extend_word_right()
            actions.edit.extend_word_right()
            # Needed to capture text in some apps (Antigravity and Google Chat).
            actions.sleep("20ms")
            selected_text = actions.edit.selected_text()
            log_dictation_debug(
                logging.INFO,
                "Context-sensitive dictation right selection: %r",
                selected_text,
            )
            if selected_text and selected_text[0] == peek_character:
                after = selected_text[1:]
            else:
                log_dictation_debug(
                    logging.WARNING,
                    "Context-sensitive dictation right selection did not include marker: %r",
                    selected_text,
                )
                after = selected_text
            actions.edit.left()
            # Needed to avoid clobbering text in some apps (e.g. Gemini).
            actions.sleep("50ms")
            actions.key("delete")  # remove the peek character
        return before, after
