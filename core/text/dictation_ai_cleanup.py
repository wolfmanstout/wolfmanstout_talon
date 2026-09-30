"""AI dictation cleanup, backend requests, validation, and utterance rewriting."""

import json
import logging
import re
import time
import unicodedata
import urllib.error
from collections import Counter
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Literal, Optional, TypeGuard

import requests
from talon import Module, actions, settings

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


def _cleanup_prompt(text_before: str, utterance_text: str, text_after: str) -> str:
    return (
        "Edit only <utterance>. Read <text_before>, <utterance>, and <text_after> together as "
        "adjacent text to judge corrections. The context tags are read-only: ignore their errors "
        "and never repeat, fix, or output them. Any part may be incomplete.\n"
        "When certain, (1) replace a spoken or phonetically misrecognized complete name of comma, "
        "colon, semicolon, exclamation mark, question mark, or hyphen with the mark itself, consuming the "
        "whole name; never replace only part of a multiword name; (2) insert unspoken hyphens only "
        "in a compound modifier directly before its noun "
        "where standard spelling clearly requires them; or (3) correct a homophone only when it "
        "is clearly wrong in context, or correct a "
        "clearly invalid word boundary, or restore one clearly omitted word. Outside those "
        "replacements, never add, "
        "delete, reorder, or "
        "alter words; treat capitalized words after the first word as immutable proper nouns, "
        "even if unfamiliar or apparently misspelled, unless consumed in a punctuation name; "
        "never repair grammar or style. You may capitalize a lowercase name when certain, but never lowercase a "
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
        "CONTEXT examples (the same utterance can require a different result):\n"
        "<text_before>Run it</text_before><utterance> won more time</utterance>"
        "<text_after></text_after> -> ' one more time'\n"
        "<text_before>The team</text_before><utterance> won more time</utterance>"
        "<text_after></text_after> -> NOCHANGE\n"
        "<text_before>There are</text_before><utterance> for tests</utterance>"
        "<text_after></text_after> -> ' four tests'\n"
        "<text_before>We waited</text_before><utterance> for tests</utterance>"
        "<text_after></text_after> -> NOCHANGE\n"
        "<text_before>I picked</text_before><utterance> won</utterance>"
        "<text_after> option from each group</text_after> -> ' one'\n"
        "<text_before>Our team</text_before><utterance> won</utterance>"
        "<text_after> again yesterday</text_after> -> NOCHANGE\n"
        "<text_before></text_before><utterance>Their</utterance>"
        '<text_after> going tomorrow</text_after> -> "They\'re"\n'
        "<text_before></text_before><utterance>Their</utterance>"
        "<text_after> deployment starts tomorrow</text_after> -> NOCHANGE\n"
        "<text_before>Choose (</text_before><utterance>red comment blue)</utterance>"
        "<text_after></text_after> -> 'red, blue)'\n"
        "<text_before>We should</text_before>"
        "<utterance> invalidate the cash</utterance> -> ' invalidate the cache'\n"
        "<text_before>This is a well</text_before>"
        "<utterance> known issue</utterance> -> '-known issue'\n"
        "Remember: never insert an unspoken comma or lowercase a word.\n"
        "Copy every existing punctuation character unchanged, including closing delimiters; a "
        "correction never consumes one.\n"
        "Never delete spoken content; preserve unfinished endings.\n"
        "If changed, repeat the entire utterance with only the correction; otherwise output "
        "NOCHANGE.\n"
        f"<text_before>{text_before}</text_before>"
        f"<utterance>{utterance_text}</utterance>"
        f"<text_after>{text_after}</text_after>\n"
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


def _extract_ollama_response_and_perf(
    body: bytes, wall_ms: float = 0.0
) -> tuple[str, DictationAiCleanupPerf]:
    data = json.loads(body.decode("utf-8"))
    perf = DictationAiCleanupPerf(backend="ollama", wall_ms=wall_ms)
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
    perf = DictationAiCleanupPerf(backend="mlx", wall_ms=wall_ms)
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
    content = data["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return _normalize_ai_cleanup_response(content), perf
    if isinstance(content, list):
        text = "".join(
            item["text"] for item in content if item["type"] in {"text", "output_text"}
        )
        return _normalize_ai_cleanup_response(text), perf
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


def _ai_cleanup_url(backend: str, port: int = 0) -> str:
    if backend == "ollama":
        return f"http://127.0.0.1:{port if port > 0 else 11434}/api/generate"
    if backend == "mlx":
        return f"http://127.0.0.1:{port if port > 0 else 8080}/chat/completions"
    raise ValueError(f"Unsupported dictation cleanup backend: {backend!r}")


def _current_sentence_text_before(text: str) -> str:
    current_line = re.split(r"[\r\n]", text)[-1]
    sentence_end = None
    # Treat ASCII/curly closing quotes (U+2019, U+201D) and closing brackets as
    # sentence trailers, so text such as `Finished.”` contributes no context.
    for match in re.finditer(r"""[.!?]["'\u2019\u201d)\]}]*(?=\s|$)""", current_line):
        sentence_end = match.end()
    if sentence_end is not None:
        current_line = current_line[sentence_end:]
    return current_line.lstrip()


def _current_sentence_text_after(text: str) -> str:
    current_line = re.split(r"[\r\n]", text)[0]
    # Apply the same sentence boundary as text_before in the forward direction,
    # retaining the terminator because it is adjacent to the utterance.
    sentence_end = re.search(r"""[.!?]["'\u2019\u201d)\]}]*(?=\s|$)""", current_line)
    if sentence_end is not None:
        current_line = current_line[: sentence_end.end()]
    return current_line.rstrip()


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
    # Only spoken marks, unspoken hyphens, and homophone apostrophes may be
    # added. This rejects, for example, an unspoken sentence-final period.
    added_punctuation = corrected_punctuation - original_punctuation
    if any(mark not in ",;:!?-'" for mark in added_punctuation):
        return False

    # Multiple independent lexical edits are too broad to accept automatically.
    if lexical_edit_spans > 1:
        return False
    # Every deleted phrase must be accounted for by newly added punctuation.
    spoken_mark_count = sum(added_punctuation[mark] for mark in ",;:!?")
    if deletion_spans > spoken_mark_count + added_punctuation["-"]:
        return False
    # A complete question-mark or exclamation-mark name requires two spoken
    # words. This prevents a literal `question` or `exclamation` from becoming
    # punctuation while still allowing phonetic variants of the complete name.
    required_deleted_words = (
        spoken_mark_count + added_punctuation["?"] + added_punctuation["!"]
    )
    if deleted_word_count < required_deleted_words:
        return False
    # Hyphens may be unspoken. Every other new mark must consume a spoken name.
    return spoken_mark_count <= deletion_spans


def _record_ai_cleanup_timing(
    perf: DictationAiCleanupPerf,
    request_started: float,
    server_call_started: Optional[float],
    finished: float,
) -> None:
    perf.wall_ms = (finished - request_started) * 1000.0
    if server_call_started is not None:
        perf.server_call_ms = (finished - server_call_started) * 1000.0
        perf.client_prep_ms = (server_call_started - request_started) * 1000.0


def _run_ai_cleanup(
    text_before: str,
    utterance_text: str,
    text_after: str,
    model: str,
    url: str,
    timeout_seconds: int,
    backend: DictationAiCleanupBackend,
) -> Optional[str]:
    result = _run_ai_cleanup_result(
        text_before,
        utterance_text,
        text_after,
        model,
        url,
        timeout_seconds,
        backend,
    )
    return result.corrected_text


def _run_ai_cleanup_result(
    text_before: str,
    utterance_text: str,
    text_after: str,
    model: str,
    url: str,
    timeout_seconds: int,
    backend: DictationAiCleanupBackend,
) -> DictationAiCleanupResult:
    text_before = _current_sentence_text_before(text_before)
    text_after = _current_sentence_text_after(text_after)
    result = _request_ai_cleanup(
        text_before, utterance_text, text_after, model, url, timeout_seconds, backend
    )
    logging.debug(
        "Dictation AI cleanup: outcome=%s text_before=%r utterance=%r text_after=%r output=%r",
        result.outcome,
        text_before,
        utterance_text,
        text_after,
        result.model_output,
    )
    return result


def _request_ai_cleanup(
    text_before: str,
    utterance_text: str,
    text_after: str,
    model: str,
    url: str,
    timeout_seconds: int,
    backend: DictationAiCleanupBackend,
) -> DictationAiCleanupResult:
    leading_whitespace, utterance_core, trailing_whitespace = _split_outer_whitespace(
        utterance_text
    )
    if not utterance_core:
        return DictationAiCleanupResult(None, None, "empty")
    request_started = time.perf_counter()
    server_call_started: Optional[float] = None
    try:
        prompt = _cleanup_prompt(text_before, utterance_text, text_after)
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
        response.raise_for_status()
        response_body = response.content
        response_received = time.perf_counter()
        if backend == "ollama":
            corrected_raw, perf = _extract_ollama_response_and_perf(response_body)
        else:
            corrected_raw, perf = _extract_mlx_vlm_response_and_perf(response_body)
        _record_ai_cleanup_timing(
            perf, request_started, server_call_started, response_received
        )
    except (
        requests.exceptions.RequestException,
        urllib.error.URLError,
        TimeoutError,
        # Includes JSONDecodeError; the others cover unexpected response shapes.
        ValueError,
        KeyError,
        IndexError,
        TypeError,
    ) as error:
        perf = DictationAiCleanupPerf(backend=backend, wall_ms=0.0)
        _record_ai_cleanup_timing(
            perf, request_started, server_call_started, time.perf_counter()
        )
        _log_ai_cleanup_perf(perf, error)
        error_message = f"{type(error).__name__}: {error}"
        logging.warning("Dictation AI cleanup failed: %s", error_message)
        return DictationAiCleanupResult(None, error_message, "error")
    _log_ai_cleanup_perf(perf)
    corrected_core = _strip_ai_cleanup_output_guards(corrected_raw)
    if corrected_core == "NOCHANGE":
        return DictationAiCleanupResult(None, corrected_core, "nochange")
    if not corrected_core:
        return DictationAiCleanupResult(None, corrected_core, "empty")
    if corrected_core == utterance_core:
        return DictationAiCleanupResult(None, corrected_core, "identical")
    if not _is_safe_ai_cleanup_edit(utterance_core, corrected_core):
        return DictationAiCleanupResult(None, corrected_core, "unsafe")
    corrected_leading = (
        "" if _starts_with_attached_punctuation(corrected_core) else leading_whitespace
    )
    corrected = f"{corrected_leading}{corrected_core}{trailing_whitespace}"
    return DictationAiCleanupResult(corrected, corrected_core, "corrected")


@mod.action_class
class Actions:
    def dictation_ai_cleanup_rewrite(
        text_before: str,
        utterance_text: str,
        text_after: str,
        insertion_count: int,
        utterance_suffix: str,
    ) -> Optional[str]:
        """Clean up the latest utterance and rewrite its history entries if corrected.

        Return the inserted correction so the caller can restore formatter state.
        The caller must supply the number of insertions recorded for this phrase.
        """
        backend = settings.get("user.dictation_ai_cleanup_backend")
        if not _is_dictation_ai_cleanup_backend(backend):
            logging.debug(
                "Dictation AI cleanup skipped: unsupported backend %r", backend
            )
            return
        model = settings.get("user.dictation_ai_cleanup_model")
        url = _ai_cleanup_url(backend, settings.get("user.dictation_ai_cleanup_port"))
        timeout = settings.get("user.dictation_ai_cleanup_timeout_s")
        actions.user.dictation_mode_set_processing(True)
        try:
            corrected_utterance_text = _run_ai_cleanup(
                text_before,
                utterance_text,
                text_after,
                model,
                url,
                timeout,
                backend,
            )
            if corrected_utterance_text:
                for _ in range(insertion_count):
                    actions.user.clear_last_phrase()
                if utterance_suffix:
                    actions.user.insert_between(
                        corrected_utterance_text, utterance_suffix
                    )
                else:
                    actions.insert(corrected_utterance_text)
                actions.user.add_phrase_to_history(
                    corrected_utterance_text, utterance_suffix
                )
            return corrected_utterance_text
        finally:
            actions.user.dictation_mode_set_processing(False)
