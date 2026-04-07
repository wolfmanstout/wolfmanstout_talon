"""Evaluation tests for dictation AI cleanup prompt.

Requires a running Ollama instance. Skipped by default.
Run with: pytest -m ollama
"""

import talon

if hasattr(talon, "test_mode"):
    import pytest

    from core.text.text_and_dictation import _run_ai_cleanup

    DEFAULT_MODEL = "gemma4:e4b"
    DEFAULT_URL = "http://127.0.0.1:11434/api/generate"
    DEFAULT_TIMEOUT = 10

    def cleanup(utterance, prior_context=""):
        return _run_ai_cleanup(
            prior_context, utterance, DEFAULT_MODEL, DEFAULT_URL, DEFAULT_TIMEOUT
        )

    # -- Cases where commas should be inserted (returned text != None) --

    @pytest.mark.ollama
    @pytest.mark.parametrize(
        "utterance, prior_context, expected",
        [
            # "comment" -> comma
            (
                "apples comment oranges comment bananas",
                "",
                "apples, oranges, bananas",
            ),
            # "come and" -> comma
            (
                "first come and second come and third",
                "",
                "first, second, third",
            ),
            # "comma" -> comma
            (
                "red comma green comma blue",
                "",
                "red, green, blue",
            ),
            # Single comma replacement
            (
                "I like cats comment dogs and birds",
                "",
                "I like cats, dogs and birds",
            ),
            # From real logs: "come and" in middle of sentence
            (
                "I'm not sure come and can you help",
                "",
                "I'm not sure, can you help",
            ),
            # "common" -> comma
            (
                "giraffe common elephant common lion",
                "",
                "giraffe, elephant, lion",
            ),
            (
                "I went to the store common bought milk common and came home",
                "",
                "I went to the store, bought milk, and came home",
            ),
        ],
        ids=[
            "comment-multiple",
            "come-and-multiple",
            "comma-multiple",
            "comment-single",
            "come-and-real-log",
            "common-multiple",
            "common-single",
        ],
    )
    def test_should_fix_comma(utterance, prior_context, expected):
        result = cleanup(utterance, prior_context)
        assert result is not None, f"Expected correction but got NOCHANGE for: {utterance}"
        # Strip leading/trailing whitespace for comparison
        assert result.strip() == expected, (
            f"Input: {utterance!r}\nExpected: {expected!r}\nGot: {result!r}"
        )

    # -- Cases where nothing should change (returned None) --

    @pytest.mark.ollama
    @pytest.mark.parametrize(
        "utterance, prior_context",
        [
            # Normal text, no comma words present
            ("This is a test", ""),
            ("this is another", "This is a test"),
            ("Switch back to main", ""),
            ("Run link talon", ""),
            ("let me know if you have ideas", "actually scrolling"),
            ("So for this reason we should", "have ideas)."),
            # From real logs: false positive cases from earlier prompts
            (
                "invalidate the cash if scroll detection ever fails",
                "we should",
            ),
            (
                "update the cached viewport after a successful scroll detection",
                "we should",
            ),
            ("added only for that purpose", "that were"),
            (
                "viewport frame purple if it is a cached frame",
                "colors the",
            ),
            ("Adjust the prompt", ""),
            ("Set this environment variable in all contexts", ""),
            ("feel free to search the web", "Is there a way to cleanly delete this"),
            # Words that contain comma-like substrings but aren't mistranscriptions
            ("please comment on the issue", ""),
            ("come and see this", ""),
            ("I want to comment on that", ""),
            ("come and get it", "Let's go"),
            ("this is a common problem", ""),
            ("we have a common interest in this", ""),
        ],
        ids=[
            "simple-text",
            "continuation",
            "command-like",
            "run-link-talon",
            "let-me-know",
            "for-this-reason",
            "invalidate-cache",
            "update-cached-viewport",
            "for-that-purpose",
            "viewport-frame",
            "adjust-prompt",
            "env-variable",
            "search-web",
            "actual-comment-on",
            "actual-come-and-see",
            "actual-comment-on-that",
            "actual-come-and-get",
            "actual-common-problem",
            "actual-common-interest",
        ],
    )
    def test_should_not_change(utterance, prior_context):
        result = cleanup(utterance, prior_context)
        assert result is None, (
            f"Expected NOCHANGE but got correction for: {utterance!r}\nGot: {result!r}"
        )
