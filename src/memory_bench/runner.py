from __future__ import annotations

import asyncio
import csv
import io
import json
import os
import time
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

import yaml

from .adapters.everos import EverOSAdapter
from .adapters.mem0 import Mem0Adapter
from .artifacts import ArtifactWriter, utc_now
from .cases import load_cases, load_principals
from .config import PROJECT_ROOT, public_config, stable_hash
from .contracts import Case, Scope, SearchRequest, Status, Track, WriteRequest
from .evaluation import Evaluation, evaluate_hits
from .rerank import rerank_result


DECISION_CASE_IDS = ("F05", "N03", "U01", "U05", "D02", "D03", "P01", "P04", "C02", "T01", "E01", "E04")
P_NATIVE_CASE_IDS = ("F05", "D03", "P01", "C02", "T01", "E01")


def select_cases(cases: list[Case], suite: str) -> list[Case]:
    if suite == "full":
        return cases
    if suite == "smoke":
        return [case for case in cases if case.id == "F02"]
    wanted = set(P_NATIVE_CASE_IDS if suite == "probe" else DECISION_CASE_IDS)
    return [case for case in cases if case.id in wanted]


def build_adapter(candidate: str, *, config: dict[str, Any], runtime_dir: Path, track: Track):
    if candidate == "mem0":
        return Mem0Adapter(config=config, runtime_dir=runtime_dir, track=track)
    if candidate == "everos":
        return EverOSAdapter(config=config, runtime_dir=runtime_dir, track=track)
    raise ValueError(f"unknown candidate: {candidate}")


def _case_status(operation_statuses: list[Status], evaluations: list[Evaluation]) -> Status:
    for status in (Status.BLOCKED, Status.TIMEOUT, Status.FAIL, Status.UNSUPPORTED):
        if status in operation_statuses:
            return status
    if any(item.status == Status.FAIL for item in evaluations):
        return Status.FAIL
    if any(item.status == Status.REVIEW_REQUIRED for item in evaluations):
        return Status.REVIEW_REQUIRED
    return Status.PASS


async def _run_case(adapter, case: Case, principals: dict, *, namespace: str, config: dict[str, Any], track: Track, writer: ArtifactWriter) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    op_statuses: list[Status] = []
    evaluations: list[Evaluation] = []
    receipts: dict[str, dict[str, Any]] = {}
    track_config = config.get("tracks", {}).get(track.value, {})
    candidate_pool_k = int(track_config.get("candidate_pool_k", config["top_k"]))
    final_top_k = int(track_config.get("final_top_k", config["top_k"]))
    for operation in case.operations:
        principal = principals[operation.principal_id] if operation.principal_id else None
        if operation.op == "write":
            request = WriteRequest(
                request_id=operation.request_id,
                namespace=namespace,
                principal_id=operation.principal_id,
                source_id=operation.source_id,
                source_session_id=operation.source_session_id,
                source_agent_id=operation.source_agent_id,
                source_domain_id=operation.source_domain_id,
                messages=operation.messages,
                write_mode=operation.write_mode,
                requested_scope=Scope(kind=operation.scope_kind, scope_id=operation.scope_id, project_id=operation.project_id),
            )
            receipt = await adapter.write(request, principal)
            payload = receipt.model_dump(mode="json")
            receipts[operation.request_id] = payload
            records.append({"op": "write", "request": request.model_dump(mode="json"), "result": payload})
            op_statuses.append(receipt.status)
            writer.event("write", {"case_id": case.id, "result": payload})
        elif operation.op == "search":
            request = SearchRequest(request_id=operation.request_id, namespace=namespace, principal_id=operation.principal_id, query=operation.query, top_k=candidate_pool_k, purpose=operation.purpose)
            # Visibility polling: some candidates finish extraction/indexing
            # asynchronously after the write receipt reports success. Retry on
            # the configured schedule while automatic scoring hard-fails, so a
            # FAIL is only recorded after the visibility window is exhausted.
            # The same code path applies to every candidate.
            deadline = float(config.get("visibility_deadline_seconds") or 0)
            intervals = [float(item) for item in (config.get("poll_intervals_seconds") or [0.0])]
            max_attempts = max(1, int(config.get("max_poll_attempts") or 1))
            transport_retries = max(0, int(config.get("max_transport_retries") or 0))
            poll_started = time.monotonic()
            attempts = 0
            while True:
                # Transport-level retries: a transient provider error (e.g. a
                # one-off 4xx from the embedding endpoint) must not overwrite
                # the real evaluation state of an otherwise working search.
                for transport_attempt in range(transport_retries + 1):
                    result = await adapter.search(request, principal)
                    if result.status == Status.PASS or transport_attempt >= transport_retries:
                        break
                    writer.event("search_transport_retry", {"case_id": case.id, "request_id": request.request_id, "retry": transport_attempt + 1, "status": result.status, "error": result.error})
                    await asyncio.sleep(1.0)
                if track == Track.R1:
                    result = await rerank_result(result, query=request.query, config=config, final_top_k=final_top_k)
                else:
                    result.hits = result.hits[:final_top_k]
                evaluation = evaluate_hits(result.hits, operation.assertions)
                attempts += 1
                writer.event("search_attempt", {"case_id": case.id, "request_id": request.request_id, "attempt": attempts, "status": result.status, "hit_count": len(result.hits), "evaluation_status": evaluation.status, "hard_failures": evaluation.hard_failures})
                if evaluation.status != Status.FAIL or result.status != Status.PASS:
                    break
                if deadline <= 0 or attempts >= max_attempts or time.monotonic() - poll_started >= deadline:
                    break
                await asyncio.sleep(max(intervals[min(attempts, len(intervals) - 1)], 0.0))
            evaluations.append(evaluation)
            op_statuses.append(result.status)
            records.append({"op": "search", "attempts": attempts, "request": request.model_dump(mode="json"), "result": result.model_dump(mode="json"), "evaluation": asdict(evaluation)})
            writer.event("search", {"case_id": case.id, "status": result.status, "hit_count": len(result.hits), "attempts": attempts, "evaluation": asdict(evaluation)})
        else:
            receipt = receipts.get(operation.receipt_ref or "")
            status = Status.PASS if receipt and receipt.get("processed") else Status.FAIL
            op_statuses.append(status)
            records.append({"op": "await_observable", "receipt_ref": operation.receipt_ref, "status": status})
    status = _case_status(op_statuses, evaluations)
    return {"case_id": case.id, "group": case.group, "title": case.title, "status": status, "operations": records}


