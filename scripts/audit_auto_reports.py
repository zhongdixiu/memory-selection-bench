#!/usr/bin/env python3
"""Audit structural consistency of Agent review summaries against run artifacts.

This check verifies counts, case IDs, mechanical statuses and copied verdicts.
It cannot determine whether an Agent's semantic judgment is correct.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
ARTIFACTS = ROOT / "artifacts"
CASE_HEADING = re.compile(r"^### 案例 ([A-Z]\d{2})：", re.M)
CASE_VERDICT = re.compile(r"\*\*本案例人工终判\*\*：`<(PASS|FAIL)(?:[^>]*)>`")
PROPOSITION_ROW = re.compile(r"^\| \d+ \| (required|forbidden) \| .*? \| `<([^>]+)>` \|", re.M)
SUMMARY_ROW = re.compile(r"^\| ([A-Z]\d{2}) \| ([A-Z_]+) \| `<?(PASS|FAIL)>?` \|", re.M)


def audit_review(path: Path) -> tuple[dict[str, object], list[str]]:
    run_id = path.stem.removeprefix("manual_review_")
    result_path = ARTIFACTS / run_id / "case_results.json"
    raw = json.loads(result_path.read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8")
    case_matches = list(CASE_HEADING.finditer(text))
    case_verdicts: dict[str, str] = {}
    errors: list[str] = []
    for index, match in enumerate(case_matches):
        end = case_matches[index + 1].start() if index + 1 < len(case_matches) else len(text)
        block = text[match.end():end]
        verdict = CASE_VERDICT.search(block)
        if verdict is None:
            errors.append(f"{run_id}/{match.group(1)}: missing case verdict")
        else:
            case_verdicts[match.group(1)] = verdict.group(1)

    summary = text.split("## 汇总", 1)[-1]
    summary_rows = {case_id: (status, verdict) for case_id, status, verdict in SUMMARY_ROW.findall(summary)}
    raw_by_case = {item["case_id"]: item for item in raw}
    raw_rows = {case_id: item["status"] for case_id, item in raw_by_case.items()}
    if len(summary_rows) != len(raw) or set(summary_rows) != set(raw_rows):
        errors.append(f"{run_id}: summary case IDs/count differ from artifacts")
    if len(case_matches) != len(raw):
        errors.append(f"{run_id}: case section count differs from artifacts")
    if "Agent 自动评估" not in text or "人工签名：未签署" not in text:
        errors.append(f"{run_id}: automatic evaluation provenance is missing")

    overrides: list[str] = []
    for case_id, (status, verdict) in summary_rows.items():
        if raw_rows.get(case_id) != status:
            errors.append(f"{run_id}/{case_id}: mechanical status mismatch")
        if case_verdicts.get(case_id) != verdict:
            errors.append(f"{run_id}/{case_id}: case and summary verdict mismatch")
        if status == "FAIL" and verdict == "PASS":
            overrides.append(case_id)
            failures = [
                failure
                for operation in raw_by_case[case_id]["operations"]
                for failure in operation.get("evaluation", {}).get("hard_failures", [])
            ]
            if not failures or any(not item.startswith("found forbidden token:") for item in failures):
                errors.append(f"{run_id}/{case_id}: semantic override has non-token hard failures")

    for index, match in enumerate(case_matches):
        case_id = match.group(1)
        end = case_matches[index + 1].start() if index + 1 < len(case_matches) else len(text)
        propositions = PROPOSITION_ROW.findall(text[match.end():end])
        bad = [
            (kind, value) for kind, value in propositions
            if (kind == "required" and value != "成立")
            or (kind == "forbidden" and value != "未出现")
        ]
        if case_verdicts.get(case_id) == "PASS" and bad:
            errors.append(f"{run_id}/{case_id}: PASS conflicts with proposition verdicts {bad}")
        if case_verdicts.get(case_id) == "FAIL" and raw_rows.get(case_id) == "REVIEW_REQUIRED" and propositions and not bad:
            errors.append(f"{run_id}/{case_id}: FAIL has no failed proposition or mechanical failure")

    counts = Counter(verdict for _, verdict in summary_rows.values())
    return {
        "run_id": run_id,
        "candidate": run_id.split("-")[1],
        "track": run_id.split("-")[2],
        "suite": run_id.split("-")[3],
        "cases": len(summary_rows),
        "pass": counts["PASS"],
        "fail": counts["FAIL"],
        "semantic_overrides": overrides,
    }, errors


def audit_integration(path: Path) -> dict[str, object]:
    run_id = path.parent.name
    data = json.loads(path.read_text(encoding="utf-8"))
    memory_modes = [task for task in data["tasks"] if task["mode"] in {"M1", "M2"}]
    literal_pass = sum(
        all(task["required_tokens_found"].values())
        and not any(task["forbidden_tokens_found"].values())
        for task in memory_modes
    )
    return {
        "run_id": run_id,
        "candidate": run_id.split("-")[1],
        "preseed_pass": sum(item["result"]["status"] == "PASS" and item["result"]["processed"] for item in data["preseed"]),
        "preseed_total": len(data["preseed"]),
        "literal_pass": literal_pass,
        "memory_mode_total": len(memory_modes),
        "bridge_searches": len(data["bridge_searches"]),
        "bridge_writes": len(data["bridge_writes"]),
    }


def main() -> int:
    review_paths = sorted(
        path for path in REPORTS.glob("manual_review_*.md")
        if re.match(r"manual_review_\d{8}T\d{6}Z-", path.name)
    )
    review_rows: list[dict[str, object]] = []
    errors: list[str] = []
    for path in review_paths:
        row, issues = audit_review(path)
        review_rows.append(row)
        errors.extend(issues)

    integration_paths = sorted(ARTIFACTS.glob("*email*/integration_results.json"))
    integration_rows = [audit_integration(path) for path in integration_paths]
    lines = [
        "# Agent 自动评估结构核对", "",
        "本文件由 `python scripts/audit_auto_reports.py` 从评审汇总与原始 artifacts 生成。",
        "仅核对结构和计数；不验证 Agent 语义判断是否正确。", "",
        "| run_id | 候选 | 轨道 | 套件 | PASS | FAIL | 机械 FAIL→语义 PASS |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in review_rows:
        lines.append(
            f"| `{row['run_id']}` | {row['candidate']} | {row['track']} | {row['suite']} | "
            f"{row['pass']}/{row['cases']} | {row['fail']} | {', '.join(row['semantic_overrides']) or '—'} |"
        )
    lines += [
        "", "## Email Agent 严格 token 检查", "",
        "| run_id | preseed PASS | M1/M2 严格 token PASS | bridge searches | bridge writes |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in integration_rows:
        lines.append(
            f"| `{row['run_id']}` | {row['preseed_pass']}/{row['preseed_total']} | "
            f"{row['literal_pass']}/{row['memory_mode_total']} | {row['bridge_searches']} | {row['bridge_writes']} |"
        )
    lines += ["", "## 结构问题", ""]
    lines += [f"- {item}" for item in errors] or ["未发现。"]
    output = REPORTS / "auto_audit.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(review_rows)} review files, {len(integration_rows)} integration files, {len(errors)} structural issue(s); wrote {output}")
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
