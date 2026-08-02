import json

import talon

if hasattr(talon, "test_mode"):
    from apps.emacs import emacs

    def response(**overrides):
        value = {
            "type": emacs.DICTATION_PEEK_RESPONSE_TYPE,
            "version": emacs.DICTATION_PEEK_PROTOCOL_VERSION,
            "requestId": "request-1",
            "ok": True,
            "before": "before λ",
            "after": " after\nline",
        }
        value.update(overrides)
        return json.dumps(value)

    def test_parse_dictation_peek_response():
        assert emacs._parse_dictation_peek_response(
            response(), "request-1", True, True
        ) == ("before λ", " after\nline")
        assert emacs._parse_dictation_peek_response(
            response(before=None), "request-1", False, True
        ) == (None, " after\nline")
        assert emacs._parse_dictation_peek_response(
            response(after=None), "request-1", True, False
        ) == ("before λ", None)

    def test_parse_dictation_peek_response_rejects_bad_envelopes():
        bad_responses = [
            "not json",
            json.dumps([]),
            response(type="other"),
            response(version=2),
            response(requestId="other"),
            response(ok=False, error="Emacs failed"),
            response(before=None),
            response(after=42),
        ]
        for raw_text in bad_responses:
            try:
                emacs._parse_dictation_peek_response(raw_text, "request-1", True, True)
            except emacs.DictationPeekProtocolError:
                pass
            else:
                raise AssertionError(f"Accepted invalid response: {raw_text}")

    def test_parse_dictation_peek_response_rejects_unrequested_context():
        cases = [
            (response(before="unexpected"), False, True),
            (response(after="unexpected"), True, False),
        ]
        for raw_text, left, right in cases:
            try:
                emacs._parse_dictation_peek_response(raw_text, "request-1", left, right)
            except emacs.DictationPeekProtocolError:
                pass
            else:
                raise AssertionError(f"Accepted unrequested context: {raw_text}")

    def test_identifies_only_matching_dictation_peek_responses():
        assert emacs._is_dictation_peek_response_for_request(response(), "request-1")
        assert not emacs._is_dictation_peek_response_for_request(
            response(requestId="stale"), "request-1"
        )
        assert not emacs._is_dictation_peek_response_for_request(
            "not json", "request-1"
        )
