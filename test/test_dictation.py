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

    def test_strip_ai_cleanup_output_guards_preserves_leading_comma():
        assert (
            text_and_dictation._strip_ai_cleanup_output_guards("\n, can you help\n")
            == ", can you help"
        )
        assert (
            text_and_dictation._strip_ai_cleanup_output_guards('"corrected text"')
            == "corrected text"
        )

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
