import asyncio

from memory_bench.artifacts import ArtifactWriter
from memory_bench.contracts import (
    AssertionSpec,
    Case,
    Operation,
    Principal,
    SearchHit,
    SearchResult,
    Status,
    Track,
)
from memory_bench.runner import _run_case


PRINCIPAL = Principal(id="p1", tenant_id="t", owner_user_id="U1", agent_id="email_agent", domain_id="email")

CASE = Case(
    id="F02",
    group="fact",
    title="默认技术语言",
    operations=[
        Operation(
            op="search",
            request_id="f02-q1",
            principal_id="p1",
            query="技术方案默认使用什么语言？",
            assertions=AssertionSpec(required_tokens=["Python"]),
        )
    ],
)


def make_config(**overrides):
    config = {
        "top_k": 5,
        "visibility_deadline_seconds": 30,
        "poll_intervals_seconds": [0, 0, 0],
        "max_poll_attempts": 5,
        "tracks": {"r0": {"candidate_pool_k": 5, "final_top_k": 5}},
    }
    config.update(overrides)
    return config


class FlakyAdapter:
    """Returns empty hits for the first `empty_attempts` searches."""

    def __init__(self, empty_attempts: int) -> None:
        self.empty_attempts = empty_attempts
        self.calls = 0

    async def search(self, request, principal):
        self.calls += 1
        if self.calls <= self.empty_attempts:
            return SearchResult(request_id=request.request_id, status=Status.PASS, hits=[], elapsed_ms=1)
        hit = SearchHit(native_id="n1", text="技术方案默认使用 Python。", observed_at="2026-09-14T00:00:00+00:00")
        return SearchResult(request_id=request.request_id, status=Status.PASS, hits=[hit], elapsed_ms=1)


class ErrorAdapter:
    """Search transport keeps failing; polling must not mask it."""

    def __init__(self) -> None:
        self.calls = 0

    async def search(self, request, principal):
        self.calls += 1
        return SearchResult(request_id=request.request_id, status=Status.FAIL, hits=[], elapsed_ms=1, error="boom")


class TransientErrorAdapter:
    """First search fails transiently, then returns the expected hit."""

    def __init__(self) -> None:
        self.calls = 0

    async def search(self, request, principal):
        self.calls += 1
        if self.calls == 1:
            return SearchResult(request_id=request.request_id, status=Status.FAIL, hits=[], elapsed_ms=1, error="Error code: 400")
        hit = SearchHit(native_id="n1", text="技术方案默认使用 Python。", observed_at="2026-09-15T00:00:00+00:00")
        return SearchResult(request_id=request.request_id, status=Status.PASS, hits=[hit], elapsed_ms=1)


def run_case(adapter, tmp_path, config):
    writer = ArtifactWriter(tmp_path, "test-run")
    return asyncio.run(
        _run_case(
            adapter,
            CASE,
            {"p1": PRINCIPAL},
            namespace="ns",
            config=config,
            track=Track.R0,
            writer=writer,
        )
    )


def test_polls_until_memory_visible(tmp_path):
    adapter = FlakyAdapter(empty_attempts=2)
    result = run_case(adapter, tmp_path, make_config())
    assert result["status"] == Status.PASS
    assert adapter.calls == 3
    assert result["operations"][0]["attempts"] == 3


def test_fail_only_after_poll_budget_exhausted(tmp_path):
    adapter = FlakyAdapter(empty_attempts=99)
    result = run_case(adapter, tmp_path, make_config(max_poll_attempts=3))
    assert result["status"] == Status.FAIL
    assert adapter.calls == 3


def test_polling_disabled_without_deadline(tmp_path):
    adapter = FlakyAdapter(empty_attempts=99)
    result = run_case(adapter, tmp_path, make_config(visibility_deadline_seconds=0))
    assert result["status"] == Status.FAIL
    assert adapter.calls == 1


def test_transport_failure_is_not_polled(tmp_path):
    adapter = ErrorAdapter()
    result = run_case(adapter, tmp_path, make_config())
    assert result["status"] == Status.FAIL
    assert adapter.calls == 1


def test_transient_transport_error_is_retried(tmp_path):
    adapter = TransientErrorAdapter()
    result = run_case(adapter, tmp_path, make_config(max_transport_retries=1))
    assert result["status"] == Status.PASS
    assert adapter.calls == 2
    assert result["operations"][0]["attempts"] == 1


def test_persistent_transport_failure_respects_retry_budget(tmp_path):
    adapter = ErrorAdapter()
    result = run_case(adapter, tmp_path, make_config(max_transport_retries=1))
    assert result["status"] == Status.FAIL
    assert adapter.calls == 2
    assert result["operations"][0]["attempts"] == 1
