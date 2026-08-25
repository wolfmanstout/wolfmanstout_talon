import json

import talon

PHRASE_EXAMPLES = ["", "foo", "foo bar", "lorem ipsum dolor sit amet"]

if hasattr(talon, "test_mode"):
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

    def test_current_sentence_fragment_excludes_previous_sentences_and_lines():
        fragment = text_and_dictation._current_sentence_fragment

        assert fragment("The first sentence. Current fragment") == "Current fragment"
        assert fragment("Finished.") == ""
        assert fragment('Finished."  ') == ""
        assert fragment("Old line\nCurrent fragment") == "Current fragment"
        assert fragment("Old line\r\nCurrent fragment") == "Current fragment"
        assert fragment("Version 1.2 is ready") == "Version 1.2 is ready"

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
            "model",
            "http://127.0.0.1:8080/chat/completions",
            1,
            "mlx",
        )

        prompt = json.loads(request["data"])["messages"][0]["content"]
        assert "<utterance> known issue</utterance>" in prompt
        assert result == "-known issue"

        text_and_dictation._run_ai_cleanup(
            "An old sentence. This is a well",
            " known issue",
            "model",
            "http://127.0.0.1:8080/chat/completions",
            1,
            "mlx",
        )
        prompt = json.loads(request["data"])["messages"][0]["content"]
        assert "<text_before>This is a well</text_before>" in prompt
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
            "model",
            "http://127.0.0.1:8080/chat/completions",
            1,
            "mlx",
        )

        assert result is None
        assert calls == [
            "Dictation AI cleanup: outcome=nochange text_before='Earlier text' "
            "input=' unchanged words' output='NOCHANGE'"
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
            "model",
            "http://127.0.0.1:11434/api/generate",
            1,
            "ollama",
        )

        assert result == "apples, oranges"
        assert json.loads(request["data"])["options"] == {"temperature": 0.0}
