import json

import talon

PHRASE_EXAMPLES = ["", "foo", "foo bar", "lorem ipsum dolor sit amet"]

if hasattr(talon, "test_mode"):
    import pytest

    # Only include this when we're running tests
    from core.text import text_and_dictation

    def test_format_phrase():
        for x in PHRASE_EXAMPLES:
            assert text_and_dictation.format_phrase([x]) == x
            assert text_and_dictation.format_phrase(x.split()) == x

    def test_capture_to_words():
        # if l is a list of strings, then (capture_to_words(l) == l) should hold.
        for s in PHRASE_EXAMPLES:
            for l in [[s], s.split(), list(s)]:
                assert text_and_dictation.capture_to_words(l) == l

    def test_normalize_dictation_words():
        assert text_and_dictation.normalize_dictation_words([]) == []
        assert text_and_dictation.normalize_dictation_words(["..."]) == []
        assert text_and_dictation.normalize_dictation_words(["…"]) == []
        assert text_and_dictation.normalize_dictation_words(["Hello,", "world."]) == [
            "hello,",
            "world",
        ]
        assert text_and_dictation.normalize_dictation_words(
            ["This", "has", "e.g.", "inside."]
        ) == ["this", "has", "e.g.", "inside"]
        assert text_and_dictation.normalize_dictation_words(["wait", "..."]) == ["wait"]
        assert text_and_dictation.normalize_dictation_words(["wait", "…"]) == ["wait"]
        assert text_and_dictation.normalize_dictation_words(["really", "?"]) == [
            "really"
        ]
        assert text_and_dictation.normalize_dictation_words(["really", "?!"]) == [
            "really"
        ]
        assert text_and_dictation.normalize_dictation_words(["123", "done."]) == [
            "123",
            "done",
        ]
        assert text_and_dictation.normalize_dictation_words(["I", "agree."]) == [
            "I",
            "agree",
        ]
        assert text_and_dictation.normalize_dictation_words(['"I', "agree."]) == [
            '"I',
            "agree",
        ]
        assert text_and_dictation.normalize_dictation_words(["I'll", "agree."]) == [
            "I'll",
            "agree",
        ]
        assert text_and_dictation.normalize_dictation_words(["I'll,", "agree."]) == [
            "I'll,",
            "agree",
        ]
        assert text_and_dictation.normalize_dictation_words(["I’d", "agree."]) == [
            "I’d",
            "agree",
        ]
        assert text_and_dictation.normalize_dictation_words(["NASA", "works."]) == [
            "NASA",
            "works",
        ]
        assert text_and_dictation.normalize_dictation_words(["iPhone", "works."]) == [
            "iPhone",
            "works",
        ]
        assert text_and_dictation.normalize_dictation_words(["OpenAI", "works."]) == [
            "OpenAI",
            "works",
        ]
        assert text_and_dictation.normalize_dictation_words(['"Hello', "world."]) == [
            '"hello',
            "world",
        ]
        assert text_and_dictation.normalize_dictation_words(["(Hello", "world."]) == [
            "(hello",
            "world",
        ]
        assert text_and_dictation.normalize_dictation_words(['"NASA', "works."]) == [
            '"NASA',
            "works",
        ]

    def test_dictation_normalization_precedes_word_replacement():
        class FakePhrase(talon.grammar.vm.Phrase):
            pass

        previous_settings_get = getattr(text_and_dictation.settings, "get", None)
        text_and_dictation.settings.get = lambda name: (
            name == "user.normalize_dictation"
        )
        talon.actions.register_test_action(
            "dictate", "parse_words", lambda phrase: ["Custom", "thing..."]
        )
        talon.actions.register_test_action(
            "dictate",
            "replace_words",
            lambda words: (
                ["CustomThing"] if words == ["custom", "thing"] else list(words)
            ),
        )
        try:
            assert text_and_dictation.capture_to_words([FakePhrase()]) == [
                "CustomThing"
            ]
        finally:
            if previous_settings_get is None:
                del text_and_dictation.settings.get
            else:
                text_and_dictation.settings.get = previous_settings_get
            talon.actions.reset_test_actions()

    def test_ai_cleanup_sets_processing_indicator_until_finished(monkeypatch):
        events = []
        setting_values = {
            "user.dictation_ai_cleanup": True,
            "user.dictation_ai_cleanup_backend": "mlx",
            "user.dictation_ai_cleanup_model": "model",
            "user.dictation_ai_cleanup_port": 0,
            "user.dictation_ai_cleanup_timeout_s": 30,
        }
        monkeypatch.setattr(
            text_and_dictation.settings, "get", setting_values.__getitem__
        )
        monkeypatch.setattr(
            text_and_dictation,
            "_run_ai_cleanup",
            lambda before, utterance, after, *args: (
                events.append(("cleanup", before, utterance, after)) or None
            ),
        )
        talon.actions.register_test_action(
            "user",
            "dictation_mode_set_processing",
            lambda processing: events.append(processing),
        )
        text_and_dictation.utterance_insertions = [(" dictated text", "")]
        text_and_dictation.utterance_text_before = "Earlier text"
        text_and_dictation.utterance_text_after = " after text"
        text_and_dictation.utterance_had_dictation = True

        try:
            text_and_dictation.on_post_phrase(None)
        finally:
            talon.actions.reset_test_actions()

        assert events == [
            True,
            ("cleanup", "Earlier text", " dictated text", " after text"),
            False,
        ]

    def test_ai_cleanup_restores_ready_indicator_after_error(monkeypatch):
        events = []
        setting_values = {
            "user.dictation_ai_cleanup": True,
            "user.dictation_ai_cleanup_backend": "mlx",
            "user.dictation_ai_cleanup_model": "model",
            "user.dictation_ai_cleanup_port": 0,
            "user.dictation_ai_cleanup_timeout_s": 30,
        }
        monkeypatch.setattr(
            text_and_dictation.settings, "get", setting_values.__getitem__
        )

        def fail_cleanup(*args):
            events.append("cleanup")
            raise RuntimeError("cleanup failed")

        monkeypatch.setattr(text_and_dictation, "_run_ai_cleanup", fail_cleanup)
        talon.actions.register_test_action(
            "user",
            "dictation_mode_set_processing",
            lambda processing: events.append(processing),
        )
        text_and_dictation.utterance_insertions = [(" dictated text", "")]
        text_and_dictation.utterance_text_before = "Earlier text"
        text_and_dictation.utterance_text_after = ""
        text_and_dictation.utterance_had_dictation = True

        try:
            with pytest.raises(RuntimeError, match="cleanup failed"):
                text_and_dictation.on_post_phrase(None)
        finally:
            talon.actions.reset_test_actions()

        assert events == [True, "cleanup", False]

    def test_dictation_insert_reuses_spacing_peek_for_text_after(monkeypatch):
        peeks = []
        setting_values = {
            "user.context_sensitive_dictation": True,
            "user.dictation_ai_cleanup": False,
            "user.dictation_debug_mode": False,
            "user.peek_right_after_insertion": False,
        }
        monkeypatch.setattr(
            text_and_dictation.settings, "get", setting_values.__getitem__
        )
        talon.actions.register_test_action(
            "user",
            "dictation_peek",
            lambda left, right: peeks.append((left, right)) or ("Before", "after"),
        )
        talon.actions.register_test_action(
            "user", "add_phrase_to_history", lambda *args: None
        )
        talon.actions.register_test_action("user", "insert_between", lambda *args: None)
        text_and_dictation.dictation_formatter.reset()
        text_and_dictation.context_check_phrase_timestamp = None
        text_and_dictation.on_pre_phrase(None)

        try:
            text_and_dictation.Actions.dictation_insert("word")
        finally:
            talon.actions.reset_test_actions()

        assert peeks == [(True, True)]
        assert text_and_dictation.utterance_text_after == " after"

    def test_dictation_insert_reuses_post_insertion_peek_for_text_after(
        monkeypatch,
    ):
        peeks = []
        setting_values = {
            "user.context_sensitive_dictation": True,
            "user.dictation_ai_cleanup": False,
            "user.dictation_debug_mode": False,
            "user.peek_right_after_insertion": True,
        }
        monkeypatch.setattr(
            text_and_dictation.settings, "get", setting_values.__getitem__
        )
        monkeypatch.setattr(text_and_dictation.time, "sleep", lambda *args: None)

        def peek(left, right):
            peeks.append((left, right))
            return ("Before", None) if left else (None, "after")

        talon.actions.register_test_action("user", "dictation_peek", peek)
        talon.actions.register_test_action(
            "user", "add_phrase_to_history", lambda *args: None
        )
        talon.actions.register_test_action("user", "insert_between", lambda *args: None)
        text_and_dictation.dictation_formatter.reset()
        text_and_dictation.context_check_phrase_timestamp = None
        text_and_dictation.on_pre_phrase(None)

        try:
            text_and_dictation.Actions.dictation_insert("word")
        finally:
            talon.actions.reset_test_actions()

        assert peeks == [(True, False), (False, True)]
        assert text_and_dictation.utterance_text_after == " after"

    def test_ai_cleanup_peeks_both_sides_for_punctuation(monkeypatch):
        peeks = []
        setting_values = {
            "user.context_sensitive_dictation": True,
            "user.dictation_ai_cleanup": True,
            "user.dictation_debug_mode": False,
            "user.peek_right_after_insertion": False,
        }
        monkeypatch.setattr(
            text_and_dictation.settings, "get", setting_values.__getitem__
        )
        talon.actions.register_test_action(
            "user",
            "dictation_peek",
            lambda left, right: peeks.append((left, right)) or ("Before", "after"),
        )
        talon.actions.register_test_action(
            "user", "add_phrase_to_history", lambda *args: None
        )
        talon.actions.register_test_action("user", "insert_between", lambda *args: None)
        text_and_dictation.dictation_formatter.reset()
        text_and_dictation.context_check_phrase_timestamp = None
        text_and_dictation.on_pre_phrase(None)

        try:
            text_and_dictation.Actions.dictation_insert(".")
        finally:
            talon.actions.reset_test_actions()

        assert peeks == [(True, True)]
        assert text_and_dictation.utterance_text_before == "Before"
        assert text_and_dictation.utterance_text_after == " after"

    def test_ai_cleanup_reuses_boundary_context_for_multiple_insertions(monkeypatch):
        peeks = []
        setting_values = {
            "user.context_sensitive_dictation": True,
            "user.dictation_ai_cleanup": True,
            "user.dictation_debug_mode": False,
            "user.peek_right_after_insertion": False,
        }
        monkeypatch.setattr(
            text_and_dictation.settings, "get", setting_values.__getitem__
        )
        talon.actions.register_test_action(
            "user",
            "dictation_peek",
            lambda left, right: peeks.append((left, right)) or ("Before", "after"),
        )
        talon.actions.register_test_action(
            "user", "add_phrase_to_history", lambda *args: None
        )
        talon.actions.register_test_action("user", "insert_between", lambda *args: None)
        text_and_dictation.dictation_formatter.reset()
        text_and_dictation.context_check_phrase_timestamp = None
        text_and_dictation.on_pre_phrase(None)

        try:
            text_and_dictation.Actions.dictation_insert("first")
            text_and_dictation.Actions.dictation_insert("second")
        finally:
            talon.actions.reset_test_actions()

        assert peeks == [(True, True)]
        assert text_and_dictation.utterance_text_before == "Before"
        assert text_and_dictation.utterance_text_after == " after"

    def test_ai_cleanup_gets_right_context_after_insertion_when_configured(
        monkeypatch,
    ):
        peeks = []
        setting_values = {
            "user.context_sensitive_dictation": True,
            "user.dictation_ai_cleanup": True,
            "user.dictation_debug_mode": False,
            "user.peek_right_after_insertion": True,
        }
        monkeypatch.setattr(
            text_and_dictation.settings, "get", setting_values.__getitem__
        )
        monkeypatch.setattr(text_and_dictation.time, "sleep", lambda *args: None)

        def peek(left, right):
            peeks.append((left, right))
            return ("Before", None) if left else (None, "after")

        talon.actions.register_test_action("user", "dictation_peek", peek)
        talon.actions.register_test_action(
            "user", "add_phrase_to_history", lambda *args: None
        )
        talon.actions.register_test_action("user", "insert_between", lambda *args: None)
        text_and_dictation.dictation_formatter.reset()
        text_and_dictation.context_check_phrase_timestamp = None
        text_and_dictation.on_pre_phrase(None)

        try:
            text_and_dictation.Actions.dictation_insert(".")
        finally:
            talon.actions.reset_test_actions()

        assert peeks == [(True, False), (False, True)]
        assert text_and_dictation.utterance_text_before == "Before"
        assert text_and_dictation.utterance_text_after == " after"

    def test_prose_number_with_suffixes():
        assert text_and_dictation.prose_number(["numeral", "5", "K"]) == "5K"
        assert text_and_dictation.prose_number(["numeral", "2.5", "M"]) == "2.5M"
        assert (
            text_and_dictation.prose_number(["numb", "12", ":", "30", "B"]) == "12:30B"
        )

    def test_spacing_and_capitalization():
        format = text_and_dictation.DictationFormat()
        format.state = None
        result = format.format("first")
        assert result == "first"
        result = format.format("second.")
        assert result == " second."
        result = format.format("third(")
        assert result == " Third("
        result = format.format("fourth")
        assert result == "fourth"
        result = format.format("e.g.")
        assert result == " e.g."
        result = format.format("fifth")
        assert result == " fifth"
        result = format.format("i.e.")
        assert result == " i.e."
        result = format.format("sixth")
        assert result == " sixth"
        result = format.format("with.\nspace")
        assert result == " with.\nSpace"
        result = format.format("new.\nline")
        assert result == " new.\nLine"
        result = format.format("bullet\n* test")
        assert result == " bullet\n* Test"
        result = format.format("bullet\n* TODO test")
        assert result == " bullet\n* TODO Test"
        result = format.format("nbsp.\xa0space")
        assert result == " nbsp.\xa0Space"

    def test_capitalization_after_sentence_end_trailing_quote():
        for before in ['done."', "done.”"]:
            format = text_and_dictation.DictationFormat()
            format.update_context(before)
            assert format.format("a new sentence") == " A new sentence"

    def test_force_spacing_and_capitalization():
        format = text_and_dictation.DictationFormat()
        format.state = None
        format.force_capitalization = "cap"
        result = format.format("first")
        assert result == "First"
        format.force_no_space = True
        result = format.format("second.")
        assert result == "second."
        format.force_capitalization = "no cap"
        result = format.format("third(")
        assert result == " third("
        result = format.format("fourth")
        assert result == "fourth"

    def test_extract_ollama_response():
        payload = json.dumps(
            {
                "response": " corrected text\n",
                "prompt_eval_count": 50,
                "prompt_eval_duration": 500_000_000,
                "eval_count": 10,
                "eval_duration": 200_000_000,
                "total_duration": 900_000_000,
                "load_duration": 100_000_000,
            }
        ).encode("utf-8")
        response, _ = text_and_dictation._extract_ollama_response_and_perf(payload)
        assert response == " corrected text"

    def test_extract_ollama_response_perf():
        payload = json.dumps(
            {
                "response": " corrected text\n",
                "prompt_eval_count": 50,
                "prompt_eval_duration": 500_000_000,
                "eval_count": 10,
                "eval_duration": 200_000_000,
                "total_duration": 900_000_000,
                "load_duration": 100_000_000,
            }
        ).encode("utf-8")
        response, perf = text_and_dictation._extract_ollama_response_and_perf(
            payload, wall_ms=321.5
        )
        assert response == " corrected text"
        assert perf.backend == "ollama"
        assert perf.wall_ms == 321.5
        assert perf.prompt_tokens == 50
        assert perf.completion_tokens == 10
        assert perf.prefill_ms == 500.0
        assert perf.decode_ms == 200.0
        assert perf.total_ms == 900.0
        assert perf.load_ms == 100.0
        assert perf.prefill_tokens_per_second() == 100.0
        assert perf.decode_tokens_per_second() == 50.0

    def test_extract_ollama_response_trailing_nochange():
        payload = json.dumps(
            {
                "response": "some echoed text\nNOCHANGE\n",
                "prompt_eval_count": 50,
                "prompt_eval_duration": 500_000_000,
                "eval_count": 10,
                "eval_duration": 200_000_000,
                "total_duration": 900_000_000,
                "load_duration": 100_000_000,
            }
        ).encode("utf-8")
        response, _ = text_and_dictation._extract_ollama_response_and_perf(payload)
        assert response == "NOCHANGE"

    def test_extract_mlx_vlm_response():
        payload = json.dumps(
            {
                "choices": [
                    {"message": {"content": " corrected text\n"}},
                ],
                "usage": {
                    "input_tokens": 120,
                    "output_tokens": 8,
                    "total_tokens": 128,
                    "prompt_tps": 240.0,
                    "generation_tps": 40.0,
                    "peak_memory": 5.5,
                },
            }
        ).encode("utf-8")
        response, _ = text_and_dictation._extract_mlx_vlm_response_and_perf(payload)
        assert response == " corrected text"

    def test_extract_mlx_vlm_response_perf():
        payload = json.dumps(
            {
                "choices": [
                    {"message": {"content": " corrected text\n"}},
                ],
                "usage": {
                    "input_tokens": 120,
                    "output_tokens": 8,
                    "total_tokens": 128,
                    "prompt_tps": 240.0,
                    "generation_tps": 40.0,
                    "peak_memory": 5.5,
                },
            }
        ).encode("utf-8")
        response, perf = text_and_dictation._extract_mlx_vlm_response_and_perf(
            payload, wall_ms=222.0
        )
        assert response == " corrected text"
        assert perf.backend == "mlx"
        assert perf.wall_ms == 222.0
        assert perf.prompt_tokens == 120
        assert perf.completion_tokens == 8
        assert perf.cached_prompt_tokens is None
        assert perf.prefill_ms == 500.0
        assert perf.decode_ms == 200.0
        assert perf.prefill_tokens_per_second() == 240.0
        assert perf.decode_tokens_per_second() == 40.0
        assert perf.peak_memory_gb == 5.5

    def test_extract_mlx_vlm_response_content_blocks():
        payload = json.dumps(
            {
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"type": "output_text", "text": "some echoed text\n"},
                                {"type": "output_text", "text": "NOCHANGE\n"},
                            ]
                        }
                    },
                ],
                "usage": {
                    "input_tokens": 120,
                    "output_tokens": 8,
                    "total_tokens": 128,
                    "prompt_tps": 240.0,
                    "generation_tps": 40.0,
                    "peak_memory": 5.5,
                },
            }
        ).encode("utf-8")
        response, _ = text_and_dictation._extract_mlx_vlm_response_and_perf(payload)
        assert response == "NOCHANGE"

    def test_extract_mlx_vlm_response_openai_usage_shape():
        payload = json.dumps(
            {
                "choices": [
                    {"message": {"content": " corrected text\n"}},
                ],
                "usage": {
                    "prompt_tokens": 120,
                    "completion_tokens": 8,
                    "total_tokens": 128,
                    "prompt_tokens_details": {"cached_tokens": 9},
                },
                "timings": {
                    "prompt_ms": 500.0,
                    "prompt_per_second": 240.0,
                    "predicted_ms": 200.0,
                    "predicted_per_second": 40.0,
                    "peak_memory": 5.5,
                },
            }
        ).encode("utf-8")
        response, perf = text_and_dictation._extract_mlx_vlm_response_and_perf(
            payload, wall_ms=222.0
        )
        assert response == " corrected text"
        assert perf.backend == "mlx"
        assert perf.wall_ms == 222.0
        assert perf.prompt_tokens == 120
        assert perf.completion_tokens == 8
        assert perf.cached_prompt_tokens == 9
        assert perf.prefill_ms == 500.0
        assert perf.decode_ms == 200.0
        assert perf.prefill_tokens_per_second() == 240.0
        assert perf.decode_tokens_per_second() == 40.0
        assert perf.peak_memory_gb == 5.5

    def test_extract_mlx_vlm_response_openai_usage_shape_with_cached_prefix():
        payload = json.dumps(
            {
                "choices": [
                    {"message": {"content": " corrected text\n"}},
                ],
                "usage": {
                    "prompt_tokens": 370,
                    "completion_tokens": 13,
                    "total_tokens": 383,
                    "prompt_tokens_details": {"cached_tokens": 355},
                },
                "timings": {
                    "prompt_ms": 61.4,
                    "prompt_per_second": 244.1,
                    "predicted_ms": 119.4,
                    "predicted_per_second": 108.9,
                    "peak_memory": 16.31,
                },
            }
        ).encode("utf-8")
        response, perf = text_and_dictation._extract_mlx_vlm_response_and_perf(
            payload, wall_ms=354.8
        )
        assert response == " corrected text"
        assert perf.backend == "mlx"
        assert perf.wall_ms == 354.8
        assert perf.prompt_tokens == 370
        assert perf.cached_prompt_tokens == 355
        assert perf.completion_tokens == 13
        assert perf.prefill_ms == 61.4
        assert perf.decode_ms == 119.4
        assert perf.prefill_tokens_per_second() == 244.1
        assert perf.decode_tokens_per_second() == 108.9
        assert perf.peak_memory_gb == 16.31

    def test_log_ai_cleanup_perf_includes_server_call_and_client_prep(monkeypatch):
        perf = text_and_dictation.DictationAiCleanupPerf(
            backend="mlx",
            wall_ms=422.7,
            server_call_ms=401.2,
            client_prep_ms=21.5,
        )
        calls = []

        def fake_log(message, *args):
            calls.append(message % args)

        monkeypatch.setattr(text_and_dictation.logging, "debug", fake_log)

        text_and_dictation._log_ai_cleanup_perf(perf)

        assert calls == [
            "Dictation AI cleanup perf: backend=mlx wall=422.7ms "
            "server_call=401.2ms client_prep=21.5ms phase_rates=unavailable"
        ]

    def test_current_sentence_context_excludes_other_sentences_and_lines():
        text_before = text_and_dictation._current_sentence_text_before
        text_after = text_and_dictation._current_sentence_text_after

        assert text_before("The first sentence. Current fragment") == "Current fragment"
        assert text_before("Finished.") == ""
        assert text_before('Finished."  ') == ""
        assert text_before("Old line\nCurrent fragment") == "Current fragment"
        assert text_before("Old line\r\nCurrent fragment") == "Current fragment"
        assert text_before("Version 1.2 is ready") == "Version 1.2 is ready"

        assert text_after(" current fragment. Next sentence") == " current fragment."
        assert text_after(" current fragment\nNext line") == " current fragment"
        assert text_after(" current fragment\r\nNext line") == " current fragment"
        assert text_after(" version 1.2 is ready") == " version 1.2 is ready"

    def test_cleanup_prompt_requires_both_context_arguments():
        with pytest.raises(TypeError):
            text_and_dictation._cleanup_prompt("", "utterance")

    def test_run_ai_cleanup_preserves_input_spacing_but_normalizes_output_spacing(
        monkeypatch,
    ):
        request = {}

        class Response:
            content = json.dumps(
                {
                    "choices": [{"message": {"content": " -known issue"}}],
                    "usage": {},
                }
            ).encode("utf-8")

        def fake_post(url, **kwargs):
            request.update(kwargs)
            return Response()

        monkeypatch.setattr(text_and_dictation.requests, "post", fake_post)

        result = text_and_dictation._run_ai_cleanup(
            "This is a well",
            " known issue",
            " after deployment",
            "model",
            "http://127.0.0.1:8080/chat/completions",
            1,
            "mlx",
        )

        prompt = json.loads(request["data"])["messages"][0]["content"]
        assert "<utterance> known issue</utterance>" in prompt
        assert "<text_after> after deployment</text_after>" in prompt
        assert result == "-known issue"

        text_and_dictation._run_ai_cleanup(
            "An old sentence. This is a well",
            " known issue",
            "",
            "model",
            "http://127.0.0.1:8080/chat/completions",
            1,
            "mlx",
        )
        prompt = json.loads(request["data"])["messages"][0]["content"]
        assert "<text_before>This is a well</text_before>" in prompt
        assert "<text_after></text_after>" in prompt
        assert "An old sentence" not in prompt

    def test_run_ai_cleanup_logs_one_consolidated_result_line(monkeypatch):
        calls = []

        class Response:
            content = json.dumps(
                {
                    "choices": [{"message": {"content": "NOCHANGE"}}],
                    "usage": {},
                }
            ).encode("utf-8")

        monkeypatch.setattr(
            text_and_dictation.requests, "post", lambda *args, **kwargs: Response()
        )
        monkeypatch.setattr(
            text_and_dictation, "_log_ai_cleanup_perf", lambda *args: None
        )
        monkeypatch.setattr(
            text_and_dictation.logging,
            "debug",
            lambda message, *args: calls.append(message % args),
        )

        result = text_and_dictation._run_ai_cleanup(
            "Earlier text",
            " unchanged words",
            " after text",
            "model",
            "http://127.0.0.1:8080/chat/completions",
            1,
            "mlx",
        )

        assert result is None
        assert calls == [
            "Dictation AI cleanup: outcome=nochange text_before='Earlier text' "
            "utterance=' unchanged words' text_after=' after text' output='NOCHANGE'"
        ]

    def test_strip_ai_cleanup_output_guards_preserves_leading_comma():
        assert (
            text_and_dictation._strip_ai_cleanup_output_guards("\n, can you help\n")
            == ", can you help"
        )
        assert (
            text_and_dictation._strip_ai_cleanup_output_guards('"corrected text"')
            == "corrected text"
        )

    def test_ai_cleanup_edit_safety_is_structural():
        is_safe = text_and_dictation._is_safe_ai_cleanup_edit

        assert is_safe("rebase on maine", "rebase on main")
        assert is_safe("Plan a head:", "Plan ahead:")
        assert is_safe("That sounds all right", "That sounds alright")
        assert is_safe("That sounds alright", "That sounds all right")
        assert is_safe(
            "We should a lot two hours for testing",
            "We should allot two hours for testing",
        )
        assert is_safe("That takes allot of time", "That takes a lot of time")
        assert is_safe("I'm bit on the fence", "I'm a bit on the fence")
        assert is_safe("first come and second", "first, second")
        assert is_safe("Are you ready question mark", "Are you ready?")
        assert is_safe("That worked exclamation Marc", "That worked!")
        assert is_safe("client haven server", "client-server")
        assert is_safe("client high fin server", "client-server")
        assert is_safe("a well known issue", "a well-known issue")
        assert is_safe("state of the art model", "state-of-the-art model")
        assert is_safe("ask michael", "ask Michael")
        assert is_safe("The cache lost it's state", "The cache lost its state")
        assert not is_safe("red green and blue", "red, green and blue")
        assert not is_safe("green and blue", ", green and blue")
        assert not is_safe("she has it covered on", "she has it covered")
        assert not is_safe("I'm not sure come and can you help", ", can you help")
        assert not is_safe("I don't know", "? I don't know")
        assert not is_safe("Ask Danise", "Ask Denise")
        assert not is_safe("Ask Sponge Bob", "Ask SpongeBob")
        assert not is_safe("ask Sponge", "ask sponge")
        assert not is_safe("I'm bit unsure", "I'm maybe a bit unsure")
        assert not is_safe("I have a question", "I have a?")
        assert not is_safe("That was an exclamation", "That was an!")
        assert not is_safe("Plan a head:", "Plan ahead")
        assert not is_safe("cached and uncached)", "cached and uncached")
        assert not is_safe("keep this, exactly", "keep this exactly")

    def test_run_ai_cleanup_handles_requests_failure(monkeypatch):
        def raise_timeout(*args, **kwargs):
            raise text_and_dictation.requests.exceptions.Timeout("too slow")

        monkeypatch.setattr(text_and_dictation.requests, "post", raise_timeout)

        assert (
            text_and_dictation._run_ai_cleanup(
                "",
                "apples comment oranges",
                "",
                "model",
                "http://127.0.0.1:8080/chat/completions",
                1,
                "mlx",
            )
            is None
        )

    def test_run_ai_cleanup_sets_ollama_temperature_to_zero(monkeypatch):
        request = {}

        class Response:
            content = json.dumps(
                {
                    "response": "apples, oranges",
                    "prompt_eval_count": 10,
                    "prompt_eval_duration": 100_000_000,
                    "eval_count": 2,
                    "eval_duration": 20_000_000,
                    "total_duration": 150_000_000,
                    "load_duration": 10_000_000,
                }
            ).encode("utf-8")

        def fake_post(url, **kwargs):
            request.update(kwargs)
            return Response()

        monkeypatch.setattr(text_and_dictation.requests, "post", fake_post)

        result = text_and_dictation._run_ai_cleanup(
            "",
            "apples comment oranges",
            "",
            "model",
            "http://127.0.0.1:11434/api/generate",
            1,
            "ollama",
        )

        assert result == "apples, oranges"
        assert json.loads(request["data"])["options"] == {"temperature": 0.0}
