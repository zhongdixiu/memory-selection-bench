from __future__ import annotations

import csv
import hashlib
import json
import platform
import shutil
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .config import PROJECT_ROOT


def _load_runs(artifacts_root: Path) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    if not artifacts_root.exists():
        return runs
    for manifest_path in sorted(artifacts_root.glob("*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        result_path = manifest_path.parent / "case_results.json"
        manifest["_run_dir"] = str(manifest_path.parent)
        manifest["_results"] = json.loads(result_path.read_text(encoding="utf-8")) if result_path.exists() else []
        runs.append(manifest)
    return runs


def _git_commit(path: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", path, "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    except Exception:
        return "unavailable"


def _python_package(python: str, package: str) -> dict[str, str]:
    code = f"import json,sys,{package}; print(json.dumps({{'python':sys.version.split()[0],'package':getattr({package},'__version__','unknown')}}))"
    try:
        return json.loads(subprocess.run([python, "-c", code], check=True, capture_output=True, text=True, timeout=30).stdout)
    except Exception as exc:
        return {"python": "unavailable", "package": "unavailable", "error": str(exc)}


def _license_record(root: str, destination: Path, candidate: str) -> dict[str, str]:
    source = Path(root) / "LICENSE"
    if not source.exists():
        return {"source": str(source), "status": "missing"}
    target = destination / "licenses" / f"{candidate}-LICENSE"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    payload = source.read_bytes()
    return {"source": str(source), "copy": str(target), "sha256": hashlib.sha256(payload).hexdigest(), "declared": "Apache-2.0"}


def generate_reports(config: dict[str, Any], reports_dir: Path | None = None) -> list[Path]:
    destination = reports_dir or PROJECT_ROOT / "reports"
    destination.mkdir(parents=True, exist_ok=True)
    runs = _load_runs(PROJECT_ROOT / "artifacts")
    created: list[Path] = []

    version_manifest = {
        "host": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
        "mem0": {"root": config["paths"]["mem0_root"], "commit": _git_commit(config["paths"]["mem0_root"]), "environment": _python_package(config["paths"]["mem0_python"], "mem0"), "license": _license_record(config["paths"]["mem0_root"], destination, "mem0"), "dependency_lock": str(Path(config["paths"]["mem0_root"]) / "poetry.lock"), "storage": {"vector": "qdrant-local", "history": "sqlite"}},
        "everos": {"root": config["paths"]["everos_root"], "commit": _git_commit(config["paths"]["everos_root"]), "environment": _python_package(config["paths"]["everos_python"], "everos"), "license": _license_record(config["paths"]["everos_root"], destination, "everos"), "dependency_lock": str(Path(config["paths"]["everos_root"]) / "uv.lock"), "storage": {"source_of_truth": "markdown", "metadata": "sqlite-wal", "index": "lancedb"}},
        "email_agent": {"root": config["paths"]["email_agent_root"], "python": config["paths"]["email_agent_python"]},
        "models": config["providers"],
    }
    path = destination / "version_manifest.json"
    path.write_text(json.dumps(version_manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    created.append(path)

    all_results: list[dict[str, Any]] = []
    for run in runs:
        for result in run["_results"]:
            evaluations = [op.get("evaluation", {}) for op in result.get("operations", []) if op.get("evaluation")]
            all_results.append({
                "run_id": run["run_id"], "candidate": run["candidate"], "track": run["track"], "suite": run["suite"],
                "case_id": result["case_id"], "group": result["group"], "status": result["status"],
                "hard_failures": json.dumps([failure for evaluation in evaluations for failure in evaluation.get("hard_failures", [])], ensure_ascii=False),
                "review_items": json.dumps([review for evaluation in evaluations for review in evaluation.get("review_items", [])], ensure_ascii=False),
                "evidence_path": f"{run['_run_dir']}/case_results.json",
            })
    path = destination / "case_results.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        fields = ("run_id", "candidate", "track", "suite", "case_id", "group", "status", "hard_failures", "review_items", "evidence_path")
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_results)
    created.append(path)

    grouped: dict[tuple[str, str], Counter] = defaultdict(Counter)
    for row in all_results:
        grouped[(row["candidate"], row["track"])][row["status"]] += 1
    lines = [
        "# 能力验证矩阵", "",
        "A～C 只能由成功执行证据确认；当前源码证据不足以把能力填成通过。D 表示接口/调用链已有明确核心缺口，E 表示尚未完成在线验证。", "",
        "| 能力 | Mem0 | EverOS | 当前证据 |", "|---|---|---|---|",
        "| Dense Top-k 检索 | E | E | launcher 已启动，模型调用未执行 |",
        "| 用户/域/项目隔离 | E | E | 映射与离线过滤测试通过，真实存储结果待跑 |",
        "| 逐消息原生来源 | E | D | Mem0 metadata 待实测；EverOS 搜索 DTO 仅返回 session_id |",
        "| direct_record | E | D | Mem0 `infer=false` 待实测；EverOS memory/add 仅接受消息 |",
        "| 公共 R1 rerank | E | E | MockTransport 契约测试通过，SiliconFlow 待调用 |",
        "| Email Agent M0/M1/M2 | E | E | 真实入口 worker 启动通过，模型任务待跑 |", "",
        "## 运行状态汇总", "",
        "该表只汇总可复现产物；`REVIEW_REQUIRED` 仍需人工语义判分。", "", "| 候选 | 轨道 | PASS | FAIL | UNSUPPORTED | BLOCKED | REVIEW_REQUIRED |", "|---|---:|---:|---:|---:|---:|---:|"
    ]
    if grouped:
        for (candidate, track), counts in sorted(grouped.items()):
            lines.append(f"| {candidate} | {track} | {counts['PASS']} | {counts['FAIL']} | {counts['UNSUPPORTED']} | {counts['BLOCKED']} | {counts['REVIEW_REQUIRED']} |")
    else:
        lines.append("| 尚未执行 | - | 0 | 0 | 0 | 0 | 0 |")
    path = destination / "capability_matrix.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    created.append(path)

    live_effect = [run for run in runs if run.get("suite") in {"decision", "full"} and run.get("track") in {"r0", "r1"}]
    probe_runs = [run for run in runs if run.get("track") == "p-native"]
    blockers = [run for run in runs if run.get("status") == "BLOCKED"]
    decision_lines = [
        "# 选型结论",
        "",
        "当前结论：证据不足，Mem0 与 EverOS 均保留候选资格。",
        "",
        f"已发现 {len(live_effect)} 个效果验证运行、{len(probe_runs)} 个原生复用探针运行。只有两候选完成同一套 decision R0/R1 后，才能进入全量 40 用例；P-native 不参与效果排名。",
    ]
    if live_effect:
        decision_lines.extend(["", "运行状态："])
        decision_lines.extend(f"- `{run['run_id']}`：{run['status']}" for run in live_effect)
    path = destination / "selection_decision.md"
    path.write_text("\n".join(decision_lines) + "\n", encoding="utf-8")
    created.append(path)

    gap_lines = [
        "# 差距与改造量记录",
        "",
        "| 项目 | Mem0 | EverOS |", "|---|---|---|",
        "| 统一身份与作用域 | 通过 benchmark metadata + 受控 filter 组合映射 | 通过 app/project 物理分区 + 受控读取空间映射 |",
        "| 原生逐消息来源 | metadata 可保留 message IDs，需验证推理更新后的继承行为 | 搜索原生暴露 session，逐消息来源需扩展 |",
        "| direct record | `infer=false` 可用 | memory/add 无对应契约，当前标记 UNSUPPORTED |",
        "| 公共 rerank | benchmark 外置 SiliconFlow rerank | benchmark 外置 SiliconFlow rerank |",
        "| Agent 接入 | 同一 Email Agent bridge | 同一 Email Agent bridge |",
        "",
        "## 源码落点", "",
        "- Mem0：`mem0/memory/main.py` 的 add/search 生命周期、`mem0/llms/openai.py` 的请求参数、`mem0/embeddings/openai.py` 的维度参数；首轮不修改这些文件，shim 位于 benchmark worker。",
        "- EverOS：`src/everos/entrypoints/api/routes/memorize.py`、`memory/search/dto.py` 与 search manager；逐消息来源/direct record 若要原生化会进入核心 DTO 和持久化链。",
        "- Email Agent：`service.py` 的 router/prefetch/context injection/log_interaction 与 `honcho_memory/service.py` 接口；当前采用外部 worker，不修改源码。", "",
        "## 初步工作量区间（乐观/通常/悲观，人日）", "",
        "以下只是源码检查后的低置信估算，必须由 P-native 和联调实耗校正；不同模块存在重叠，不能直接求和承诺总工期。", "",
        "| 模块 | Mem0 | EverOS | 置信度/依据 |", "|---|---:|---:|---|",
        "| 身份与作用域服务 | 2/4/7 | 3/6/10 | 低；两者均无生产认证，EverOS 还需跨 app/project 编排 |",
        "| 逐消息来源链 | 2/4/7 | 5/9/15 | 低；Mem0 可携 metadata，EverOS 搜索 DTO 目前为 session 级 |",
        "| 项目共享与隔离 | 1/3/5 | 2/4/7 | 低；均已有映射原型，需补写权限与审计 |",
        "| 版本/来源时间/as-of | 5/9/15 | 5/10/18 | 低；两者都不能直接满足全部固定时间用例 |",
        "| 案例 direct record | 2/4/7 | 4/8/14 | 低；Mem0 有 infer=false，EverOS 无公开等价写入契约 |",
        "| Email Agent 产品化适配 | 2/4/7 | 2/4/7 | 中低；真实注入点已定位、worker 已启动 |",
        "| 恢复、幂等与回归 | 3/6/10 | 3/6/10 | 低；可靠性运行尚未执行 |", "",
        "因此目前不能支持“2～3 周完成统一平台”的承诺；只能在效果、P-native 与 Agent 结果齐全后重新划定 MVP 复用边界。",
    ]
    path = destination / "gaps_and_effort.md"
    path.write_text("\n".join(gap_lines) + "\n", encoding="utf-8")
    created.append(path)

    integration_runs = [run for run in runs if run.get("suite") == "email-integration"]
    integration_lines = [
        "# Agent 接入验证",
        "",
        "选择 Email Agent：它已有 `MemoryDependencyRouter`、prefetch/context injection 和 append-turn 接口。benchmark 在控制器完成受控检索，再通过独立 worker 将上下文注入真实 AgentScope Agent，无需修改外部源码。",
        "",
        "OpenClaw 本轮不接入：虽然有 memory plugin hooks，但当前目录未安装 node_modules，且接入面明显大于 Email Agent。此判断仅用于缩小验证范围，不构成能力淘汰结论。",
        "",
        "M0（无记忆）、M1（强制检索）、M2（使用 Email Agent 原有 MemoryDependencyRouter）使用新 session；捕获写入与新会话召回分离，评估回答不写回，防止实验自身污染记忆。SMTP/IMAP 使用同签名 stub，禁止真实邮箱副作用。",
    ]
    if integration_runs:
        integration_lines.extend(["", "执行记录："])
        integration_lines.extend(f"- `{run['run_id']}`：{run['status']}；{run.get('error', '见 integration_results.json')}" for run in integration_runs)
    path = destination / "integration_report.md"
    path.write_text("\n".join(integration_lines) + "\n", encoding="utf-8")
    created.append(path)

    blocker_lines = ["# 阻塞项", ""]
    if blockers:
        blocker_lines.extend(f"- `{run['run_id']}`：{run.get('error', '未记录原因')}" for run in blockers)
    else:
        blocker_lines.append("当前产物中没有 BLOCKED 运行。未执行不等于通过。")
    path = destination / "blockers.md"
    path.write_text("\n".join(blocker_lines) + "\n", encoding="utf-8")
    created.append(path)
    return created