def _csv_text(results: Iterable[dict[str, Any]]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=("case_id", "group", "title", "status", "hard_failures", "review_items"))
    writer.writeheader()
    for item in results:
        evaluations = [op.get("evaluation", {}) for op in item.get("operations", []) if op.get("evaluation")]
        writer.writerow({
            "case_id": item["case_id"], "group": item["group"], "title": item["title"], "status": item["status"],
            "hard_failures": json.dumps([failure for evaluation in evaluations for failure in evaluation.get("hard_failures", [])], ensure_ascii=False),
            "review_items": json.dumps([review for evaluation in evaluations for review in evaluation.get("review_items", [])], ensure_ascii=False),
        })
    return output.getvalue()


async def run_benchmark(*, config: dict[str, Any], candidate: str, track: Track, suite: str, artifacts_root: Path | None = None) -> tuple[str, dict[str, Any]]:
    cases = select_cases(load_cases(PROJECT_ROOT / "data/cases.yaml"), suite)
    principals = load_principals(PROJECT_ROOT / "data/principals.yaml")
    candidate_descriptor = yaml.safe_load((PROJECT_ROOT / f"configs/providers/{candidate}.yaml").read_text(encoding="utf-8"))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = f"{timestamp}-{candidate}-{track.value}-{suite}-{uuid4().hex[:8]}"
    writer = ArtifactWriter(artifacts_root or PROJECT_ROOT / "artifacts", run_id)
    namespace = f"bench-{run_id}".lower()
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "started_at": utc_now(),
        "candidate": candidate,
        "track": track,
        "suite": suite,
        "case_ids": [case.id for case in cases],
        "case_data_hash": stable_hash([case.model_dump(mode="json") for case in cases]),
        "principal_data_hash": stable_hash({key: value.model_dump(mode="json") for key, value in principals.items()}),
        "candidate_descriptor": candidate_descriptor,
        "config": public_config(config),
        "config_hash": stable_hash(public_config(config)),
        "status": Status.NOT_RUN,
    }
    writer.write_json("manifest.json", manifest)
    adapter = None
    results: list[dict[str, Any]] = []
    try:
        required_secrets = {config["providers"][name]["api_key_env"] for name in ("llm", "embedding")}
        if track == Track.R1:
            required_secrets.add(config["providers"]["rerank"]["api_key_env"])
        missing = sorted(name for name in required_secrets if not os.getenv(name, "").strip())
        if missing:
            raise RuntimeError(f"missing environment variable(s): {', '.join(missing)}")
        adapter = build_adapter(candidate, config=config, runtime_dir=PROJECT_ROOT / "runtime" / run_id, track=track)
        await adapter.start()
        manifest["health"] = await adapter.health()
        for case in cases:
            case_namespace = f"{namespace}-{case.id.lower()}"
            results.append(await _run_case(adapter, case, principals, namespace=case_namespace, config=config, track=track, writer=writer))
        statuses = [Status(item["status"]) for item in results]
        manifest["status"] = Status.FAIL if Status.FAIL in statuses else (Status.TIMEOUT if Status.TIMEOUT in statuses else Status.PASS)
    except Exception as exc:
        manifest["status"] = Status.BLOCKED
        manifest["error"] = str(exc)
        writer.event("run_error", {"error": str(exc)})
        if not results:
            results = [
                {"case_id": case.id, "group": case.group, "title": case.title, "status": Status.BLOCKED, "error": str(exc), "operations": []}
                for case in cases
            ]
    finally:
        try:
            if adapter is not None:
                await adapter.close()
        except Exception as exc:
            manifest["close_error"] = str(exc)
        manifest["finished_at"] = utc_now()
        writer.write_json("manifest.json", manifest)
        writer.write_json("case_results.json", results)
        (writer.run_dir / "case_results.csv").write_text(_csv_text(results), encoding="utf-8")
        logs = getattr(adapter, "logs", None) or getattr(adapter, "stderr_lines", None) or []
        if logs:
            (writer.run_dir / "candidate.log").write_text("\n".join(logs), encoding="utf-8")
    return run_id, manifest
