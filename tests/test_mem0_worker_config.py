from pathlib import Path

from memory_bench.adapters.mem0_worker import LANGUAGE_ALIGNMENT_INSTRUCTIONS, _worker_config


def _set_env(monkeypatch):
    monkeypatch.setenv("MEMORY_BENCH_LLM_MODEL", "qwen-test")
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-llm-key")
    monkeypatch.setenv("MEMORY_BENCH_LLM_BASE_URL", "https://example.invalid/llm")
    monkeypatch.setenv("MEMORY_BENCH_EMBED_MODEL", "BAAI/bge-m3")
    monkeypatch.setenv("SILICONFLOW_API_KEY", "test-embed-key")
    monkeypatch.setenv("MEMORY_BENCH_EMBED_BASE_URL", "https://example.invalid/embed")


def test_config_pins_unified_models_and_dims(monkeypatch):
    _set_env(monkeypatch)
    config = _worker_config(Path("/tmp/runtime-x"))
    assert config["version"] == "v1.1"
    assert config["llm"]["config"]["model"] == "qwen-test"
    assert config["llm"]["config"]["temperature"] == 0.0
    assert config["embedder"]["config"]["model"] == "BAAI/bge-m3"
    assert config["embedder"]["config"]["embedding_dims"] == 1024
    assert config["vector_store"]["config"]["embedding_model_dims"] == 1024
    assert config["vector_store"]["config"]["path"] == "/tmp/runtime-x/qdrant"
    assert config["history_db_path"] == "/tmp/runtime-x/history.db"


def test_language_alignment_uses_official_custom_instructions_port(monkeypatch):
    _set_env(monkeypatch)
    config = _worker_config(Path("/tmp/runtime-x"))
    instructions = config["custom_instructions"]
    assert instructions == LANGUAGE_ALIGNMENT_INSTRUCTIONS
    # shim 的两个关键点：保持输入语言输出、明确禁止改写成英文
    assert "SAME LANGUAGE" in instructions
    assert "Do NOT translate" in instructions
