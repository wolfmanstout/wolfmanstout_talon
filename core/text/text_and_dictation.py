# Descended from https://github.com/dwiel/talon_community/blob/master/misc/dictation.py
import json
import logging
import re
import time
import unicodedata
import urllib.error
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Literal, Optional, TypeGuard

import requests
from talon import Context, Module, actions, grammar, settings, speech_system, ui

from ..numbers.numbers import get_spoken_form_under_one_hundred

mod = Module()

DictationAiCleanupBackend = Literal["ollama", "mlx"]
DictationAiCleanupOutcome = Literal[
    "corrected", "nochange", "identical", "unsafe", "empty", "error"
]


@dataclass
class DictationAiCleanupPerf:
    backend: DictationAiCleanupBackend
    wall_ms: float
    server_call_ms: Optional[float] = None
    client_prep_ms: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    prefill_ms: Optional[float] = None
    decode_ms: Optional[float] = None
    total_ms: Optional[float] = None
    load_ms: Optional[float] = None
    cached_prompt_tokens: Optional[int] = None
    prefill_tps: Optional[float] = None
    decode_tps: Optional[float] = None
    peak_memory_gb: Optional[float] = None

    @staticmethod
    def _tokens_per_second(
        token_count: Optional[int], duration_ms: Optional[float]
    ) -> Optional[float]:
        if token_count is None or duration_ms is None or duration_ms <= 0:
            return None
        return token_count / (duration_ms / 1000.0)

    def prefill_tokens_per_second(self) -> Optional[float]:
        return self.prefill_tps or self._tokens_per_second(
            self.prompt_tokens, self.prefill_ms
        )

    def decode_tokens_per_second(self) -> Optional[float]:
        return self.decode_tps or self._tokens_per_second(
            self.completion_tokens, self.decode_ms
        )


