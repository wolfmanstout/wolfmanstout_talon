"""Evaluation tests for dictation AI cleanup prompt.

Requires a running local LLM server. Skipped by default.
Run with: pytest -m ollama test/test_dictation_ai_eval.py
Run hard requirements with: pytest -m "ollama and hard" test/test_dictation_ai_eval.py
Score ideal behavior with: pytest -m "ollama and ideal" test/test_dictation_ai_eval.py

Override the target server with environment variables, for example:
DICTATION_AI_CLEANUP_BACKEND=mlx
DICTATION_AI_CLEANUP_MODEL=mlx-community/gemma-4-26b-a4b-it-qat-4bit
DICTATION_AI_CLEANUP_URL=http://127.0.0.1:8080/chat/completions
"""

import os
import re

import talon

if hasattr(talon, "test_mode"):
    import pytest

    from core.text.text_and_dictation import _run_ai_cleanup

    DEFAULT_BACKEND = os.getenv("DICTATION_AI_CLEANUP_BACKEND", "mlx")
    DEFAULT_MODEL = os.getenv(
        "DICTATION_AI_CLEANUP_MODEL", "mlx-community/gemma-4-26b-a4b-it-qat-4bit"
    )
    DEFAULT_URL = os.getenv(
        "DICTATION_AI_CLEANUP_URL", "http://127.0.0.1:8080/chat/completions"
    )
    DEFAULT_TIMEOUT = int(os.getenv("DICTATION_AI_CLEANUP_TIMEOUT_S", "10"))

    def cleanup(utterance, prior_context=""):
        return _run_ai_cleanup(
            prior_context,
            utterance,
            DEFAULT_MODEL,
            DEFAULT_URL,
            DEFAULT_TIMEOUT,
            DEFAULT_BACKEND,
        )

    # -- Cases where speech-recognition errors should be corrected --

    @pytest.mark.ollama
    @pytest.mark.ideal
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
                (
                    "I like cats, dogs and birds",
                    "I like cats, dogs, and birds",
                ),
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
            # Prior context can make a clause-comma reading more obvious.
            (
                "common I need to reschedule",
                "I'm running late",
                ", I need to reschedule",
            ),
            (
                "come and I can help",
                "I'm available now",
                ", I can help",
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
            "context-common-leading-clause",
            "context-come-and-leading-clause",
        ],
    )
    def test_should_fix_misrecognized_comma(utterance, prior_context, expected):
        result = cleanup(utterance, prior_context)
        assert result is not None, (
            f"Expected correction but got NOCHANGE for: {utterance}"
        )
        # Strip leading/trailing whitespace for comparison
        expected_outputs = (expected,) if isinstance(expected, str) else expected
        assert result.strip() in expected_outputs, (
            f"Input: {utterance!r}\nExpected: {expected!r}\nGot: {result!r}"
        )

    @pytest.mark.ollama
    @pytest.mark.ideal
    @pytest.mark.parametrize(
        "utterance, expected",
        [
            (
                "The choices are colon red green or blue",
                (
                    "The choices are: red, green or blue",
                    "The choices are: red, green, or blue",
                ),
            ),
            ("Set the header coal on enabled", "Set the header: enabled"),
            ("I finished semicolon you can start", "I finished; you can start"),
            (
                "Keep the cache semi colon it is still valid",
                "Keep the cache; it is still valid",
            ),
            ("Stop exclamation mark", "Stop!"),
            ("That worked exclamation Marc", "That worked!"),
            ("Are you ready question mark", "Are you ready?"),
            ("Why did it fail question Marc", "Why did it fail?"),
        ],
        ids=[
            "colon",
            "colon-misrecognized",
            "semicolon",
            "semicolon-split",
            "exclamation-mark",
            "exclamation-mark-misrecognized",
            "question-mark",
            "question-mark-misrecognized",
        ],
    )
    def test_should_fix_other_punctuation(utterance, expected):
        result = cleanup(utterance)
        assert result is not None, (
            f"Expected correction but got NOCHANGE for: {utterance}"
        )
        expected_outputs = (expected,) if isinstance(expected, str) else expected
        assert result.strip() in expected_outputs, (
            f"Input: {utterance!r}\nExpected: {expected!r}\nGot: {result!r}"
        )

    @pytest.mark.ollama
    @pytest.mark.ideal
    @pytest.mark.parametrize(
        "utterance, prior_context, expected",
        [
            ("Yes I agree", "", "Yes, I agree"),
            ("However I would wait", "", "However, I would wait"),
            (
                "After reviewing the logs I changed the timeout",
                "",
                "After reviewing the logs, I changed the timeout",
            ),
            (
                "When the server is ready run the benchmark",
                "",
                "When the server is ready, run the benchmark",
            ),
            (
                "to be clear this is optional",
                "The benchmark passed",
                "to be clear, this is optional",
            ),
            (
                "No don't fix the stale comment, fix the code so that it aligns with that comment",
                "",
                "No, don't fix the stale comment, fix the code so that it aligns with that comment",
            ),
            (
                "So for this reason we should",
                "have ideas).",
                (
                    "So for this reason we should",
                    "So for this reason, we should",
                    "So, for this reason, we should",
                ),
            ),
            (
                "I finished you can start",
                "",
                ("I finished you can start", "I finished, you can start"),
            ),
        ],
        ids=[
            "yes",
            "however",
            "introductory-phrase",
            "introductory-clause",
            "context-incomplete",
            "discourse-no",
            "for-this-reason",
            "independent-clauses",
        ],
    )
    def test_should_insert_confident_comma(utterance, prior_context, expected):
        result = cleanup(utterance, prior_context)
        actual = utterance if result is None else result.strip()
        expected_outputs = (expected,) if isinstance(expected, str) else expected
        assert actual in expected_outputs, (
            f"Input: {utterance!r}\nExpected: {expected!r}\nGot: {result!r}"
        )

    @pytest.mark.ollama
    @pytest.mark.ideal
    @pytest.mark.parametrize(
        "utterance, prior_context, expected",
        [
            ("Their going to deploy it", "", "They're going to deploy it"),
            ("Its ready to run", "", "It's ready to run"),
            ("The cache lost it's state", "", "The cache lost its state"),
            ("There are two many requests", "", "There are too many requests"),
            ("We need to right the file", "", "We need to write the file"),
            ("Use the write configuration", "", "Use the right configuration"),
            (
                "There going tomorrow",
                "The release is scheduled",
                "They're going tomorrow",
            ),
            (
                "invalidate the cash if scroll detection ever fails",
                "we should",
                "invalidate the cache if scroll detection ever fails",
            ),
        ],
        ids=[
            "their-theyre",
            "its-its-contraction",
            "its-possessive",
            "two-too",
            "right-write",
            "write-right",
            "context-theyre",
            "cash-cache",
        ],
    )
    def test_should_fix_homophone(utterance, prior_context, expected):
        result = cleanup(utterance, prior_context)
        assert result is not None, (
            f"Expected correction but got NOCHANGE for: {utterance}"
        )
        assert result.strip() == expected, (
            f"Input: {utterance!r}\nExpected: {expected!r}\nGot: {result!r}"
        )

    @pytest.mark.ollama
    @pytest.mark.ideal
    def test_should_fix_main_homophone():
        utterance = "Commit then rebase on maine and push"
        result = cleanup(utterance)
        actual = utterance if result is None else result.strip()
        words = re.findall(r"\b[\w']+\b", actual.lower())
        assert "main" in words and "maine" not in words, (
            f"Expected maine -> main correction, got: {result!r}"
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
            # From real logs: false positive cases from earlier prompts
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
            # From real logs: model added a comma without any trigger word
            ("Also create", ""),
            # Punctuation words and near-homophones used literally.
            ("The colon absorbs water", ""),
            ("A semicolon joins related clauses", ""),
            ("The exclamation mark is too large", ""),
            ("Mark asked a question", ""),
            ("Please call on the next speaker", ""),
            # Do not infer unspoken punctuation other than a highly confident comma.
            ("Are you ready", ""),
            ("This is amazing", ""),
            ("Here are the options", ""),
            ("We should rerun the benchmark if the flag changes", ""),
            ("but only when requests arrive quickly", "The cache works"),
            # Correctly used homophones must remain untouched.
            ("Their server is fast", ""),
            ("They're going home", ""),
            ("The service warmed its cache", ""),
            ("It's ready", ""),
            ("Write the result to the right file", ""),
            ("Two requests are too many", ""),
            ("I know the answer is no", ""),
            # Grammar and style are outside the allowed scope.
            ("Me and him tested it", ""),
            ("I wanna see how this compares", ""),
            ("we should kind of maybe try it", ""),
        ],
        ids=[
            "simple-text",
            "continuation",
            "command-like",
            "run-link-talon",
            "let-me-know",
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
            "no-trigger-also-create",
            "literal-colon",
            "literal-semicolon",
            "literal-exclamation-mark",
            "literal-question-mark-name",
            "literal-call-on",
            "no-unspoken-question-mark",
            "no-unspoken-exclamation-mark",
            "no-unspoken-colon",
            "no-unspoken-semicolon",
            "incomplete-clause-no-comma",
            "correct-their",
            "correct-theyre",
            "correct-its-possessive",
            "correct-its-contraction",
            "correct-write-right",
            "correct-two-too",
            "correct-know-no",
            "grammar-pronouns",
            "style-wanna",
            "style-fillers",
        ],
    )
    @pytest.mark.ideal
    def test_should_not_change(utterance, prior_context):
        result = cleanup(utterance, prior_context)
        assert result is None, (
            f"Expected NOCHANGE but got correction for: {utterance!r}\nGot: {result!r}"
        )

    @pytest.mark.ollama
    @pytest.mark.hard
    @pytest.mark.parametrize(
        "utterance, prior_context",
        [
            (
                "update the cached viewport after a successful scroll detection",
                "we should",
            ),
            ("on the issue", "please comment"),
            ("problem", "this is a common"),
            ("after the benchmark", "Their going to deploy it"),
            ("I don't know", "What time is it question mark"),
        ],
        ids=[
            "ordinary-continuation",
            "literal-comment",
            "literal-common",
            "ignore-context-homophone",
            "ignore-context-punctuation",
        ],
    )
    def test_should_never_output_prior_context(utterance, prior_context):
        result = cleanup(utterance, prior_context)
        assert result is None, (
            "Read-only prior context affected the model output:\n"
            f"Context: {prior_context!r}\nGot: {result!r}"
        )

    @pytest.mark.ollama
    @pytest.mark.hard
    def test_should_never_repeat_prior_context():
        utterance = "invalidate the cash if scroll detection ever fails"
        prior_context = "we should"
        result = cleanup(utterance, prior_context)
        assert result is None or not result.strip().startswith(prior_context), (
            "Prior context was repeated in the model output:\n"
            f"Context: {prior_context!r}\nGot: {result!r}"
        )

    @pytest.mark.ollama
    @pytest.mark.hard
    def test_should_never_delete_or_reorder_words():
        utterance = "Commit then rebase on maine and push"
        result = cleanup(utterance)
        actual = utterance if result is None else result.strip()
        words = re.findall(r"\b[\w']+\b", actual.lower())
        words = ["maine" if word == "main" else word for word in words]
        assert words == re.findall(r"\b[\w']+\b", utterance.lower()), (
            f"A non-homophone word was added, deleted, or reordered: {result!r}"
        )
