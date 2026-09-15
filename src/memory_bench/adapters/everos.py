from __future__ import annotations

import asyncio
import json
import os
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from memory_bench.contracts import Principal, SearchHit, SearchRequest, SearchResult, Status, Track, WriteReceipt, WriteRequest


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class EverOSAdapter:
    candidate = "everos"

    def __init__(self, *, config: dict[str, Any], runtime_dir: Path, track: Track) -> None:
        self.config = config
        self.runtime_dir = runtime_dir
        self.track = track
        self.port = _free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self.process: asyncio.subprocess.Process | None = None
        self.logs: list[str] = []
        self._log_task: asyncio.Task | None = None
        self.client = httpx.AsyncClient(timeout=config["request_timeout_seconds"])

    def _write_safe_config(self) -> None:
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        content = """[memory]\ntimezone = \"Asia/Shanghai\"\n\n[api]\nhost = \"127.0.0.1\"\n\n[llm]\nmodel = \"qwen3.7-plus\"\napi_key = \"\"\nbase_url = \"https://dashscope.aliyuncs.com/compatible-mode/v1\"\n\n[embedding]\nmodel = \"BAAI/bge-m3\"\napi_key = \"\"\nbase_url = \"https://api.siliconflow.cn/v1\"\n\n[rerank]\nprovider = \"vllm\"\nmodel = \"BAAI/bge-reranker-v2-m3\"\napi_key = \"\"\nbase_url = \"https://api.siliconflow.cn/v1\"\n"""
        (self.runtime_dir / "everos.toml").write_text(content, encoding="utf-8")
        # An empty override file is valid and keeps EverOS's native strategy
        # defaults. There is deliberately no synthetic global scheduler switch:
        # ome.toml only accepts per-strategy overrides.
        (self.runtime_dir / "ome.toml").write_text("# Native OME strategy defaults.\n", encoding="utf-8")

    async def start(self) -> None:
        self._write_safe_config()
        paths = self.config["paths"]
        providers = self.config["providers"]
        env = os.environ.copy()
        env.pop("all_proxy", None)
        env.pop("ALL_PROXY", None)
        env.update(
            {
                "EVEROS_ROOT": str(self.runtime_dir),
                "EVEROS_LLM__MODEL": providers["llm"]["model"],
                "EVEROS_LLM__BASE_URL": providers["llm"]["base_url"],
                "EVEROS_LLM__API_KEY": os.environ["DASHSCOPE_API_KEY"],
                "EVEROS_LLM__EXTRA": json.dumps({"extra_body": {"enable_thinking": False}}),
                "EVEROS_EMBEDDING__MODEL": providers["embedding"]["model"],
                "EVEROS_EMBEDDING__BASE_URL": providers["embedding"]["base_url"],
                "EVEROS_EMBEDDING__API_KEY": os.environ["SILICONFLOW_API_KEY"],
                "EVEROS_RERANK__PROVIDER": "vllm",
                "EVEROS_RERANK__MODEL": providers["rerank"]["model"],
                "EVEROS_RERANK__BASE_URL": providers["rerank"]["base_url"],
                "EVEROS_RERANK__API_KEY": os.environ["SILICONFLOW_API_KEY"],
                "EVEROS_LOG_LEVEL": "INFO",
            }
        )
        executable = str(Path(paths["everos_python"]).with_name("everos"))
        self.process = await asyncio.create_subprocess_exec(
            executable,
            "server",
            "start",
            "--root",
            str(self.runtime_dir),
            "--host",
            "127.0.0.1",
            "--port",
            str(self.port),
            cwd=paths["everos_root"],
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self._log_task = asyncio.create_task(self._drain_logs())
        deadline = time.monotonic() + 120
        while time.monotonic() < deadline:
            if self.process.returncode is not None:
                raise RuntimeError(f"EverOS exited during startup: {self.logs[-20:]}")
            try:
                response = await self.client.get(f"{self.base_url}/health", timeout=2)
                if response.status_code == 200:
                    return
            except httpx.HTTPError:
                pass
            await asyncio.sleep(0.5)
        raise TimeoutError(f"EverOS startup timed out: {self.logs[-20:]}")

    async def _drain_logs(self) -> None:
        assert self.process and self.process.stdout
        while line := await self.process.stdout.readline():
            self.logs.append(line.decode("utf-8", errors="replace").rstrip())
            self.logs = self.logs[-1000:]

    async def close(self) -> None:
        await self.client.aclose()
        if not self.process:
            return
        self.process.terminate()
        try:
            await asyncio.wait_for(self.process.wait(), timeout=20)
        except asyncio.TimeoutError:
            self.process.kill()
            await self.process.wait()
        if self._log_task:
            await self._log_task

    async def health(self) -> dict:
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _space(namespace: str, kind: str, scope_id: str, project_id: str | None, source_domain: str, track: Track) -> tuple[str, str]:
        if track == Track.P_NATIVE:
            return f"{namespace}-{source_domain}", f"{namespace}-{project_id or 'default'}"
        if kind == "user_public":
            return f"{namespace}-shared", f"{namespace}-default"
        if kind == "domain":
            return f"{namespace}-domain-{scope_id}", f"{namespace}-default"
        if kind == "project":
            return f"{namespace}-projects", f"{namespace}-{project_id or scope_id}"
        return f"{namespace}-agent-{scope_id}", f"{namespace}-{project_id or 'default'}"

    def _read_spaces(self, namespace: str, principal: Principal) -> list[tuple[str, str]]:
        if not principal.owner_user_id:
            return []
        if self.track == Track.P_NATIVE:
            return [(f"{namespace}-{principal.domain_id}", f"{namespace}-default")]
        spaces = [
            (f"{namespace}-shared", f"{namespace}-default"),
            (f"{namespace}-domain-{principal.domain_id}", f"{namespace}-default"),
        ]
        spaces.extend((f"{namespace}-projects", f"{namespace}-{project}") for project in principal.allowed_projects)
        spaces.extend((f"{namespace}-agent-{agent}", f"{namespace}-default") for agent in principal.allowed_agent_private)
        return spaces

    async def write(self, request: WriteRequest, principal: Principal) -> WriteReceipt:
        started = time.perf_counter()
        now = datetime.now(timezone.utc).isoformat()
        if request.write_mode == "direct_record":
            return WriteReceipt(request_id=request.request_id, status=Status.UNSUPPORTED, received_at=now, elapsed_ms=0, error="EverOS memory/add has no direct_record contract")
        if not principal.owner_user_id:
            return WriteReceipt(request_id=request.request_id, status=Status.UNSUPPORTED, received_at=now, elapsed_ms=0, error="principal has no owner user")
        app_id, project_id = self._space(
            request.namespace,
            request.requested_scope.kind,
            request.requested_scope.scope_id,
            request.requested_scope.project_id,
            request.source_domain_id,
            self.track,
        )
        messages = []
        for item in request.messages:
            sender_id = principal.owner_user_id if item.role == "user" else request.source_agent_id
            messages.append(
                {
                    "sender_id": sender_id,
                    "role": "assistant" if item.role == "system" else item.role,
                    "timestamp": int(datetime.fromisoformat(item.occurred_at.replace("Z", "+00:00")).timestamp() * 1000),
                    "content": item.content,
                }
            )
        try:
            add_response = await self.client.post(
                f"{self.base_url}/api/v2/memory/add",
                json={"session_id": request.source_session_id, "app_id": app_id, "project_id": project_id, "messages": messages},
                headers={"X-Request-Id": request.request_id},
            )
            add_response.raise_for_status()
            flush_response = await self.client.post(
                f"{self.base_url}/api/v2/memory/flush",
                json={"session_id": request.source_session_id, "app_id": app_id, "project_id": project_id},
                headers={"X-Request-Id": f"{request.request_id}-flush"},
            )
            flush_response.raise_for_status()
            add_body = add_response.json()
            flush_body = flush_response.json()
            raw = {"add": add_body, "flush": flush_body}
            processed = any(
                body.get("data", {}).get("status") == "extracted"
                for body in (add_body, flush_body)
            )
            return WriteReceipt(
                request_id=request.request_id,
                status=Status.PASS,
                accepted=True,
                processed=processed,
                received_at=now,
                elapsed_ms=int((time.perf_counter() - started) * 1000),
                raw=raw,
            )
        except httpx.TimeoutException:
            return WriteReceipt(request_id=request.request_id, status=Status.TIMEOUT, received_at=now, elapsed_ms=int((time.perf_counter() - started) * 1000), error="write/flush timeout")
        except Exception as exc:
            detail = getattr(getattr(exc, "response", None), "text", "")
            return WriteReceipt(request_id=request.request_id, status=Status.FAIL, received_at=now, elapsed_ms=int((time.perf_counter() - started) * 1000), error=f"{exc}: {detail[:500]}")

    async def search(self, request: SearchRequest, principal: Principal) -> SearchResult:
        started = time.perf_counter()
        spaces = self._read_spaces(request.namespace, principal)
        if not spaces:
            return SearchResult(request_id=request.request_id, status=Status.PASS, hits=[], elapsed_ms=0)
        try:
            by_id: dict[str, SearchHit] = {}
            raw_responses = []
            for app_id, project_id in spaces:
                response = await self.client.post(
                    f"{self.base_url}/api/v2/memory/search",
                    json={
                        "user_id": principal.owner_user_id,
                        "app_id": app_id,
                        "project_id": project_id,
                        "query": request.query,
                        "method": "vector",
                        "top_k": request.top_k,
                    },
                )
                response.raise_for_status()
                body = response.json()
                raw_responses.append(body)
                for item in body.get("data", {}).get("episodes", []):
                    hit = SearchHit(
                        native_id=str(item.get("id") or ""),
                        text="\n".join(str(value) for value in (item.get("summary"), item.get("subject"), item.get("episode")) if value),
                        score=item.get("score"),
                        native_metadata={key: item.get(key) for key in ("user_id", "app_id", "project_id", "session_id", "timestamp", "sender_ids", "atomic_facts")},
                        source_refs=[item["session_id"]] if item.get("session_id") else None,
                        observed_at=datetime.now(timezone.utc).isoformat(),
                    )
                    old = by_id.get(hit.native_id)
                    if old is None or float(hit.score or 0) > float(old.score or 0):
                        by_id[hit.native_id] = hit
            hits = sorted(by_id.values(), key=lambda item: float(item.score or 0), reverse=True)[: request.top_k]
            return SearchResult(request_id=request.request_id, status=Status.PASS, hits=hits, elapsed_ms=int((time.perf_counter() - started) * 1000), raw=raw_responses)
        except httpx.TimeoutException:
            return SearchResult(request_id=request.request_id, status=Status.TIMEOUT, elapsed_ms=int((time.perf_counter() - started) * 1000), error="search timeout")
        except Exception as exc:
            detail = getattr(getattr(exc, "response", None), "text", "")
            return SearchResult(request_id=request.request_id, status=Status.FAIL, elapsed_ms=int((time.perf_counter() - started) * 1000), error=f"{exc}: {detail[:500]}")