@dataclass
class DictationAiCleanupResult:
    corrected_text: Optional[str]
    model_output: Optional[str]
    outcome: DictationAiCleanupOutcome


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
mod.setting(
    "dictation_ai_cleanup",
    type=bool,
    default=False,
    desc="If true, send each dictation utterance to an LLM and rewrite only when corrections are found.",
)
mod.setting(
    "dictation_ai_cleanup_model",
    type=str,
    default="mlx-community/gemma-4-26b-a4b-it-qat-4bit",
    desc="Model used for dictation cleanup.",
)
mod.setting(
    "dictation_ai_cleanup_backend",
    type=str,
    default="mlx",
    desc="LLM backend used for dictation cleanup. Supported values: 'ollama' and 'mlx'.",
)
mod.setting(
    "dictation_ai_cleanup_port",
    type=int,
    default=0,
    desc="Port for dictation cleanup backends. Set to 0 to use the backend default (11434 for Ollama, 8080 for mlx).",
)
mod.setting(
    "dictation_ai_cleanup_timeout_s",
    type=int,
    default=30,
    desc="Timeout for dictation cleanup requests, in seconds.",
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
utterance_insertions: list[tuple[str, str]] = []
utterance_preceding_text = ""
utterance_had_dictation = False


def on_pre_phrase(d):
    global phrase_timestamp
    global utterance_insertions, utterance_preceding_text, utterance_had_dictation
    phrase_timestamp = time.time()
    utterance_insertions = []
    utterance_preceding_text = ""
    utterance_had_dictation = False


def on_post_phrase(d):
    global phrase_timestamp, utterance_insertions, utterance_preceding_text
    global utterance_had_dictation
    insertions = utterance_insertions
    preceding_text = utterance_preceding_text
    had_dictation = utterance_had_dictation
    phrase_timestamp = None
    utterance_insertions = []
    utterance_preceding_text = ""
    utterance_had_dictation = False
    if (
        not had_dictation
        or not insertions
        or not settings.get("user.dictation_ai_cleanup")
    ):
        return
    utterance_text = "".join(inserted_text for inserted_text, _ in insertions)
    utterance_suffix = "".join(suffix for _, suffix in reversed(insertions))
    backend = settings.get("user.dictation_ai_cleanup_backend")
    if not _is_dictation_ai_cleanup_backend(backend):
        logging.debug("Dictation AI cleanup skipped: unsupported backend %r", backend)
        return
    model = settings.get("user.dictation_ai_cleanup_model")
    port = settings.get("user.dictation_ai_cleanup_port")
    if backend == "ollama":
        resolved_port = port if port > 0 else 11434
        url = f"http://127.0.0.1:{resolved_port}/api/generate"
    else:
        resolved_port = port if port > 0 else 8080
        url = f"http://127.0.0.1:{resolved_port}/chat/completions"
    timeout = settings.get("user.dictation_ai_cleanup_timeout_s")
    actions.user.dictation_mode_set_processing(True)
    try:
        corrected_utterance_text = _run_ai_cleanup(
            preceding_text, utterance_text, model, url, timeout, backend
        )
        if corrected_utterance_text:
            _apply_ai_cleanup_rewrite(
                preceding_text,
                insertions,
                corrected_utterance_text,
                utterance_suffix,
            )
    finally:
        actions.user.dictation_mode_set_processing(False)


def _cleanup_prompt(preceding_text: str, utterance_text: str) -> str:
    return (
        "Edit only <utterance>. <text_before> is read-only text immediately before it; their "
        "contents are adjacent on screen. Ignore its errors and never repeat, fix, or output it. "
        "Either may be incomplete.\n"
        "When certain, (1) replace a spoken or phonetically misrecognized complete name of comma, "
        "colon, semicolon, exclamation mark, question mark, or hyphen with the mark, consuming the "
        "whole name; never replace only part of a multiword name; (2) insert unspoken hyphens only "
        "in a compound modifier directly before its noun "
        "where standard spelling clearly requires them; or (3) correct a homophone only when it "
        "is clearly wrong in context, or correct a "
        "clearly invalid word boundary, or restore one clearly omitted word. Outside those "
        "replacements, never add, "
        "delete, reorder, or "
        "alter words; treat capitalized words after the first word as immutable proper nouns, "
        "even if unfamiliar or apparently misspelled, unless consumed in a punctuation name; do "
        "not proofread. You may capitalize a lowercase name when certain, but never lowercase a "
        "word. Never insert unspoken "
        "punctuation except required hyphens. Never output tags. Output the entire corrected "
        "<utterance>, never only the changed span, or exactly NOCHANGE if unchanged. Trimming "
        "leading or trailing whitespace is not a change; return NOCHANGE rather than a trimmed "
        "copy.\n\n"
        "NOCHANGE examples: 'come and see this'; 'come and get it'; "
        "'The colon absorbs water'; 'A semicolon joins clauses'; 'I have a question'; "
        "'The hyphen key is stuck'; 'Run link talon'; 'whether their report was'; "
        "'please comment on it'; 'This issue is high priority'; "
        "'When the server is ready run the benchmark'; "
        "'viewport frame purple if it is a cached frame'; "
        "'I use it a lot'; 'We found a safe haven'; "
        "'ask Danise whether it is ready'.\n"
        "<text_before></text_before><utterance>Hello Sarah</utterance> -> NOCHANGE\n"
        "<utterance>I can take care of</utterance> -> NOCHANGE\n"
        "<text_before>Their going to deploy it</text_before>"
        "<utterance> after the benchmark</utterance> -> NOCHANGE\n"
        "<text_before>What time is it question mark</text_before>"
        "<utterance> I don't know</utterance> -> NOCHANGE\n"
        "<text_before>The options are red</text_before>"
        "<utterance> green and blue</utterance> -> NOCHANGE\n\n"
        "FIX examples:\n"
        "'first come and second come and third' -> 'first, second, third'\n"
        '"I\'m not sure come and can you help" -> "I\'m not sure, can you help"\n'
        "'giraffe common elephant common lion' -> 'giraffe, elephant, lion'\n"
        "'Set the header coal on enabled' -> 'Set the header: enabled'\n"
        "'That worked exclamation Marc' -> 'That worked!'\n"
        "'The exclamation mark is large' -> NOCHANGE\n"
        "'Why did it fail question more' -> 'Why did it fail?'\n"
        "'client haven server' -> 'client-server'\n"
        "'a high priority issue' -> 'a high-priority issue'\n"
        "'state of the art model' -> 'state-of-the-art model'\n"
        "'Their going to deploy it' -> \"They're going to deploy it\"\n"
        "'There are two many requests' -> 'There are too many requests'\n"
        "'ask michael whether it is ready' -> 'ask Michael whether it is ready'\n"
        "<text_before>This is a well</text_before>"
        "<utterance> known issue</utterance> -> '-known issue'\n"
        "Remember: never insert an unspoken comma.\n"
        "Preserve every existing punctuation character, including closing delimiters.\n"
        "Never delete spoken content; preserve unfinished endings.\n"
        "If changed, repeat the entire utterance with only the correction; otherwise output "
        "NOCHANGE.\n"
        f"<text_before>{preceding_text}</text_before>"
        f"<utterance>{utterance_text}</utterance>\n"
    )


def _normalize_ai_cleanup_response(response: str) -> str:
    response = response.strip("\n")
    if response.endswith("\nNOCHANGE"):
        return "NOCHANGE"
    return response


def _strip_ai_cleanup_output_guards(response: str) -> str:
    response = response.strip()
    if (
        len(response) >= 2
        and response[0] == response[-1]
        and response[0] in {'"', "'", "`"}
    ):
        return response[1:-1].strip()
    return response


def _make_ai_cleanup_perf(
    backend: DictationAiCleanupBackend, wall_ms: float
) -> DictationAiCleanupPerf:
    return DictationAiCleanupPerf(backend=backend, wall_ms=wall_ms)


def _extract_ollama_response_and_perf(
    body: bytes, wall_ms: float = 0.0
) -> tuple[str, DictationAiCleanupPerf]:
    data = json.loads(body.decode("utf-8"))
    perf = _make_ai_cleanup_perf("ollama", wall_ms)
    perf.prompt_tokens = data["prompt_eval_count"]
    perf.completion_tokens = data["eval_count"]
    perf.prefill_ms = data["prompt_eval_duration"] / 1_000_000.0
    perf.decode_ms = data["eval_duration"] / 1_000_000.0
    perf.total_ms = data["total_duration"] / 1_000_000.0
    perf.load_ms = data["load_duration"] / 1_000_000.0
    response = data["response"]
    return _normalize_ai_cleanup_response(response), perf


def _extract_mlx_vlm_response_and_perf(
    body: bytes, wall_ms: float = 0.0
) -> tuple[str, DictationAiCleanupPerf]:
    data = json.loads(body.decode("utf-8"))
    perf = _make_ai_cleanup_perf("mlx", wall_ms)
    usage = data["usage"]
    timings = data.get("timings", {})
    perf.prompt_tokens = usage.get("input_tokens", usage.get("prompt_tokens"))
    perf.completion_tokens = usage.get("output_tokens", usage.get("completion_tokens"))
    perf.cached_prompt_tokens = usage.get("prompt_tokens_details", {}).get(
        "cached_tokens"
    )
    perf.prefill_tps = usage.get("prompt_tps", timings.get("prompt_per_second"))
    perf.decode_tps = usage.get("generation_tps", timings.get("predicted_per_second"))
    perf.peak_memory_gb = usage.get("peak_memory", timings.get("peak_memory"))
    if "prompt_ms" in timings:
        perf.prefill_ms = timings["prompt_ms"]
    elif perf.prompt_tokens is not None and perf.prefill_tps:
        uncached_prompt_tokens = perf.prompt_tokens
        if perf.cached_prompt_tokens is not None:
            uncached_prompt_tokens = max(
                0, perf.prompt_tokens - perf.cached_prompt_tokens
            )
        perf.prefill_ms = (uncached_prompt_tokens / perf.prefill_tps) * 1000.0
    if "predicted_ms" in timings:
        perf.decode_ms = timings["predicted_ms"]
    elif perf.completion_tokens is not None and perf.decode_tps:
        perf.decode_ms = (perf.completion_tokens / perf.decode_tps) * 1000.0
    choices = data["choices"]
    first_choice = choices[0]
    message = first_choice["message"]
    content = message["content"]
    if isinstance(content, str):
        return _normalize_ai_cleanup_response(content), perf
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if item["type"] in {"text", "output_text"}:
                text_parts.append(item["text"])
        return _normalize_ai_cleanup_response("".join(text_parts)), perf
    return "", perf


def _log_ai_cleanup_perf(
    perf: DictationAiCleanupPerf, error: Optional[Exception] = None
) -> None:
    parts = [
        f"backend={perf.backend}",
        f"wall={perf.wall_ms:.1f}ms",
    ]
    if perf.server_call_ms is not None:
        parts.append(f"server_call={perf.server_call_ms:.1f}ms")
    if perf.client_prep_ms is not None:
        parts.append(f"client_prep={perf.client_prep_ms:.1f}ms")
    if perf.total_ms is not None:
        parts.append(f"backend_total={perf.total_ms:.1f}ms")
    if perf.load_ms is not None:
        parts.append(f"load={perf.load_ms:.1f}ms")
    if perf.prompt_tokens is not None:
        parts.append(f"prompt_tokens={perf.prompt_tokens}")
    if perf.cached_prompt_tokens is not None:
        parts.append(f"cached_prompt_tokens={perf.cached_prompt_tokens}")
    if perf.completion_tokens is not None:
        parts.append(f"completion_tokens={perf.completion_tokens}")
    if perf.peak_memory_gb is not None:
        parts.append(f"peak_memory={perf.peak_memory_gb:.2f}GB")
    prefill_tps = perf.prefill_tokens_per_second()
    if perf.prefill_ms is not None:
        parts.append(f"prefill={perf.prefill_ms:.1f}ms")
    if prefill_tps is not None:
        parts.append(f"prefill_rate={prefill_tps:.1f} tok/s")
    decode_tps = perf.decode_tokens_per_second()
    if perf.decode_ms is not None:
        parts.append(f"decode={perf.decode_ms:.1f}ms")
    if decode_tps is not None:
        parts.append(f"decode_rate={decode_tps:.1f} tok/s")
    if perf.prefill_ms is None and perf.decode_ms is None:
        parts.append("phase_rates=unavailable")
    if error is not None:
        parts.append(f"error={error}")
    logging.debug("Dictation AI cleanup perf: %s", " ".join(parts))


def _is_dictation_ai_cleanup_backend(
    value: object,
) -> TypeGuard[DictationAiCleanupBackend]:
    return value in {"ollama", "mlx"}


def _current_sentence_fragment(text: str) -> str:
    current_line = re.split(r"[\r\n]", text)[-1]
    sentence_end = None
    # Treat ASCII/curly closing quotes (U+2019, U+201D) and closing brackets as
    # sentence trailers, so text such as `Finished.”` contributes no context.
    for match in re.finditer(r"""[.!?]["'\u2019\u201d)\]}]*(?=\s|$)""", current_line):
        sentence_end = match.end()
    if sentence_end is not None:
        current_line = current_line[sentence_end:]
    return current_line.lstrip()


def _split_outer_whitespace(text: str) -> tuple[str, str, str]:
    left = 0
    right = len(text)
    while left < right and text[left].isspace():
        left += 1
    while right > left and text[right - 1].isspace():
        right -= 1
    return text[:left], text[left:right], text[right:]


def _starts_with_attached_punctuation(text: str) -> bool:
    if not text:
        return False
    # Connector, dash, closing, final-quote, and other punctuation attach to
    # preceding text. Opening punctuation and initial quotes retain the space.
    return unicodedata.category(text[0]) in {"Pc", "Pd", "Pe", "Pf", "Po"}


def _removes_capitalization(original: str, corrected: str) -> bool:
    """Return whether an edit lowers any previously uppercase character."""
    return any(
        char.isupper() and (index >= len(corrected) or not corrected[index].isupper())
        for index, char in enumerate(original)
    )


def _is_allowed_ai_cleanup_word_replacement(
    original_words: list[str], corrected_words: list[str]
) -> bool:
    """Allow equal-count homophones or one localized split/merge."""
    return len(original_words) == len(corrected_words) or (
        bool(original_words)
        and bool(corrected_words)
        and len(original_words) <= 2
        and len(corrected_words) <= 2
    )


def _is_safe_ai_cleanup_edit(original: str, corrected: str) -> bool:
    """Reject model edits outside the cleanup operation's structural limits."""
    # Compare words independently of punctuation, but keep their original forms
    # so an otherwise unchanged word cannot silently change capitalization.
    word_pattern = r"\b[\w']+\b"
    original_words = re.findall(word_pattern, original)
    corrected_words = re.findall(word_pattern, corrected)
    matcher = SequenceMatcher(
        None,
        [word.lower() for word in original_words],
        [word.lower() for word in corrected_words],
        autojunk=False,
    )
    deletion_spans = 0
    deleted_word_count = 0
    lexical_edit_spans = 0
    allowed_removed_punctuation: Counter[str] = Counter()
    for operation, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        old_words = original_words[old_start:old_end]
        new_words = corrected_words[new_start:new_end]
        if operation == "equal":
            # Adding capitalization can correct a recognized name, but removing
            # existing capitalization may corrupt special vocabulary.
            if any(
                _removes_capitalization(old, new)
                for old, new in zip(old_words, new_words, strict=True)
            ):
                return False
            continue
        if operation == "replace" and _is_allowed_ai_cleanup_word_replacement(
            old_words, new_words
        ):
            # One replacement may correct a homophone or a localized word
            # boundary. Capitalized words after the first are proper nouns.
            if _removes_capitalization("".join(old_words), "".join(new_words)):
                return False
            if any(
                index > 0 and any(char.isupper() for char in old)
                for index, old in enumerate(old_words, old_start)
            ):
                return False
            if len(old_words) == len(new_words):
                # Apostrophe removal can itself be a homophone correction, as
                # in `it's` -> `its`. No other existing punctuation is editable.
                for old, new in zip(old_words, new_words, strict=True):
                    if (
                        old.replace("'", "").casefold()
                        == new.replace("'", "").casefold()
                    ):
                        removed_apostrophes = old.count("'") - new.count("'")
                        if removed_apostrophes > 0:
                            allowed_removed_punctuation["'"] += removed_apostrophes
            lexical_edit_spans += 1
            continue
        if operation == "insert" and len(new_words) == 1:
            # Permit one model-restored recognition omission. The prompt must
            # supply the semantic judgment; this guard limits its blast radius.
            lexical_edit_spans += 1
            continue
        if operation in {"delete", "replace"} and not new_words:
            # A punctuation name may consume one or two recognized words.
            if not 1 <= len(old_words) <= 2:
                return False
            deletion_spans += 1
            deleted_word_count += len(old_words)
            continue
        # Broader insertions, reordered words, and broad replacements are unsafe.
        return False

    original_punctuation = Counter(
        char for char in original if unicodedata.category(char).startswith("P")
    )
    corrected_punctuation = Counter(
        char for char in corrected if unicodedata.category(char).startswith("P")
    )
    removed_punctuation = original_punctuation - corrected_punctuation
    if removed_punctuation - allowed_removed_punctuation:
        return False

    # Every deleted phrase must be accounted for by newly added punctuation.
    added_marks = {
        mark: max(0, corrected.count(mark) - original.count(mark)) for mark in ",;:!?-"
    }
    # Multiple independent lexical edits are too broad to accept automatically.
    if lexical_edit_spans > 1:
        return False
    if deletion_spans > sum(added_marks.values()):
        return False
    # A complete question-mark or exclamation-mark name requires two spoken
    # words. This prevents a literal `question` or `exclamation` from becoming
    # punctuation while still allowing phonetic variants of the complete name.
    required_deleted_words = (
        sum(count for mark, count in added_marks.items() if mark != "-")
        + added_marks["?"]
        + added_marks["!"]
    )
    if deleted_word_count < required_deleted_words:
        return False
    # Hyphens may be unspoken. Every other new mark must consume a spoken name.
    return (
        sum(count for mark, count in added_marks.items() if mark != "-")
        <= deletion_spans
    )


def _log_ai_cleanup_result(
    result: DictationAiCleanupResult, preceding_text: str, utterance_text: str
) -> None:
    logging.debug(
        "Dictation AI cleanup: outcome=%s preceding_text=%r input=%r output=%r",
        result.outcome,
        preceding_text,
        utterance_text,
        result.model_output,
    )


def _run_ai_cleanup(
    preceding_text: str,
    utterance_text: str,
    model: str,
    url: str,
    timeout_seconds: int,
    backend: DictationAiCleanupBackend,
) -> Optional[str]:
    result = _run_ai_cleanup_result(
        preceding_text, utterance_text, model, url, timeout_seconds, backend
    )
    return result.corrected_text


def _run_ai_cleanup_result(
    preceding_text: str,
    utterance_text: str,
    model: str,
    url: str,
    timeout_seconds: int,
    backend: DictationAiCleanupBackend,
) -> DictationAiCleanupResult:
    preceding_text = _current_sentence_fragment(preceding_text)
    leading_whitespace, utterance_core, trailing_whitespace = _split_outer_whitespace(
        utterance_text
    )
    if not utterance_core:
        result = DictationAiCleanupResult(None, None, "empty")
        _log_ai_cleanup_result(result, preceding_text, utterance_text)
        return result
    request_started = time.perf_counter()
    server_call_started: Optional[float] = None
    try:
        prompt = _cleanup_prompt(preceding_text, utterance_text)
        if backend == "ollama":
            payload_dict = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {"temperature": 0.0},
            }
        else:
            payload_dict = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": 0.0,
            }
        payload = json.dumps(payload_dict).encode("utf-8")
        server_call_started = time.perf_counter()
        response = requests.post(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout_seconds,
        )
        response_body = response.content
        response_received = time.perf_counter()
        wall_ms = (response_received - request_started) * 1000.0
        server_call_ms = (
            (response_received - server_call_started) * 1000.0
            if server_call_started is not None
            else None
        )
        client_prep_ms = (
            (server_call_started - request_started) * 1000.0
            if server_call_started is not None
            else None
        )
        if backend == "ollama":
            corrected_raw, perf = _extract_ollama_response_and_perf(
                response_body, wall_ms
            )
        else:
            corrected_raw, perf = _extract_mlx_vlm_response_and_perf(
                response_body, wall_ms
            )
        perf.server_call_ms = server_call_ms
        perf.client_prep_ms = client_prep_ms
    except (
        requests.exceptions.RequestException,
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as error:
        failed_at = time.perf_counter()
        wall_ms = (failed_at - request_started) * 1000.0
        server_call_ms = (
            (failed_at - server_call_started) * 1000.0
            if server_call_started is not None
            else None
        )
        client_prep_ms = (
            (server_call_started - request_started) * 1000.0
            if server_call_started is not None
            else None
        )
        perf = _make_ai_cleanup_perf(backend, wall_ms)
        perf.server_call_ms = server_call_ms
        perf.client_prep_ms = client_prep_ms
        _log_ai_cleanup_perf(perf, error)
        result = DictationAiCleanupResult(None, str(error), "error")
        _log_ai_cleanup_result(result, preceding_text, utterance_text)
        return result
    _log_ai_cleanup_perf(perf)
    corrected_core = _strip_ai_cleanup_output_guards(corrected_raw)
    if corrected_core == "NOCHANGE":
        result = DictationAiCleanupResult(None, corrected_core, "nochange")
        _log_ai_cleanup_result(result, preceding_text, utterance_text)
        return result
    if not corrected_core:
        result = DictationAiCleanupResult(None, corrected_core, "empty")
        _log_ai_cleanup_result(result, preceding_text, utterance_text)
        return result
    if corrected_core == utterance_core:
        result = DictationAiCleanupResult(None, corrected_core, "identical")
        _log_ai_cleanup_result(result, preceding_text, utterance_text)
        return result
    if not _is_safe_ai_cleanup_edit(utterance_core, corrected_core):
        result = DictationAiCleanupResult(None, corrected_core, "unsafe")
        _log_ai_cleanup_result(result, preceding_text, utterance_text)
        return result
    corrected_leading = (
        "" if _starts_with_attached_punctuation(corrected_core) else leading_whitespace
    )
    corrected = f"{corrected_leading}{corrected_core}{trailing_whitespace}"
    result = DictationAiCleanupResult(corrected, corrected_core, "corrected")
    _log_ai_cleanup_result(result, preceding_text, utterance_text)
    return result


def _apply_ai_cleanup_rewrite(
    preceding_text: str,
    insertions: list[tuple[str, str]],
    corrected_utterance_text: str,
    utterance_suffix: str,
):
    for _ in insertions:
        actions.user.clear_last_phrase()
    if utterance_suffix:
        actions.user.insert_between(corrected_utterance_text, utterance_suffix)
    else:
        actions.insert(corrected_utterance_text)
    actions.user.add_phrase_to_history(corrected_utterance_text, utterance_suffix)
    dictation_formatter.update_context(preceding_text)
    dictation_formatter.pass_through(corrected_utterance_text)


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
        actions.user.select_last_phrase(skip_whitespace=True)
        text_toggles = []
        for format in formats:
            if format == "bold":
                actions.user.bold()
                text_toggles.append(format)
            elif format == "italic":
                actions.user.italic()
                text_toggles.append(format)
            elif format != "link":
                logging.warning("Unknown rich text format: %s", format)
        if "link" in formats:
            # Hyperlinking in Google Docs collapses the selection, so it must run
            # after selection-preserving toggles like bold and italic.
            actions.user.link_selection_from_clipboard()
        else:
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
        preceding_text = dictation_formatter.before
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
                preceding_text = dictation_formatter.before
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
        if phrase_timestamp is not None:
            global utterance_preceding_text, utterance_had_dictation
            if not utterance_had_dictation:
                utterance_preceding_text = preceding_text
            utterance_had_dictation = True
            utterance_insertions.append((text, " " if add_space_after else ""))

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
