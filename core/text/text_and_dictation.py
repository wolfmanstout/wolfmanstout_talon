# Descended from https://github.com/dwiel/talon_community/blob/master/misc/dictation.py
import json
import logging
import re
import time
import unicodedata
import urllib.error
import urllib.request
from typing import Callable, Optional

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
    "dictation_ai_cleanup",
    type=bool,
    default=False,
    desc="If true, send each dictation utterance to an LLM and rewrite only when corrections are found.",
)
mod.setting(
    "dictation_ai_cleanup_model",
    type=str,
    default="gemma4:e4b",
    desc="Ollama model used for dictation cleanup.",
)
mod.setting(
    "dictation_ai_cleanup_url",
    type=str,
    default="http://127.0.0.1:11434/api/generate",
    desc="Ollama generate API endpoint.",
)
mod.setting(
    "dictation_ai_cleanup_timeout_s",
    type=int,
    default=5,
    desc="Timeout for Ollama dictation cleanup requests, in seconds.",
)
setting_peek_right_after_insertion = mod.setting(
    "peek_right_after_insertion",
    type=bool,
    default=False,
    desc="If true, context sensitive dictation will only peek right after inserting text. Useful in applications for which the default behavior causes problems.",
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


@mod.capture(rule="({user.vocabulary} | <user.prose_contact> | <phrase>)+")
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
        "| <user.prose_contact>"
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
        if i > 0 and needs_space_between(words[i - 1], word):
            result += " "
        result += word
    return result


def capture_to_words(m):
    words = []
    for item in m:
        words.extend(
            actions.dictate.replace_words(actions.dictate.parse_words(item))
            if isinstance(item, grammar.vm.Phrase)
            else [item]
        )
    return words


def apply_formatting(m):
    formatter = DictationFormat()
    formatter.state = None
    result = ""
    for item in m:
        # prose modifiers (cap/no cap/no space) produce formatter callbacks.
        if isinstance(item, Callable):
            item(formatter)
        else:
            words = (
                actions.dictate.replace_words(actions.dictate.parse_words(item))
                if isinstance(item, grammar.vm.Phrase)
                else [item]
            )
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


def omit_space_before(text: str) -> bool:
    return not text or no_space_before.search(text)


def omit_space_after(text: str) -> bool:
    return not text or no_space_after.search(text)


def needs_space_between(before: str, after: str) -> bool:
    return not (omit_space_after(before) or omit_space_before(after))


# # TESTS, uncomment to enable
# assert needs_space_between("a", "break")
# assert needs_space_between("break", "a")
# assert needs_space_between(".", "a")
# assert needs_space_between("said", "'hello")
# assert needs_space_between("hello'", "said")
# assert needs_space_between("hello.", "'John")
# assert needs_space_between("John.'", "They")
# assert needs_space_between("paid", "$50")
# assert needs_space_between("50$", "payment")
# assert not needs_space_between("", "")
# assert not needs_space_between("a", "")
# assert not needs_space_between("a", " ")
# assert not needs_space_between("", "a")
# assert not needs_space_between(" ", "a")
# assert not needs_space_between("a", ",")
# assert not needs_space_between("'", "a")
# assert not needs_space_between("a", "'")
# assert not needs_space_between("and-", "or")
# assert not needs_space_between("mary", "-kate")
# assert not needs_space_between("$", "50")
# assert not needs_space_between("US", "$")
# assert not needs_space_between("(", ")")
# assert not needs_space_between("(", "e.g.")
# assert not needs_space_between("example", ")")
# assert not needs_space_between("example", '".')
# assert not needs_space_between("example", '."')
# assert not needs_space_between("hello'", ".")
# assert not needs_space_between("hello.", "'")

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
        if not self.force_no_space and needs_space_between(self.before, text):
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
    for i, c in enumerate(text):
        if c.isalpha():
            break
    if i >= 0 and i < len(text):
        text = text[:i] + formatter(text[i]) + text[i + 1 :]
    return text


def log_dictation_debug(level: int, message: str, *args) -> None:
    if settings.get("user.dictation_debug_mode"):
        logging.log(level, message, *args)


dictation_formatter = DictationFormat()
ui.register("app_deactivate", lambda app: dictation_formatter.reset())
ui.register("win_focus", lambda win: dictation_formatter.reset())

# TODO: Use a stack
phrase_timestamp = None
context_check_phrase_timestamp = None
utterance_chunks: list[tuple[str, str]] = []
utterance_prior_context = ""
utterance_had_dictation = False


def on_pre_phrase(d):
    global phrase_timestamp
    global utterance_chunks, utterance_prior_context, utterance_had_dictation
    phrase_timestamp = time.time()
    utterance_chunks = []
    utterance_prior_context = ""
    utterance_had_dictation = False


def on_post_phrase(d):
    global phrase_timestamp, utterance_chunks, utterance_prior_context
    global utterance_had_dictation
    chunks = utterance_chunks
    prior_context = utterance_prior_context
    had_dictation = utterance_had_dictation
    phrase_timestamp = None
    utterance_chunks = []
    utterance_prior_context = ""
    utterance_had_dictation = False
    if not had_dictation or not chunks or not settings.get("user.dictation_ai_cleanup"):
        return
    utterance_before_text = "".join(before for before, _ in chunks)
    utterance_after_text = "".join(after for _, after in reversed(chunks))
    model = settings.get("user.dictation_ai_cleanup_model")
    url = settings.get("user.dictation_ai_cleanup_url")
    timeout = settings.get("user.dictation_ai_cleanup_timeout_s")
    corrected_before = _run_ai_cleanup(
        prior_context, utterance_before_text, model, url, timeout
    )
    if not corrected_before:
        return
    _apply_ai_cleanup_rewrite(
        prior_context, chunks, corrected_before, utterance_after_text
    )


def _cleanup_prompt(prior_context: str, utterance_text: str) -> str:
    return (
        "Speech recognition sometimes writes a word instead of a comma.\n"
        "These words may be mistranscribed commas: "
        "'comment', 'come and', 'comma', 'come in', 'common'.\n"
        "Replace ALL of these words with ', ' ONLY when they appear as list "
        "separators between items (like 'A comment B comment C').\n"
        "Do NOT replace them when used with normal meaning "
        "(like 'please comment on' or 'come and see').\n"
        "Do NOT insert commas anywhere else. Do NOT change any other words.\n"
        "Replace ALL occurrences in a single pass, not just the first.\n"
        "If no replacement is needed, return exactly: NOCHANGE\n"
        "Otherwise return ONLY the corrected text.\n\n"
        "Examples:\n"
        "- 'apples comment oranges comment bananas' -> 'apples, oranges, bananas'\n"
        "- 'please comment on the issue' -> NOCHANGE\n"
        "- 'come and see this' -> NOCHANGE\n\n"
        f"PRIOR_CONTEXT:\n{prior_context}\n\n"
        f"UTTERANCE:\n{utterance_text}\n"
    )


def _extract_ollama_response(body: bytes) -> str:
    data = json.loads(body.decode("utf-8"))
    response = data.get("response", "")
    if not isinstance(response, str):
        return ""
    response = response.strip("\n")
    # The model sometimes echoes the text then appends NOCHANGE on a new line.
    if response.endswith("\nNOCHANGE"):
        return "NOCHANGE"
    return response


def _is_outer_guard(char: str) -> bool:
    return char.isspace() or unicodedata.category(char).startswith("P")


def _split_outer_guards(text: str) -> tuple[str, str, str]:
    left = 0
    right = len(text)
    while left < right and _is_outer_guard(text[left]):
        left += 1
    while right > left and _is_outer_guard(text[right - 1]):
        right -= 1
    return text[:left], text[left:right], text[right:]


def _run_ai_cleanup(
    prior_context: str,
    utterance_text: str,
    model: str,
    url: str,
    timeout_seconds: int,
) -> Optional[str]:
    leading_guard, utterance_core, trailing_guard = _split_outer_guards(utterance_text)
    if not utterance_core:
        return None
    try:
        payload = json.dumps(
            {
                "model": model,
                "prompt": _cleanup_prompt(prior_context, utterance_core),
                "stream": False,
                "think": False,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            corrected_raw = _extract_ollama_response(response.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        logging.debug("Dictation AI cleanup skipped: %s", error)
        return None
    _, corrected_core, _ = _split_outer_guards(corrected_raw)
    logging.debug(
        "Dictation AI cleanup model I/O(core): prior_context=%r input=%r output=%r",
        prior_context,
        utterance_core,
        corrected_core,
    )
    if corrected_core == "NOCHANGE":
        logging.debug("Dictation AI cleanup: model reported no change")
        return None
    if not corrected_core:
        logging.debug("Dictation AI cleanup: empty response, skipping rewrite")
        return None
    if corrected_core == utterance_core:
        logging.debug("Dictation AI cleanup: unchanged response, skipping rewrite")
        return None
    corrected = f"{leading_guard}{corrected_core}{trailing_guard}"
    return corrected


def _apply_ai_cleanup_rewrite(
    prior_context: str,
    chunks: list[tuple[str, str]],
    corrected_before: str,
    after_suffix: str,
):
    for _ in chunks:
        actions.user.clear_last_phrase()
    if after_suffix:
        actions.user.insert_between(corrected_before, after_suffix)
    else:
        actions.insert(corrected_before)
    actions.user.add_phrase_to_history(corrected_before, after_suffix)
    dictation_formatter.update_context(prior_context)
    dictation_formatter.pass_through(corrected_before)


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

    def dictation_insert_raw(text: str):
        """Inserts text as-is, without invoking the dictation formatter."""
        actions.user.dictation_insert(text, auto_cap=False)

    def dictation_insert(text: str, auto_cap: bool = True) -> str:
        """Inserts dictated text, formatted appropriately."""
        original_text = text
        needs_check_after = False
        add_space_after = False
        prior_context = dictation_formatter.before
        if settings.get("user.context_sensitive_dictation"):
            global context_check_phrase_timestamp, phrase_timestamp
            if context_check_phrase_timestamp != phrase_timestamp:
                # Peek left if we might need leading space or auto-capitalization;
                # peek right if we might need trailing space. NB. We peek right
                # BEFORE insertion to avoid breaking the undo-chain between the
                # inserted text and the trailing space.
                need_left = not omit_space_before(text) or (
                    auto_cap and text != auto_capitalize(text, "sentence start")[0]
                )
                if settings.get("user.peek_right_after_insertion"):
                    need_right = False
                    needs_check_after = not omit_space_after(text)
                else:
                    need_right = not omit_space_after(text)
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
                prior_context = dictation_formatter.before
                add_space_after = after is not None and needs_space_between(text, after)
                context_check_phrase_timestamp = phrase_timestamp
        text = dictation_formatter.format(text, auto_cap)
        # Straighten curly quotes that were introduced to obtain proper
        # spacing. The formatter context still has the original curly quotes
        # so that future dictation is properly formatted.
        text = text.replace("“", '"').replace("”", '"')
        actions.insert(text)
        if needs_check_after:
            # Determined experimentally in Gmail on Mac.
            time.sleep(0.2)
            _, after = actions.user.dictation_peek(False, True)
            add_space_after = after is not None and needs_space_between(
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
        if phrase_timestamp is not None:
            global utterance_prior_context, utterance_had_dictation
            if not utterance_had_dictation:
                utterance_prior_context = prior_context
            utterance_had_dictation = True
            utterance_chunks.append((text, " " if add_space_after else ""))

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
        # edit.copy() while nothing is selected. We use "." instead of " "
        # because Gmail Chat merges adjacent whitespace in the clipboard.
        actions.insert(".")
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
            # Needed to capture text in some apps (Antigravity).
            actions.sleep("10ms")
            selected_text = actions.edit.selected_text()
            log_dictation_debug(
                logging.INFO,
                "Context-sensitive dictation left selection: %r",
                selected_text,
            )
            if selected_text and selected_text[-1] == ".":
                before = selected_text[:-1]
            elif (
                selected_text and selected_text[-2:] == ".\n"
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
            actions.key("backspace")  # remove the marker
        else:
            actions.edit.left()  # go left before marker
            # We want to select at least two characters to the right, plus the marker
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
            selected_text = actions.edit.selected_text()
            log_dictation_debug(
                logging.INFO,
                "Context-sensitive dictation right selection: %r",
                selected_text,
            )
            if selected_text and selected_text[0] == ".":
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
            actions.key("delete")  # remove marker
        return before, after
