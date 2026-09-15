from __future__ import annotations

import os
import time
from typing import Any

import httpx

from .contracts import SearchHit, SearchResult, Status


async def rerank_result(
    result: SearchResult,
    *,
    query: str,
    config: dict[str, Any],
    final_top_k: int,
    client: httpx.AsyncClient | None = None,
) -> SearchResult:
    result.rerank_configured = True
    result.rerank_requested = True
    if result.status != Status.PASS or not result.hits:
        return result
    provider = config["providers"]["rerank"]
    own_client = client is None
    http = client or httpx.AsyncClient(timeout=config["request_timeout_seconds"])
    started = time.perf_counter()
    try:
        response = await http.post(
            f"{provider['base_url'].rstrip('/')}/rerank",
            headers={"Authorization": f"Bearer {os.environ[provider['api_key_env']]}"},
            json={
                "model": provider["model"],
                "query": query,
                "documents": [item.text for item in result.hits],
                "top_n": min(final_top_k, len(result.hits)),
            },
        )
        response.raise_for_status()
        body = response.json()
        ranked: list[SearchHit] = []
        seen: set[int] = set()
        for item in body.get("results", []):
            index = int(item["index"])
            if index < 0 or index >= len(result.hits) or index in seen:
                raise ValueError(f"invalid rerank index: {index}")
            seen.add(index)
            hit = result.hits[index].model_copy(deep=True)
            hit.native_metadata["dense_score"] = hit.score
            hit.score = float(item["relevance_score"])
            ranked.append(hit)
        if not ranked:
            raise ValueError("rerank response has no results")
        result.hits = ranked
        result.rerank_applied = True
        result.elapsed_ms += int((time.perf_counter() - started) * 1000)
        result.raw = {"dense": result.raw, "rerank": {"result_count": len(ranked)}}
        return result
    except httpx.TimeoutException:
        result.status = Status.TIMEOUT
        result.error = "common rerank timeout"
        return result
    except Exception as exc:
        result.status = Status.FAIL
        result.error = f"common rerank failed: {exc}"
        return result
    finally:
        if own_client:
            await http.aclose()
