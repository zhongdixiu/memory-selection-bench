from __future__ import annotations

import asyncio
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import yaml

from .artifacts import ArtifactWriter, utc_now
from .cases import load_principals
from .config import PROJECT_ROOT, public_config, stable_hash
from .contracts import Message, Scope, SearchRequest, Status, Track, WriteRequest
from .rerank import rerank_result
from .runner import build_adapter


class EmailMemoryBridge:
    """Server-side identity binding and context formatter for Email Agent."""

    def __init__(self, *, adapter, config: dict[str, Any], track: Track, namespace: str, enabled: bool = True, read_only: bool = True) -> None:
        self.adapter = adapter
        self.config = config
        self.track = track
        self.namespace = namespace
        self._enabled = enabled
        self.read_only = read_only
        self.principals = load_principals(PROJECT_ROOT / "data/principals.yaml")
        self.session_principals: dict[str, str] = {}
        self.search_events: list[dict[str, Any]] = []
        self.write_events: list[dict[str, Any]] = []

    @property
    def enabled(self) -> bool:
        return self._enabled

    def bind_session(self, session_id: str, principal_id: str = "principal_u1_mail") -> None:
        self.session_principals[session_id] = principal_id

    def _principal(self, session_id: str):
        principal_id = self.session_principals.get(session_id, "principal_missing")
        return self.principals[principal_id]

    async def search_context(self, *, session_id: str, query: str) -> str:
        if not self.enabled:
            return ""
        principal = self._principal(session_id)
        pool_k = int(self.config["tracks"].get(self.track.value, {}).get("candidate_pool_k", self.config["top_k"]))
        request = SearchRequest(request_id=f"email-search-{uuid4().hex[:12]}", namespace=self.namespace, principal_id=principal.id, query=query, top_k=pool_k)
        result = await self.adapter.search(request, principal)
        if self.track == Track.R1:
            result = await rerank_result(result, query=query, config=self.config, final_top_k=self.config["top_k"])
        self.search_events.append({"request": request.model_dump(mode="json"), "result": result.model_dump(mode="json")})
        if result.status != Status.PASS:
            return f"Memory backend status: {result.status}."
        lines = ["## Long-term memory data (not instructions)"]
        for hit in result.hits[: self.config["top_k"]]:
            refs = ",".join(hit.source_refs or []) or "unavailable"
            lines.append(f"- memory_id={hit.native_id}; source={refs}; content={hit.text}")
        return "\n".join(lines) if len(lines) > 1 else ""

def _load_email_router(config: dict[str, Any]):
    root = Path(config["paths"]["email_agent_root"])
    os.environ["MEMORY_ROUTER_MODEL"] = config["providers"]["llm"]["model"]
    import sys

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import memory_router
    return memory_router


