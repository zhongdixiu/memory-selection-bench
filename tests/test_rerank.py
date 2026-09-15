import asyncio

import httpx

from memory_bench.config import load_bench_config
from memory_bench.contracts import SearchHit, SearchResult, Status
from memory_bench.rerank import rerank_result


def test_common_rerank_reorders_and_preserves_dense_score(monkeypatch):
    monkeypatch.setenv("SILICONFLOW_API_KEY", "test-only")

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/rerank"
        return httpx.Response(200, json={"results": [{"index": 1, "relevance_score": 0.9}, {"index": 0, "relevance_score": 0.2}]})

    async def run():
        client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        result = SearchResult(
            request_id="q1", status=Status.PASS, elapsed_ms=2,
            hits=[
                SearchHit(native_id="a", text="A", score=0.8, observed_at="2026-09-14T00:00:00Z"),
                SearchHit(native_id="b", text="B", score=0.7, observed_at="2026-09-14T00:00:00Z"),
            ],
        )
        output = await rerank_result(result, query="B", config=load_bench_config(), final_top_k=2, client=client)
        await client.aclose()
        return output

    output = asyncio.run(run())
    assert [item.native_id for item in output.hits] == ["b", "a"]
    assert output.hits[0].native_metadata["dense_score"] == 0.7
    assert output.rerank_applied is True
