import talon

PHRASE_EXAMPLES = ["", "foo", "foo bar", "lorem ipsum dolor sit amet"]

if hasattr(talon, "test_mode"):
    import pytest

    # Only include this when we're running tests
    from core.text import dictation_ai_cleanup, text_and_dictation

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
            dictation_ai_cleanup,
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

        monkeypatch.setattr(dictation_ai_cleanup, "_run_ai_cleanup", fail_cleanup)
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

    @pytest.mark.parametrize("suffix", ["", ")"])
    def test_ai_cleanup_rewrites_phrase_and_restores_formatter(monkeypatch, suffix):
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

        def cleanup(before, utterance, after, model, url, timeout, backend):
            assert (before, utterance, after) == (
                "Before",
                " first comment second",
                " after",
            )
            assert (model, url, timeout, backend) == (
                "model",
                "http://127.0.0.1:8080/chat/completions",
                30,
                "mlx",
            )
            return " first, second"

        monkeypatch.setattr(dictation_ai_cleanup, "_run_ai_cleanup", cleanup)
        monkeypatch.setattr(
            text_and_dictation.dictation_formatter,
            "update_context",
            lambda text: events.append(("context", text)),
        )
        monkeypatch.setattr(
            text_and_dictation.dictation_formatter,
            "pass_through",
            lambda text: events.append(("formatter", text)),
        )
        for namespace, name in [
            ("user", "dictation_mode_set_processing"),
            ("user", "clear_last_phrase"),
            ("user", "insert_between"),
            ("user", "add_phrase_to_history"),
            ("", "insert"),
        ]:
            talon.actions.register_test_action(
                namespace, name, lambda *args, name=name: events.append((name, *args))
            )
        text_and_dictation.on_pre_phrase(None)
        text_and_dictation.utterance_insertions = [
            (" first comment", suffix),
            (" second", ""),
        ]
        text_and_dictation.utterance_text_before = "Before"
        text_and_dictation.utterance_text_after = " after"
        text_and_dictation.utterance_had_dictation = True
        try:
            text_and_dictation.on_post_phrase(None)
        finally:
            talon.actions.reset_test_actions()

        insertion = (
            ("insert_between", " first, second", suffix)
            if suffix
            else ("insert", " first, second")
        )
        assert events == [
            ("dictation_mode_set_processing", True),
            ("clear_last_phrase",),
            ("clear_last_phrase",),
            insertion,
            ("add_phrase_to_history", " first, second", suffix),
            ("dictation_mode_set_processing", False),
            ("context", "Before"),
            ("formatter", " first, second"),
        ]
        assert text_and_dictation.utterance_insertions == []
        assert text_and_dictation.phrase_timestamp is None

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