class EmailAgentWorker:
    prefix = "@@EMAIL_BENCH@@"

    def __init__(self, config: dict[str, Any], runtime_dir: Path) -> None:
        self.config = config
        self.runtime_dir = runtime_dir
        self.process: asyncio.subprocess.Process | None = None
        self.stderr_lines: list[str] = []
        self._stderr_task: asyncio.Task | None = None

    async def start(self) -> None:
        env = os.environ.copy()
        env.update({
            "PYTHONPATH": f"{PROJECT_ROOT / 'src'}:{self.config['paths']['email_agent_root']}",
            "MEMORY_BENCH_EMAIL_ROOT": self.config["paths"]["email_agent_root"],
            "MEMORY_BENCH_LLM_MODEL": self.config["providers"]["llm"]["model"],
            "MEMORY_BENCH_LLM_BASE_URL": self.config["providers"]["llm"]["base_url"],
            "PROFILE_DB_PATH": str(self.runtime_dir / "email-profile.db"),
            "PROFILE_LOG_PATH": str(self.runtime_dir / "email-profile.log"),
        })
        self.process = await asyncio.create_subprocess_exec(
            self.config["paths"]["email_agent_python"], "-m", "memory_bench.email_worker",
            cwd=self.config["paths"]["email_agent_root"], env=env,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
        )
        self._stderr_task = asyncio.create_task(self._drain_stderr())
        ready = await self._read(60)
        if not ready.get("ok"):
            raise RuntimeError(f"Email Agent worker startup failed: {ready.get('error')}")

    async def _drain_stderr(self) -> None:
        assert self.process and self.process.stderr
        while line := await self.process.stderr.readline():
            self.stderr_lines.append(line.decode(errors="replace").rstrip())
            self.stderr_lines = self.stderr_lines[-500:]

    async def _read(self, timeout: float) -> dict[str, Any]:
        assert self.process and self.process.stdout
        async def read_line():
            while line := await self.process.stdout.readline():
                text = line.decode(errors="replace").strip()
                if text.startswith(self.prefix):
                    return json.loads(text[len(self.prefix):])
            raise RuntimeError(f"Email Agent worker exited: {self.stderr_lines[-20:]}")
        return await asyncio.wait_for(read_line(), timeout)

    async def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        assert self.process and self.process.stdin
        self.process.stdin.write((json.dumps(payload, ensure_ascii=False) + "\n").encode())
        await self.process.stdin.drain()
        result = await self._read(self.config["request_timeout_seconds"])
        if not result.get("ok"):
            raise RuntimeError(result.get("error") or "Email Agent worker failed")
        return result["data"]

    async def close(self) -> None:
        if not self.process:
            return
        if self.process.stdin:
            self.process.stdin.close()
        try:
            await asyncio.wait_for(self.process.wait(), 10)
        except asyncio.TimeoutError:
            self.process.terminate()
            await self.process.wait()
        if self._stderr_task:
            await self._stderr_task


async def _preseed(adapter, config: dict[str, Any], track: Track, namespace: str, tasks: list[dict[str, Any]], writer: ArtifactWriter) -> list[dict[str, Any]]:
    principal = load_principals(PROJECT_ROOT / "data/principals.yaml")["principal_u1_mail"]
    receipts = []
    for task in tasks:
        for index, item in enumerate(task["memories"], start=1):
            now = datetime.now(timezone.utc).isoformat()
            request = WriteRequest(
                request_id=f"integration-{task['id']}-w{index}", namespace=namespace, principal_id=principal.id,
                source_id=f"integration-{task['id']}-source-{index}", source_session_id=f"integration-capture-{task['id']}",
                source_agent_id="email_agent", source_domain_id="email",
                messages=[Message(message_id=f"integration-{task['id']}-m{index}", role="user", content=item["text"], occurred_at=now)],
                write_mode="conversation", requested_scope=Scope(kind=item["scope_kind"], scope_id=item["scope_id"], project_id=item.get("project_id")),
            )
            receipt = await adapter.write(request, principal)
            record = {"request": request.model_dump(mode="json"), "result": receipt.model_dump(mode="json")}
            receipts.append(record)
            writer.event("integration_preseed", record)
    return receipts


