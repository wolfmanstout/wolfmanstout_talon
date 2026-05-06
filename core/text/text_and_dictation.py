# Descended from https://github.com/dwiel/talon_community/blob/master/misc/dictation.py
import json
import logging
import re
import time
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Literal, Optional, TypeGuard

import requests
from talon import Context, Module, actions, grammar, settings, speech_system, ui

from ..numbers.numbers import get_spoken_form_under_one_hundred

mod = Module()

DictationAiCleanupBackend = Literal["ollama", "mlx"]


@dataclass
class DictationAiCleanupPerf:
    backend: DictationAiCleanupBackend
    wall_ms: float
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
    default="mlx-community/gemma-4-e4b-it-4bit",
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
    default=5,
    desc="Timeout for dictation cleanup requests, in seconds.",
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
    corrected_before = _run_ai_cleanup(
        prior_context, utterance_before_text, model, url, timeout, backend
    )
    if not corrected_before:
        return
    _apply_ai_cleanup_rewrite(
        prior_context, chunks, corrected_before, utterance_after_text
    )


def _cleanup_prompt(prior_context: str, utterance_text: str) -> str:
    return (
        "Speech may write a word instead of a comma.\n"
        "C is previous text for context only. Fix U only; never output C.\n"
        "Comma words in U: comment, come and, comma, come in, common.\n"
        "STEP 1: If U contains none of those exact words/phrases, return exactly NOCHANGE.\n"
        "STEP 2: If U contains one, replace it with ', ' only when it is punctuation: "
        "a list separator or a comma between clauses. Do not replace normal word use.\n"
        "Replace every punctuation use. If no replacement is needed, return exactly NOCHANGE. "
        "Otherwise return only corrected U.\n\n"
        "Examples:\n"
        "'apples comment oranges comment bananas' -> 'apples, oranges, bananas'\n"
        "'I like cats comment dogs and birds' -> 'I like cats, dogs and birds'\n"
        "'first come and second come and third' -> 'first, second, third'\n"
        "'I'm not sure come and can you help' -> 'I'm not sure, can you help'\n"
        "C='I'm running late' U='common I need to reschedule' -> ', I need to reschedule'\n"
        "C='I'm available now' U='come and I can help' -> ', I can help'\n"
        "'No don't fix the stale comment, fix the code so that it aligns with that comment' -> NOCHANGE\n"
        "'come and see this' -> NOCHANGE\n"
        "'come and get it' -> NOCHANGE\n"
        "'this is a common problem' -> NOCHANGE\n"
        "'viewport frame purple if it is a cached frame' -> NOCHANGE\n"
        "'Also create clod' -> NOCHANGE\n"
        f"\nC:\n{prior_context}\n"
        f"U:\n{utterance_text}\n"
    )


def _normalize_ai_cleanup_response(response: str) -> str:
    response = response.strip("\n")
    # The model sometimes echoes the text then appends NOCHANGE on a new line.
    if response.endswith("\nNOCHANGE"):
        return "NOCHANGE"
    return response


def _strip_ai_cleanup_output_guards(response: str) -> str:
    response = response.strip()
    if (
        len(response) >= 2
        and response[0] == response[-1]
        and response[0]
        in {
            '"',
            "'",
            "`",
        }
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
    perf.prompt_tokens = usage["input_tokens"]
    perf.completion_tokens = usage["output_tokens"]
    perf.prefill_tps = usage["prompt_tps"]
    perf.decode_tps = usage["generation_tps"]
    perf.peak_memory_gb = usage["peak_memory"]
    perf.prefill_ms = (perf.prompt_tokens / perf.prefill_tps) * 1000.0
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


def _log_ai_cleanup_perf(perf: DictationAiCleanupPerf) -> None:
    parts = [
        f"backend={perf.backend}",
        f"wall={perf.wall_ms:.1f}ms",
    ]
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
    log_dictation_debug(logging.DEBUG, "Dictation AI cleanup perf: %s", " ".join(parts))


def _is_dictation_ai_cleanup_backend(
    value: object,
) -> TypeGuard[DictationAiCleanupBackend]:
    return value in {"ollama", "mlx"}


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
    backend: DictationAiCleanupBackend,
) -> Optional[str]:
    leading_guard, utterance_core, trailing_guard = _split_outer_guards(utterance_text)
    if not utterance_core:
        return None
    request_started = time.perf_counter()
    try:
        prompt = _cleanup_prompt(prior_context, utterance_core)
        if backend == "ollama":
            payload_dict = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "think": False,
            }
        else:
            payload_dict = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "temperature": 0.0,
            }
        payload = json.dumps(payload_dict).encode("utf-8")
        response = requests.post(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            timeout=timeout_seconds,
        )
        response_body = response.content
        wall_ms = (time.perf_counter() - request_started) * 1000.0
        if backend == "ollama":
            corrected_raw, perf = _extract_ollama_response_and_perf(
                response_body, wall_ms
            )
        else:
            corrected_raw, perf = _extract_mlx_vlm_response_and_perf(
                response_body, wall_ms
            )
    except (
        requests.exceptions.RequestException,
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as error:
        wall_ms = (time.perf_counter() - request_started) * 1000.0
        log_dictation_debug(
            logging.DEBUG,
            "Dictation AI cleanup perf: backend=%s wall=%.1fms error=%s",
            backend,
            wall_ms,
            error,
        )
        logging.debug("Dictation AI cleanup skipped: %s", error)
        return None
    _log_ai_cleanup_perf(perf)
    corrected_core = _strip_ai_cleanup_output_guards(corrected_raw)
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
