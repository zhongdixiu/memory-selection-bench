import pytest

from memory_bench.config import load_dotenv


def test_loads_key_value_pairs(tmp_path, monkeypatch):
    monkeypatch.delenv("BENCH_TEST_KEY", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text("BENCH_TEST_KEY=value\n", encoding="utf-8")
    assert load_dotenv(env_file) == ["BENCH_TEST_KEY"]
    import os

    assert os.environ["BENCH_TEST_KEY"] == "value"


def test_existing_environment_wins(tmp_path, monkeypatch):
    monkeypatch.setenv("BENCH_TEST_KEY", "from-shell")
    env_file = tmp_path / ".env"
    env_file.write_text("BENCH_TEST_KEY=from-file\n", encoding="utf-8")
    assert load_dotenv(env_file) == []
    import os

    assert os.environ["BENCH_TEST_KEY"] == "from-shell"


def test_skips_comments_blank_and_malformed_lines(tmp_path, monkeypatch):
    monkeypatch.delenv("BENCH_TEST_A", raising=False)
    monkeypatch.delenv("BENCH_TEST_B", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# comment\n\n  \nno_equals_line\nBENCH_TEST_A=1\nexport BENCH_TEST_B=2\n",
        encoding="utf-8",
    )
    import os

    assert load_dotenv(env_file) == ["BENCH_TEST_A", "BENCH_TEST_B"]
    assert os.environ["BENCH_TEST_A"] == "1"
    assert os.environ["BENCH_TEST_B"] == "2"


def test_strips_matching_quotes_and_whitespace(tmp_path, monkeypatch):
    monkeypatch.delenv("BENCH_TEST_Q1", raising=False)
    monkeypatch.delenv("BENCH_TEST_Q2", raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "BENCH_TEST_Q1 = 'single quoted' \nBENCH_TEST_Q2=\"double quoted\"\n",
        encoding="utf-8",
    )
    import os

    load_dotenv(env_file)
    assert os.environ["BENCH_TEST_Q1"] == "single quoted"
    assert os.environ["BENCH_TEST_Q2"] == "double quoted"


def test_missing_file_returns_empty(tmp_path):
    assert load_dotenv(tmp_path / "does-not-exist.env") == []
