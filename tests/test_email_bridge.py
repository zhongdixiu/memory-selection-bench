import asyncio

from memory_bench.cases import load_principals
from memory_bench.config import PROJECT_ROOT, load_bench_config
from memory_bench.contracts import SearchHit, SearchResult, Status, Track, WriteReceipt
from memory_bench.email_integration import EmailMemoryBridge


class FakeAdapter:
    candidate = "fake"

    async def search(self, request, principal):
        return SearchResult(request_id=request.request_id, status=Status.PASS, elapsed_ms=1, hits=[SearchHit(native_id="m1", text="P1 先接 Email Agent", score=0.8, source_refs=["source-m1"], observed_at="2026-09-14T00:00:00Z")])

    async def write(self, request, principal):
        return WriteReceipt(request_id=request.request_id, status=Status.PASS, accepted=True, processed=True, received_at="2026-09-14T00:00:00Z", elapsed_ms=1)


def test_email_bridge_binds_session_to_server_side_principal():
    async def run():
        bridge = EmailMemoryBridge(adapter=FakeAdapter(), config=load_bench_config(), track=Track.R0, namespace="ns")
        bridge.bind_session("s1", "principal_u1_mail")
        result = await bridge.search_context(session_id="s1", query="P1")
        return bridge, result

    bridge, result = asyncio.run(run())
    assert "Email Agent" in result
    assert bridge.search_events[0]["request"]["principal_id"] == "principal_u1_mail"


def test_email_bridge_disabled_mode_does_not_search():
    async def run():
        bridge = EmailMemoryBridge(adapter=FakeAdapter(), config=load_bench_config(), track=Track.R0, namespace="ns", enabled=False)
        bridge.bind_session("s1")
        result = await bridge.search_context(session_id="s1", query="q")
        return bridge, result

    bridge, result = asyncio.run(run())
    assert result == ""
    assert bridge.search_events == []
