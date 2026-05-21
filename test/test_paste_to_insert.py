import talon

if hasattr(talon, "test_mode"):
    from plugin.paste_to_insert import (
        should_paste_to_insert,
        split_surrounding_horizontal_whitespace,
    )

    def test_should_paste_to_insert_respects_threshold():
        assert should_paste_to_insert("hello world", 10, True)
        assert not should_paste_to_insert("hello", 10, True)
        assert not should_paste_to_insert("hello world", -1, True)

    def test_should_paste_to_insert_pastes_newlines_when_enabled():
        assert should_paste_to_insert("hello\n", 10, True)
        assert not should_paste_to_insert("hello\n", 10, False)

    def test_should_paste_to_insert_ignores_surrounding_horizontal_whitespace():
        assert should_paste_to_insert(" hello world ", 10, True)
        assert not should_paste_to_insert(" hello ", 10, True)
        assert should_paste_to_insert(" hello\n", 10, True)

    def test_split_surrounding_horizontal_whitespace():
        assert split_surrounding_horizontal_whitespace(" hello world ") == (
            " ",
            "hello world",
            " ",
        )
        assert split_surrounding_horizontal_whitespace("\nhello\n") == (
            "",
            "\nhello\n",
            "",
        )
