from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from memory_bench.contracts import Principal, SearchHit, SearchRequest, SearchResult, Status, Track, WriteReceipt, WriteRequest


PREFIX = "@@MEMORY_BENCH@@"


class Mem0Adapter:
    candidate = "mem0"

    def __init__(self, *, config: dict[str, Any], runtime_dir: Path, track: Track) -> None:
        self.config = config
        self.runtime_dir = runtime_dir
        self.track = track
        self.process: asyncio.subprocess.Process | None = None
        self.stderr_lines: list[str] = []
        self._stderr_task: asyncio.Task | None = None

    async def start(self) -> None:
        paths = self.config["paths"]
        providers = self.config["providers"]
        env = os.environ.copy()
        # The host exports a SOCKS all_proxy while this candidate venv does not
        # include socksio. Keep the explicit HTTP(S) proxies and remove only the
        # lower-priority SOCKS fallback so client construction remains valid.
        env.pop("all_proxy", None)
        env.pop("ALL_PROXY", None)
        env.update(
            {
                "PYTHONPATH": f"{Path(__file__).resolve().parents[2]}:{paths['mem0_root']}",
                "MEMORY_BENCH_RUNTIME_DIR": str(self.runtime_dir),
                "MEMORY_BENCH_LLM_MODEL": providers["llm"]["model"],
                "MEMORY_BENCH_LLM_BASE_URL": providers["llm"]["base_url"],
                "MEMORY_BENCH_EMBED_MODEL": providers["embedding"]["model"],
                "MEMORY_BENCH_EMBED_BASE_URL": providers["embedding"]["base_url"],
                "MEM0_TELEMETRY": "false",
            }
        )
        self.process = await asyncio.create_subprocess_exec(
            paths["mem0_python"],
            "-m",
            "memory_bench.adapters.mem0_worker",
            cwd=paths["mem0_root"],
            env=env,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self._stderr_task = asyncio.create_task(self._drain_stderr())
        ready = await self._read_response(timeout=120)
        if not ready.get("ok") or not ready.get("ready"):
            raise RuntimeError(f"Mem0 worker failed to start: {ready.get('error')}")

    async def _drain_stderr(self) -> None:
        assert self.process and self.process.stderr
        while line := await self.process.stderr.readline():
            self.stderr_lines.append(line.decode("utf-8", errors="replace").rstrip())
            self.stderr_lines = self.stderr_lines[-500:]

    async def _read_response(self, timeout: float) -> dict[str, Any]:
        assert self.process and self.process.stdout

        async def read() -> dict[str, Any]:
            while line := await self.process.stdout.readline():
                text = line.decode("utf-8", errors="replace").strip()
                if text.startswith(PREFIX):
                    return json.loads(text[len(PREFIX) :])
            raise RuntimeError(f"Mem0 worker exited; stderr tail: {self.stderr_lines[-10:]}")

        return await asyncio.wait_for(read(), timeout=timeout)

    async def _call(self, command: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        assert self.process and self.process.stdin
        body = json.dumps({"command": command, "payload": payload or {}}, ensure_ascii=False) + "\n"
        self.process.stdin.write(body.encode("utf-8"))
        await self.process.stdin.drain()
        response = await self._read_response(self.config["request_timeout_seconds"])
        if not response.get("ok"):
            raise RuntimeError(response.get("error") or "Mem0 worker error")
        return response.get("data") or {}

    async def close(self) -> None:
        if not self.process:
            return
        try:
            await self._call("close")
        except Exception:
            self.process.terminate()
        try:
            await asyncio.wait_for(self.process.wait(), timeout=10)
        except asyncio.TimeoutError:
            self.process.kill()
            await self.process.wait()
        if self._stderr_task:
            await self._stderr_task

    async def health(self) -> dict:
        return await self._call("health")

    @staticmethod
    def _base_metadata(request: WriteRequest, principal: Principal) -> dict[str, Any]:
        return {
            "bench_namespace": request.namespace,
            "tenant_id": principal.tenant_id,
            "scope_kind": request.requested_scope.kind,
            "scope_id": request.requested_scope.scope_id,
            "project_id": request.requested_scope.project_id,
            "source_agent_id": request.source_agent_id,
            "source_domain_id": request.source_domain_id,
            "source_session_id": request.source_session_id,
            "source_id": request.source_id,
            "source_message_ids": [item.message_id for item in request.messages],
            "source_occurred_at": max(item.occurred_at for item in request.messages),
        }

    def _filter_sets(self, namespace: str, principal: Principal) -> list[dict[str, Any]]:
        if not principal.owner_user_id:
            return []
        base = {"user_id": principal.owner_user_id, "bench_namespace": namespace}
        if self.track == Track.P_NATIVE:
            return [base]
        filters = [
            {**base, "scope_kind": "user_public", "scope_id": principal.owner_user_id},
            {**base, "scope_kind": "domain", "scope_id": principal.domain_id},
        ]
        filters.extend({**base, "scope_kind": "project", "scope_id": project} for project in principal.allowed_projects)
        filters.extend(
            {**base, "scope_kind": "agent_private", "scope_id": agent}
            for agent in principal.allowed_agent_private
        )
        return filters

    async def write(self, request: WriteRequest, principal: Principal) -> WriteReceipt:
        started = time.perf_counter()
        now = datetime.now(timezone.utc).isoformat()
        if not principal.owner_user_id:
            return WriteReceipt(request_id=request.request_id, status=Status.UNSUPPORTED, received_at=now, elapsed_ms=0, error="principal has no owner user")
        payload = {
            "messages": [{"role": item.role, "content": item.content} for item in request.messages],
            "user_id": principal.owner_user_id,
            "metadata": self._base_metadata(request, principal),
            "infer": request.write_mode == "conversation",
        }
        try:
            data = await self._call("write", payload)
            return WriteReceipt(
                request_id=request.request_id,
                status=Status.PASS,
                accepted=True,
                processed=True,
                native_ids=data.get("native_ids", []),
                received_at=now,
                elapsed_ms=int((time.perf_counter() - started) * 1000),
                raw=data.get("raw"),
            )
        except asyncio.TimeoutError:
            return WriteReceipt(request_id=request.request_id, status=Status.TIMEOUT, received_at=now, elapsed_ms=int((time.perf_counter() - started) * 1000), error="write timeout")
        except Exception as exc:
            return WriteReceipt(request_id=request.request_id, status=Status.FAIL, received_at=now, elapsed_ms=int((time.perf_counter() - started) * 1000), error=str(exc))

    async def search(self, request: SearchRequest, principal: Principal) -> SearchResult:
        started = time.perf_counter()
        filter_sets = self._filter_sets(request.namespace, principal)
        if not filter_sets:
            return SearchResult(request_id=request.request_id, status=Status.PASS, hits=[], elapsed_ms=0)
        try:
            data = await self._call("search", {"query": request.query, "top_k": request.top_k, "filter_sets": filter_sets})
            hits = []
            for item in data.get("results", []):
                metadata = dict(item.get("metadata") or {})
                refs = metadata.get("source_message_ids")
                hits.append(
                    SearchHit(
                        native_id=str(item.get("id") or ""),
                        text=str(item.get("memory") or item.get("text") or ""),
                        score=item.get("score"),
                        native_metadata=metadata,
                        source_refs=list(refs) if isinstance(refs, list) else None,
                        observed_at=datetime.now(timezone.utc).isoformat(),
                    )
                )
            return SearchResult(request_id=request.request_id, status=Status.PASS, hits=hits, elapsed_ms=int((time.perf_counter() - started) * 1000))
        except asyncio.TimeoutError:
            return SearchResult(request_id=request.request_id, status=Status.TIMEOUT, elapsed_ms=int((time.perf_counter() - started) * 1000), error="search timeout")
        except Exception as exc:
            return SearchResult(request_id=request.request_id, status=Status.FAIL, elapsed_ms=int((time.perf_counter() - started) * 1000), error=str(exc))