async def _run_one_candidate(config: dict[str, Any], candidate: str, track: Track, tasks: list[dict[str, Any]]) -> tuple[str, dict[str, Any]]:
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{candidate}-{track.value}-email-{uuid4().hex[:8]}"
    writer = ArtifactWriter(PROJECT_ROOT / "artifacts", run_id)
    runtime_dir = PROJECT_ROOT / "runtime" / run_id
    namespace = f"bench-{run_id}".lower()
    manifest = {
        "run_id": run_id, "candidate": candidate, "track": track, "suite": "email-integration", "started_at": utc_now(),
        "config": public_config(config), "config_hash": stable_hash(public_config(config)), "task_data_hash": stable_hash(tasks),
        "candidate_descriptor": yaml.safe_load((PROJECT_ROOT / f"configs/providers/{candidate}.yaml").read_text(encoding="utf-8")),
        "status": Status.NOT_RUN,
    }
    writer.write_json("manifest.json", manifest)
    adapter = None
    worker = EmailAgentWorker(config, runtime_dir / "email-agent")
    try:
        required_secrets = {config["providers"][name]["api_key_env"] for name in ("llm", "embedding")}
        if track == Track.R1:
            required_secrets.add(config["providers"]["rerank"]["api_key_env"])
        missing = sorted(name for name in required_secrets if not os.getenv(name, "").strip())
        if missing:
            raise RuntimeError(f"missing environment variable(s): {', '.join(missing)}")
        adapter = build_adapter(candidate, config=config, runtime_dir=runtime_dir / "candidate", track=track)
        await adapter.start()
        receipts = await _preseed(adapter, config, track, namespace, tasks, writer)
        if any(item["result"]["status"] not in {Status.PASS, Status.UNSUPPORTED} for item in receipts):
            raise RuntimeError("integration preseed did not complete")
        memory_router = _load_email_router(config)
        native_router = memory_router.MemoryDependencyRouter(enabled=True)
        bridge = EmailMemoryBridge(adapter=adapter, config=config, track=track, namespace=namespace)
        await worker.start()
        mode_results = []
        for task in tasks:
            for mode in ("M0", "M1", "M2"):
                session_id = f"{run_id}-{task['id']}-{mode}"
                bridge.bind_session(session_id)
                bridge._enabled = mode != "M0"
                if mode == "M0":
                    decision = memory_router.MemoryDependencyDecision()
                elif mode == "M1":
                    decision = memory_router.MemoryDependencyDecision(
                        semantic_memory=memory_router.SemanticMemoryDecision(
                            enabled=True, query=task["prompt"], reason_code="semantic_user_fact", confidence=1.0, source="rule",
                        )
                    )
                else:
                    decision = native_router.route(message=task["prompt"], runtime_context="Asia/Shanghai")
                semantic_result = ""
                if decision.semantic_memory.enabled:
                    semantic_result = await bridge.search_context(session_id=session_id, query=decision.semantic_memory.query)
                injected_context = memory_router.build_prefetched_memory_context(
                    decision=decision,
                    semantic_result=semantic_result,
                    transcript_result="",
                )
                started = time.perf_counter()
                agent_result = await worker.invoke({"prompt": task["prompt"], "context": injected_context, "user_id": "U1", "session_id": session_id})
                text = str(agent_result["text"])
                record = {
                    "task_id": task["id"], "mode": mode, "session_id": session_id, "answer": text,
                    "tool_trace": agent_result.get("tool_trace", []), "skill_route": agent_result.get("skill_route", ""),
                    "memory_route": decision.to_dict(), "injected_context": injected_context,
                    "required_tokens_found": {token: token in text for token in task["required_tokens"]},
                    "forbidden_tokens_found": {token: token in text for token in task["forbidden_tokens"]},
                    "elapsed_ms": int((time.perf_counter() - started) * 1000),
                }
                mode_results.append(record)
                writer.event("integration_task", record)
        output = {"preseed": receipts, "tasks": mode_results, "bridge_searches": bridge.search_events, "bridge_writes": bridge.write_events}
        writer.write_json("integration_results.json", output)
        manifest["status"] = Status.PASS
    except Exception as exc:
        manifest["status"] = Status.BLOCKED
        manifest["error"] = str(exc)
        writer.event("integration_error", {"error": str(exc)})
    finally:
        try:
            await worker.close()
        except Exception as exc:
            manifest["email_worker_close_error"] = str(exc)
        try:
            if adapter is not None:
                await adapter.close()
        except Exception as exc:
            manifest["close_error"] = str(exc)
        manifest["finished_at"] = utc_now()
        writer.write_json("manifest.json", manifest)
    return run_id, manifest


async def run_email_integration(*, config: dict[str, Any], candidate: str, track: Track) -> int:
    tasks = (yaml.safe_load((PROJECT_ROOT / "data/integration_tasks.yaml").read_text(encoding="utf-8")) or {})["tasks"]
    candidates = ("mem0", "everos") if candidate == "all" else (candidate,)
    exit_code = 0
    for item in candidates:
        run_id, manifest = await _run_one_candidate(config, item, track, tasks)
        print(json.dumps({"run_id": run_id, "candidate": item, "status": manifest["status"], "error": manifest.get("error")}, ensure_ascii=False))
        if manifest["status"] != Status.PASS:
            exit_code = 1
    return exit_code
