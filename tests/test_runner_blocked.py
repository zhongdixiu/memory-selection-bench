import asyncio

from memory_bench.config import load_bench_config
from memory_bench.contracts import Status, Track
from memory_bench.runner import run_benchmark


def test_missing_secrets_produce_a_blocked_artifact(tmp_path, monkeypatch):
    monkeypatch.delenv("DASHSCOPE_API_KEY", raising=False)
    monkeypatch.delenv("SILICONFLOW_API_KEY", raising=False)
    run_id, manifest = asyncio.run(
        run_benchmark(
            config=load_bench_config(),
            candidate="mem0",
            track=Track.R0,
            suite="smoke",
            artifacts_root=tmp_path,
        )
    )
    assert manifest["status"] == Status.BLOCKED
    assert "DASHSCOPE_API_KEY" in manifest["error"]
    assert (tmp_path / run_id / "manifest.json").exists()
