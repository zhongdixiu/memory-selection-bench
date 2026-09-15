from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import httpx


def _endpoint(base_url: str, suffix: str) -> str:
    return f"{base_url.rstrip('/')}/{suffix.lstrip('/')}"


def environment_checks(config: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for name, path in config["paths"].items():
        exists = Path(path).exists()
        checks.append({"kind": "path", "name": name, "target": path, "ok": exists})
    seen: set[str] = set()
    for provider in ("llm", "embedding", "rerank"):
        env_name = config["providers"][provider]["api_key_env"]
        if env_name in seen:
            continue
        seen.add(env_name)
        checks.append(
            {
                "kind": "secret",
                "name": env_name,
                "target": env_name,
                "ok": bool(os.getenv(env_name, "").strip()),
            }
        )
    return checks


async def live_provider_checks(config: dict[str, Any]) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    timeout = config["request_timeout_seconds"]
    async with httpx.AsyncClient(timeout=timeout) as client:
        llm = config["providers"]["llm"]
        llm_started = time.perf_counter()
        try:
            response = await client.post(
                _endpoint(llm["base_url"], "chat/completions"),
                headers={"Authorization": f"Bearer {os.environ[llm['api_key_env']]}"},
                json={
                    "model": llm["model"],
                    "messages": [{"role": "user", "content": "仅回复 OK"}],
                    "temperature": llm["temperature"],
                    "max_tokens": 16,
                    "enable_thinking": False,
                },
            )
            response.raise_for_status()
            body = response.json()
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
            checks.append({"kind": "live", "name": "llm", "ok": bool(content), "status_code": response.status_code, "elapsed_ms": int((time.perf_counter() - llm_started) * 1000)})
        except Exception as exc:
            checks.append({"kind": "live", "name": "llm", "ok": False, "error": str(exc), "elapsed_ms": int((time.perf_counter() - llm_started) * 1000)})

        embedding = config["providers"]["embedding"]
        embed_started = time.perf_counter()
        try:
            response = await client.post(
                _endpoint(embedding["base_url"], "embeddings"),
                headers={"Authorization": f"Bearer {os.environ[embedding['api_key_env']]}"},
                json={"model": embedding["model"], "input": ["memory benchmark dimension probe"]},
            )
            response.raise_for_status()
            vector = response.json().get("data", [{}])[0].get("embedding", [])
            expected = int(embedding["dimensions"])
            checks.append({"kind": "live", "name": "embedding", "ok": len(vector) == expected, "dimensions": len(vector), "expected_dimensions": expected, "status_code": response.status_code, "elapsed_ms": int((time.perf_counter() - embed_started) * 1000)})
        except Exception as exc:
            checks.append({"kind": "live", "name": "embedding", "ok": False, "error": str(exc), "elapsed_ms": int((time.perf_counter() - embed_started) * 1000)})

        rerank = config["providers"]["rerank"]
        rerank_started = time.perf_counter()
        try:
            response = await client.post(
                _endpoint(rerank["base_url"], "rerank"),
                headers={"Authorization": f"Bearer {os.environ[rerank['api_key_env']]}"},
                json={"model": rerank["model"], "query": "首选 Python", "documents": ["默认使用 Java", "技术方案默认使用 Python"], "top_n": 2},
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            valid = bool(results) and all("index" in item and "relevance_score" in item for item in results)
            checks.append({"kind": "live", "name": "rerank", "ok": valid, "result_count": len(results), "status_code": response.status_code, "elapsed_ms": int((time.perf_counter() - rerank_started) * 1000)})
        except Exception as exc:
            checks.append({"kind": "live", "name": "rerank", "ok": False, "error": str(exc), "elapsed_ms": int((time.perf_counter() - rerank_started) * 1000)})
    return checks
