from memory_bench.artifacts import redact


def test_redaction_preserves_assertion_tokens_but_hides_credentials():
    value = redact({"required_tokens": ["Python"], "api_key": "secret-value", "access_token": "secret-token"})
    assert value["required_tokens"] == ["Python"]
    assert value["api_key"] == "<redacted>"
    assert value["access_token"] == "<redacted>"
