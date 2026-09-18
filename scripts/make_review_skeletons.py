#!/usr/bin/env python
"""Generate pre-filled manual-review skeletons from run artifacts.

Mechanical evidence (run metadata, hashes, hit texts verbatim, write receipts,
attempt curves, FAIL attributions established in docs/experiment-design.md) is
pre-filled; per-proposition verdicts and final judgments are left blank for the
human reviewer. Never overwrites an existing review file unless --force.

For mem0 runs the script additionally:
- inventories every conversation write that returned PASS with raw.results=[]
  ("extraction skipped") and infers the likely cause per write:
    * curated attribution (CURATED_WRITE_NOTES, from manual tracing of the
      locked mem0 2.0.20 pipeline — see docs/experiment-design.md), or
    * literal-overlap suspects: same-owner memories stored by *preceding*
      cases in run order, scored by CJK/alnum bigram overlap with the
      dropped message (mem0's dedup retrieval filters only on user_id and
      ignores namespace/domain/project metadata, so any earlier equivalent
      memory suppresses the write), or
    * no suspect found → extraction miss or weak-semantic-equivalence drift;
      the note tells the reviewer to compare against the other track's run
      (write path is identical between R0/R1; divergence = nondeterminism).
- links "missing required token" failures to dropped write messages when the
  token occurs in the dropped content (root cause is the write path, not
  retrieval).
- flags "found forbidden token" failures as possible substring artifacts:
  the mechanical check cannot see negation (e.g. a stored denial
  「用户明确否认负责预算」contains the forbidden substring 负责预算).

For everos runs it detects the index-integrity defect established on the full
suite (runs 4a9195d0 / 7d5ce615): the shared LanceDB episode table is keyed
"{user}_ep_{date}_{seq}" with NO app/project component while seq restarts per
space, so a later space's cascade upsert overwrites earlier spaces' rows
(markdown source of truth stays intact). Signature: search attempt curve
[1, 0, 0, ...] (visible on attempt 1, then lost) in cases whose single session
writes to multiple spaces (D01/D04/P02).

Usage:
    python scripts/make_review_skeletons.py <run_id> [<run_id> ...] [--force]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = PROJECT_ROOT / "artifacts"
REPORTS = PROJECT_ROOT / "reports"

# 人工溯源确证、字面重叠推断覆盖不到的空写入归因（键为 "<case_id>:<request_id>"）。
# 依据：本仓 docs/experiment-design.md「Mem0 写路径去重越界发现」与 2026-09-15
# full 套件（9109eb89 / 5ec2c317）逐案人工比对。新 run 若案例构成变化请复核本表。
CURATED_WRITE_NOTES = {
    "P02:p02-w1": "确证去重来源：P01「P1 项目决定优先接入 Email Agent」——跨语言等价（邮件↔Email Agent），字面重叠推断检不出；P01/P02 属不同 project 命名空间仍被吞噬",
    "F04:f04-w1": "确证提取遗漏（非去重）：无前序等价记忆（「对外发送前确认」主题首次出现），R0/R1 双轨稳定复现——提取召回缺陷",
    "U01:u01-w1": "弱语义等价漂移：疑与 F03「邮件回复尽量简洁」被判等价（full R0 存、R1 丢；字面重叠低，推断检不出）——写路径非确定性实例",
}

SUSPECT_THRESHOLD = 0.25


def load_run(run_id: str):
    run_dir = ARTIFACTS / run_id
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    cases = json.loads((run_dir / "case_results.json").read_text(encoding="utf-8"))
    attempts: dict[str, list] = {}
    events_path = run_dir / "events.jsonl"
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            if event.get("kind") == "search_attempt":
                payload = event["payload"]
                key = f"{payload['case_id']}:{payload['request_id']}"
                attempts.setdefault(key, []).append(payload["hit_count"])
    return manifest, cases, attempts


def load_definitions():
    raw = yaml.safe_load((PROJECT_ROOT / "data/cases.yaml").read_text(encoding="utf-8"))
    items = raw["cases"] if isinstance(raw, dict) else raw
    case_defs = {c["id"]: c for c in items}
    raw_p = yaml.safe_load((PROJECT_ROOT / "data/principals.yaml").read_text(encoding="utf-8"))
    plist = raw_p["principals"] if isinstance(raw_p, dict) and "principals" in raw_p else raw_p
    owners = {p["id"]: p.get("owner_user_id", "?") for p in plist}
    return case_defs, owners


def lang_of(text: str) -> str:
    cjk = sum(1 for ch in text if "一" <= ch <= "鿿")
    letters = sum(1 for ch in text if ch.isalpha())
    if letters == 0:
        return "无文字"
    ratio = cjk / letters
    if ratio > 0.1:
        return "中文" if ratio > 0.6 else "中英混合"
    return "英文"


def dig(obj, *path, default=None):
    for key in path:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(key)
        if obj is None:
            return default
    return obj


def _bigrams(text: str) -> set[str]:
    s = re.sub(r"[^\w]", "", text, flags=re.UNICODE)
    return {s[i : i + 2] for i in range(len(s) - 1)}


def infer_suspects(message_content: str, owner: str, preceding: list[tuple[str, str, str, str]]):
    """preceding: (case_id, request_id, owner, memory_text) stored before this write."""
    bg = _bigrams(message_content)
    if not bg:
        return []
    scored = []
    for cid, _rid, ow, text in preceding:
        if ow != owner:
            continue
        overlap = len(bg & _bigrams(text)) / len(bg)
        if overlap >= SUSPECT_THRESHOLD:
            scored.append((round(overlap, 2), cid, text))
    scored.sort(key=lambda x: -x[0])
    return scored[:3]


def build_write_facts(candidate: str, cases: list[dict], owners: dict) -> dict[str, list[dict]]:
    """Per-case write summaries in run order, with dedup-suspect inference.

    Returns {case_id: [ {req, owner, mode, messages, stored, empty, suspects, curated, note} ]}.
    mem0 conversation writes only; other writes are recorded with empty=False.
    """
    facts: dict[str, list[dict]] = {}
    preceding: list[tuple[str, str, str, str]] = []
    for case in cases:
        cid = case["case_id"]
        cw: list[dict] = []
        for op in case["operations"]:
            if op["op"] != "write":
                continue
            req = op["request"]
            r = op["result"]
            rid = req.get("request_id", "?")
            owner = owners.get(req.get("principal_id"), "?")
            mode = req.get("write_mode", "?")
            msgs = [(m.get("message_id"), m.get("content", "")) for m in (req.get("messages") or [])]
            stored: list[str] = []
            empty = False
            suspects: list = []
            if candidate == "mem0" and mode == "conversation" and r.get("status") == "PASS":
                results = dig(r, "raw", "results", default=[])
                stored = [x.get("memory") or "" for x in results]
                if not results:
                    empty = True
                    joined = " ".join(c for _, c in msgs)
                    suspects = infer_suspects(joined, owner, preceding)
            curated = CURATED_WRITE_NOTES.get(f"{cid}:{rid}")
            note = _classify_write(case, curated, suspects) if empty else ""
            cw.append({"req": rid, "owner": owner, "mode": mode, "messages": msgs, "stored": stored, "empty": empty, "suspects": suspects, "curated": curated, "note": note})
            for text in stored:
                preceding.append((cid, rid, owner, text))
        facts[cid] = cw
    return facts


def _classify_write(case: dict, curated: str | None, suspects: list) -> str:
    if curated:
        label = curated
    elif suspects:
        srcs = "；".join(f"{cid}「{text[:26]}」重叠{score:.2f}" for score, cid, text in suspects)
        label = f"疑被前序记忆去重吞噬：{srcs}（去重仅按 user_id，无视 domain/project/namespace metadata）"
    else:
        label = "无字面重叠疑源：提取遗漏或弱语义等价漂移（字符串不可复现的 LLM 判定）——对照另一轨道 run 的同名写入，不一致即为写路径非确定性"
    if case["status"] != "FAIL":
        label = "案例非 FAIL（写入被跳过但未触发机械失败；负例属期望行为，非负例仍须核对语义命题）；" + label
    return label


def write_receipt_lines(candidate: str, op: dict, owner: str, wfact: dict | None = None) -> list[str]:
    r = op["result"]
    rid = op["request"].get("request_id", "?")
    if r.get("status") == "UNSUPPORTED":
        return [f"- write[{rid}]（{owner}）：**UNSUPPORTED**（direct_record 无契约，未发请求）：`{r.get('error','')}`"]
    if candidate == "mem0":
        raw_results = dig(r, "raw", "results", default=[])
        if raw_results:
            mems = "; ".join(f"{x.get('event')}:「{(x.get('memory') or '')[:60]}」" for x in raw_results)
            return [f"- write[{rid}]（{owner}）：PASS，native_ids={len(r.get('native_ids') or [])} 条 → {mems}"]
        extra = f"——{wfact['note']}" if wfact and wfact.get("note") else ""
        return [f"- write[{rid}]（{owner}）：**PASS 但 raw.results=[]（提取跳过，无记忆落库）**{extra}"]
    add_status = dig(r, "raw", "add", "data", "status", default="?")
    flush_status = dig(r, "raw", "flush", "data", "status", default="?")
    return [f"- write[{rid}]（{owner}）：{r.get('status')}，processed={r.get('processed')}（add={add_status} → flush={flush_status}）"]


def _dedup_attribution_row(cid: str, token: str, w: dict) -> dict:
    content = " ".join(c for _, c in w["messages"])
    base = f"期望 token「{token}」对应的写入消息「{content[:30]}」未落库（{w['req']}：write PASS 但 raw.results=[]）"
    if w.get("curated") and "提取遗漏" in w["curated"]:
        return {"case": cid, "cat": "能力层·提取遗漏", "evidence": f"{base}；{w['curated']}", "concl": "维持 FAIL（提取召回缺陷，双轨稳定复现）"}
    if w.get("curated"):
        return {"case": cid, "cat": "能力层·写路径去重越界", "evidence": f"{base}；{w['curated']}", "concl": "维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效）"}
    if w.get("suspects"):
        srcs = "；".join(f"{s_cid}「{text[:26]}」重叠{score:.2f}" for score, s_cid, text in w["suspects"])
        return {"case": cid, "cat": "能力层·写路径去重越界", "evidence": f"{base}；疑源：{srcs}；去重仅按 user_id、无视 domain/project/namespace metadata（experiment-design 隔离映射），且结果依赖案例顺序", "concl": "维持 FAIL（记入能力矩阵：metadata 隔离在写路径失效）"}
    return {"case": cid, "cat": "待定（未落库·疑源待对照）", "evidence": f"{base}；无字面重叠疑源——提取遗漏或弱等价漂移，对照另一轨道 run 同名写入", "concl": "`<评审人填写>`"}


def _case_spaces(case: dict) -> list[str]:
    """Distinct write target spaces (scope kind/id) for a case, in write order."""
    seen = []
    for op in case["operations"]:
        if op["op"] != "write":
            continue
        scope = op["request"].get("requested_scope") or {}
        label = f"{scope.get('kind')}/{scope.get('scope_id')}"
        if label not in seen:
            seen.append(label)
    return seen


def everos_index_collision(case: dict, attempt_map: dict) -> str | None:
    """Return evidence text if the case shows the cross-space episode-id collision signature."""
    spaces = _case_spaces(case)
    if len(spaces) < 2:
        return None
    for op in case["operations"]:
        if op["op"] != "search":
            continue
        curve = attempt_map.get(f"{case['case_id']}:{op['request'].get('request_id')}", [])
        if curve and curve[0] >= 1 and curve[-1] == 0:
            return (f"attempt1 命中 {curve[0]} 条后全部归零（曲线 {curve[:5]}…）；同 session 写入 {len(spaces)} 个空间（{'、'.join(spaces)}）；"
                    "各空间 episode 序号独立计数致同名 ep_<date>_00000001，而共享 LanceDB episode 表主键 {user}_ep_{date}_{seq} 不含空间成分，"
                    "后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好；索引终态可在 runtime/<run>/.index/lancedb 复核）")
    if case["status"] == "FAIL":
        # 次级签名：轮询窗口（≈120s）远超索引收敛（20~40s）仍全程 0 hits，
        # 且案例含多空间写入——覆盖先于收敛完成，本空间索引行从未对检索可见。
        for op in case["operations"]:
            if op["op"] != "search":
                continue
            curve = attempt_map.get(f"{case['case_id']}:{op['request'].get('request_id')}", [])
            if len(curve) >= 4 and all(h == 0 for h in curve):
                return (f"轮询 {len(curve)} 次（≈120s，远超 20~40s 索引收敛窗口）始终 0 hits；同 session 写入 {len(spaces)} 个空间（{'、'.join(spaces)}）；"
                        "覆盖先于索引收敛完成，本空间索引行从未可检索（次级冲突签名；对照另一轨道同案例曲线 [1,0,…]——attempt1 命中后归零，"
                        "runtime markdown 证实两空间 episode 均已提取）；共享 LanceDB 主键 {user}_ep_{date}_{seq} 不含空间成分，"
                        "后完成空间的 cascade upsert 覆盖先前空间的索引行（索引终态可在 runtime/<run>/.index/lancedb 复核）")
    return None


def attribution_rows(candidate: str, case: dict, wfacts: dict, attempt_map: dict) -> list[dict]:
    """Pre-fill established attributions; reviewer may override."""
    cid = case["case_id"]
    rows = []
    writes = [op for op in case["operations"] if op["op"] == "write"]
    searches = [op for op in case["operations"] if op["op"] == "search"]
    if any(op["result"].get("status") == "UNSUPPORTED" for op in writes):
        rows.append({"case": cid, "cat": "契约缺口", "evidence": "write=UNSUPPORTED：memory/add 无 direct_record 对应契约（设计预期）", "concl": "维持 UNSUPPORTED（非运行故障）"})
        return rows
    if case["status"] != "FAIL":
        return rows
    wfacts_case = wfacts.get(cid, [])
    empty_writes = [w for w in wfacts_case if w["empty"]]
    linked_write_reqs: set[str] = set()
    for op in searches:
        ev = op.get("evaluation", {})
        fails = ev.get("hard_failures", [])
        hits = op["result"].get("hits", [])
        hit_langs = sorted({lang_of(h.get("text", "")) for h in hits})
        if any("source reference" in f for f in fails):
            refs = sorted({ref for h in hits for ref in (h.get("source_refs") or [])})
            if candidate == "everos":
                evidence = f"hard_failures 含来源检查失败；hits[].source_refs={refs[:3]}（session 级，raw DTO 无消息级引用；按设计不得用 harness 已知 message ID 补判）"
                concl = "维持 FAIL（已记录 D 类缺口）"
            elif not hits:
                evidence = "0 hits 时来源检查为连带失败（无 hit 可核来源），根因见写路径/召回行"
                concl = "随根因行"
            else:
                evidence = f"hits[].source_refs={refs[:3]} 不含期望 message ID（mem0 为消息级来源）；若期望消息对应的写入未落库（见写路径行），此失败为连带结果；否则需人工核对期望 ID 与写入 message_ids"
                concl = "`<评审人填写>`"
            rows.append({"case": cid, "cat": "能力层·来源粒度（D 类缺口）" if candidate == "everos" else "来源检查失败", "evidence": evidence, "concl": concl})
        for f in fails:
            if not f.startswith("missing required token"):
                continue
            token = f.partition(":")[2].strip()
            matched = [w for w in empty_writes if any(token in (c or "") for _, c in w["messages"])]
            if matched:
                for w in matched:
                    linked_write_reqs.add(w["req"])
                    rows.append(_dedup_attribution_row(cid, token, w))
                continue
            collision = everos_index_collision(case, attempt_map) if candidate == "everos" else None
            if collision:
                rows.append({"case": cid, "cat": "能力层·索引完整性（跨空间 episode id 冲突）", "evidence": f"missing required token: {token}；{collision}", "concl": "维持 FAIL（记入能力矩阵：同用户多空间场景索引行被覆盖，提取与空间路由本身正确）"})
            elif hits and "英文" in hit_langs:
                pure = "hit 文本为英文" if hit_langs == ["英文"] else f"hit 语言混杂（{','.join(hit_langs)}）"
                rows.append({"case": cid, "cat": "能力层·语言合规", "evidence": f"missing required token: {token}；{pure}——缺失 token 疑以英文 hit 表述（如「上海」→\"moved to Shanghai\"）；默认提示词含强制语言一致规则，属共享 LLM 违规；R1 伴随跨语言 rerank 分数坍缩", "concl": "维持 FAIL（记入能力矩阵：中文业务召回不稳定）"})
            elif not hits:
                rows.append({"case": cid, "cat": "待定（0 hits）", "evidence": f"missing required token: {token}；检索 0 命中，看 attempts 曲线区分可见性/召回", "concl": "`<评审人填写>`"})
            else:
                rows.append({"case": cid, "cat": "待定（token 未命中但有 hit）", "evidence": f"missing required token: {token}；hit 语言={','.join(hit_langs)}，需人工比对文本", "concl": "`<评审人填写>`"})
        for f in fails:
            if f.startswith("found forbidden token"):
                token = f.partition(":")[2].strip()
                rows.append({"case": cid, "cat": "待定（疑子串误判·否定表述）", "evidence": f"found forbidden token: {token}；子串判定无法识别否定/更正——若 hit 语义为否认该命题（如「用户明确否认负责预算」），机械 FAIL 属判定方法局限，可按语义改判", "concl": "`<评审人填写：hit 为否定表述则改判 PASS>`"})
    if not rows and empty_writes:
        detail = "；".join(f"{w['req']}：{w['note'][:40]}" for w in empty_writes)
        rows.append({"case": cid, "cat": "待定（FAIL 但机械归因未触发）", "evidence": f"存在未落库写入（{detail}），核对 hard_failures 与写入回执", "concl": "`<评审人填写>`"})
    if not rows:
        fails_all = [f for op in searches for f in op.get("evaluation", {}).get("hard_failures", [])]
        rows.append({"case": cid, "cat": "待定", "evidence": f"hard_failures：{('；'.join(fails_all))[:120] or '（无，FAIL 来自操作级状态）'}", "concl": "`<评审人填写>`"})
    return rows


def render_run_level_observations(candidate: str, cases: list[dict], wfacts: dict, attempt_map: dict) -> list[str]:
    """Auto-generated navigation section: empty-write inventory + forbidden-token flags."""
    status_by_case = {c["case_id"]: c["status"] for c in cases}
    lines: list[str] = []
    if candidate == "mem0":
        empties = [(cid, w) for cid, ws in wfacts.items() for w in ws if w["empty"]]
        if empties:
            lines += [
                "## 运行级机械观察（脚本自动生成，评审导航用）",
                "",
                f"**提取跳过的 conversation 写入（write PASS 但 raw.results=[]），共 {len(empties)} 处**。",
                "根因三分：① 跨案例/跨作用域语义去重（疑源列出）；② 提取遗漏；",
                "③ 边缘等价判定漂移（写路径非确定性——与另一轨道 run 对照，不一致即属此类）。",
                "去重机制：mem0 提取前的重复检索仅按 user_id 过滤，无视 namespace/domain/",
                "project metadata，且 last-messages 上下文跨案例共享（experiment-design 隔离映射）。",
                "",
                "| case[request] | 案例状态 | 未落库消息 | 初判分类与疑源 |",
                "|---|---|---|---|",
            ]
            for cid, w in empties:
                content = " ".join(c for _, c in w["messages"])[:40]
                lines.append(f"| {cid}[{w['req']}] | {status_by_case.get(cid,'?')} | 「{content}」 | {w['note']} |")
            lines.append("")
    if candidate == "everos":
        collisions = [(c["case_id"], everos_index_collision(c, attempt_map)) for c in cases]
        collisions = [(cid, ev) for cid, ev in collisions if ev]
        if collisions:
            lines += [
                "## 运行级机械观察（脚本自动生成，评审导航用）",
                "",
                f"**索引完整性缺陷签名（attempt1 命中后归零），共 {len(collisions)} 例**：{', '.join(cid for cid, _ in collisions)}。",
                "机制：episode 序号按空间独立计数（各空间当日都从 ep_…_00000001 起），而共享 LanceDB",
                "episode 表主键 `{user}_ep_{date}_{seq}` 不含 app/project 成分——同一 session 先后 flush 到",
                "多个空间时，后完成空间的 cascade upsert 覆盖先前空间的索引行（markdown 事实源完好，",
                "提取与空间路由本身正确）。整个 run 终态索引仅 5 行，每个 (user,date,seq) 只剩最后一个写者",
                "（如 U1_ep_20260915_00000001 终归 t05-projects）；其余案例当时可检索只因每案例检索紧跟自身写入、",
                "在下一案例覆盖前完成。同用户同日多空间为产品真实场景，属结构性缺陷，双轨稳定复现。",
                "",
            ]
            for cid, ev in collisions:
                lines.append(f"- **{cid}**：{ev}")
            lines.append("")
        zero_hit_single = []
        for c in cases:
            if c["status"] == "UNSUPPORTED":
                continue  # direct_record 未写入，0 hits 与时序无关
            searches = [op for op in c["operations"] if op["op"] == "search"]
            if searches and all((op.get("attempts") or 1) <= 1 and not op["result"].get("hits") for op in searches):
                zero_hit_single.append(c["case_id"])
        if zero_hit_single:
            lines += [
                f"**单次即时检索且 0 hits 的案例（{len(zero_hit_single)} 个）**：{', '.join(zero_hit_single)}。",
                "方法论披露：everos 索引异步收敛（实测约 20~40s，对照 F03 曲线 [0,0,1,…]），而自动判分仅在",
                "存在硬失败时触发可见性轮询——负例（无 required token）0 hits 不构成硬失败，检索在写入 flush",
                "后约 1s 单次执行即定案。因此这些 0 hits **不能区分「内容级克制」与「索引未就绪」**；runtime",
                "markdown 显示 N 组消息实际全部被提取存储（表述忠实：疑问存为「U1询问…」、否认存为「U1否认…」）。",
                "评审 N 组语义命题时以 hits（主依据）+ 候选自产 md（补充证据）判定，勿把 0 hits 直接当作",
                "「推测未存储」；写入空间不在检索 principal 可读集合的隔离类负例（如 D02/U05/P04）不受时序影响。",
                "候选行为差异备忘：everos 对负例消息的策略是**忠实提取、中性框架**（疑问存为询问、否认存为否认），",
                "而非 mem0 式的整条跳过——两者皆为可辩护的产品行为，评审按语义命题判定而非按「是否存储」判定。",
                "另注意：N03 的 everos episode「U1否认负责预算…」含 forbidden 子串「负责预算」，若检索时索引已收敛",
                "会触发与 mem0 R1 同类的否定子串误判 FAIL；本次因 0 hits 未触发，评审终判时按同一口径处理。",
                "",
            ]
    forbidden_cases = []
    for c in cases:
        for op in c["operations"]:
            for f in op.get("evaluation", {}).get("hard_failures", []):
                if f.startswith("found forbidden token"):
                    forbidden_cases.append(f"{c['case_id']}（{f.partition(':')[2].strip()}）")
    if forbidden_cases:
        lines += [
            f"**『出现禁止 token』FAIL：{', '.join(forbidden_cases)}**——子串判定无法识别否定/更正表述；",
            "若 hit 语义是否认该命题（如「用户明确否认负责预算」包含子串「负责预算」），评审可按语义改判 PASS（理由必填）。",
            "",
        ]
    if lines:
        lines.append("")
    return lines


def render_case(candidate: str, track: str, case: dict, case_def: dict, owners: dict, attempt_map: dict, wfacts: dict) -> str:
    cid = case["case_id"]
    wfacts_case = {w["req"]: w for w in wfacts.get(cid, [])}
    out = ["---", "", f"### 案例 {cid}：{case.get('title', case_def.get('title',''))}", ""]
    ops = case["operations"]
    evals = [op.get("evaluation") for op in ops if op.get("evaluation")]
    all_fails = [f for ev in evals for f in ev.get("hard_failures", [])]
    out.append(f"**自动判分结果**：{case['status']}；hard_failures：{('；'.join(all_fails)) if all_fails else '无'}")
    out.append("")

    # 用例输入
    out.append("**用例输入**（data/cases.yaml，供忠实度对照）：")
    for op_def in case_def.get("operations", []):
        owner = owners.get(op_def.get("principal_id"), op_def.get("principal_id") or "-")
        if op_def.get("op") == "write":
            for m in op_def.get("messages", []):
                out.append(f"- write[{op_def.get('request_id')}]（{owner}，scope={op_def.get('scope_kind')}/{op_def.get('scope_id')}，occurred_at={m.get('occurred_at')}）：「{m.get('content')}」")
        elif op_def.get("op") == "search":
            a = op_def.get("assertions") or {}
            checks = []
            if a.get("required_tokens"): checks.append(f"required_tokens={a['required_tokens']}")
            if a.get("forbidden_tokens"): checks.append(f"forbidden_tokens={a['forbidden_tokens']}")
            if a.get("source_check") and a.get("source_check") != "none": checks.append(f"source_check={a['source_check']} 期望 {a.get('source_message_ids')}")
            out.append(f"- search[{op_def.get('request_id')}]（{owner}）：「{op_def.get('query')}」 机械检查：{'，'.join(checks) or '无'}")
    out.append("")

    # 写入回执（机械核对）
    out.append("**写入回执核对**（机械证据）：")
    for op in ops:
        if op["op"] == "write":
            owner = owners.get(op["request"].get("principal_id"), "?")
            out.extend(write_receipt_lines(candidate, op, owner, wfacts_case.get(op["request"].get("request_id"))))
    out.append("")

    # 检索尝试曲线
    for op in ops:
        if op["op"] == "search":
            key = f"{cid}:{op['request'].get('request_id')}"
            curve = attempt_map.get(key, [])
            out.append(f"**检索尝试曲线**（attempts={op.get('attempts')}）：hits 序列 {curve if curve else '（无事件）'}")
            out.append("")

    # hits 原文
    out.append("**候选实际返回的 hit 文本**（原样粘贴；判定只依据这些内容）：")
    hits = []
    for op in ops:
        if op["op"] == "search":
            hits = op["result"].get("hits", [])
    if not hits:
        out.append("")
        out.append("```")
        out.append("（0 hits——候选未返回任何内容）")
        out.append("```")
    else:
        out.append("")
        for i, h in enumerate(hits, 1):
            dense = dig(h, "native_metadata", "dense_score")
            score_txt = f"score={h.get('score'):.4f}" + (f"，dense={dense:.4f}" if dense is not None and track == "r1" else "")
            out.append("```")
            out.append(f"[hit {i}] {score_txt} source_refs={h.get('source_refs')} 语言={lang_of(h.get('text',''))}")
            out.append(h.get("text", ""))
            out.append("```")
            out.append("")

    # 逐命题判定表
    review_items = [item for ev in evals for item in ev.get("review_items", [])]
    out.append("**逐命题判定**（required 须确认成立，forbidden 须确认不成立；判定与理由由评审人填写）：")
    out.append("")
    if review_items:
        out.append("| # | 类型 | 命题 | 判定 | 理由 |")
        out.append("|---|---|---|---|---|")
        for i, item in enumerate(review_items, 1):
            kind, _, prop = item.partition(":")
            hint = "`<成立\\|不成立\\|部分成立>`" if kind.strip() == "required" else "`<未出现\\|出现>`"
            out.append(f"| {i} | {kind.strip()} | {prop.strip()} | {hint} | `<引用 hit 文本依据>` |")
    else:
        out.append("（本案例无语义命题，仅机械检查——终判可直接依据 hard_failures 与归因表）")
    out.append("")

    # 忠实度备注（机械观察预填）
    out.append("**忠实度备注**（机械观察已预填，评审人补充判断）：")
    notes = []
    if candidate == "mem0":
        notes.append("mem0 hit 为提取改写后的事实句（非原话）；语言对齐 shim 自 2026-09-15 生效，提取应保持中文。")
    else:
        notes.append("everos hit 为 summary/subject/episode 三段拼接，内容重复属正常（artifacts-format §6.2），按整体语义判断。")
    if any(f.startswith("found forbidden token") for f in all_fails):
        notes.append("⚠ hard_failures 含『出现禁止 token』：子串判定无法识别否定/更正表述——若 hit 语义为否认该命题，可人工改判 PASS，理由必填。")
    empty_in_case = [w for w in wfacts_case.values() if w["empty"]]
    if candidate == "mem0" and empty_in_case:
        notes.append("⚠ 本案例有写入未落库（write PASS 但 raw.results=[]，分类见写入回执核对）：若缺失 token 在未落库消息中，FAIL 根因在写路径（去重/提取）而非检索能力；检索 0 hits 是下游连带结果。")
    if candidate == "everos" and everos_index_collision(case, attempt_map):
        notes.append("⚠ 索引完整性缺陷签名：attempt1 曾命中、随后归零（见检索尝试曲线）——episode 已正确提取并写入所属空间的 markdown 事实源，但共享 LanceDB 主键（{user}_ep_{date}_{seq}，不含空间成分）被同 session 另一空间的同名 episode 覆盖。FAIL 根因在索引层，非提取/路由/检索能力；评审可读 runtime 目录 md 原文核对内容忠实度。")
    for op in ops:
        if op["op"] != "search":
            continue
        for h in op["result"].get("hits", []):
            lang = lang_of(h.get("text", ""))
            if candidate == "everos" and lang == "英文":
                notes.append("⚠ 检出英文 episode：默认提示词含强制语言一致规则，此为共享 LLM 违规（能力发现），评审时记录对 token/命题判定的影响。")
                break
            if candidate == "mem0" and lang == "英文":
                notes.append("⚠ 检出英文事实句：shim 生效后不应出现，若确认请检查 worker custom_instructions 并单独归因。")
                break
    if not hits:
        has_forbidden_only = review_items and all(item.startswith("forbidden") for item in review_items)
        if candidate == "everos" and case.get("status") != "UNSUPPORTED" and all((op.get("attempts") or 1) <= 1 for op in ops if op["op"] == "search"):
            notes.append("⚠ everos 0 hits 且 attempts=1：everos 索引异步收敛（实测约 20~40s），无硬失败的检索不触发可见性轮询，本次检索距写入 flush 仅约 1s——0 hits 可能是索引未就绪而非内容不存在。请对照 runtime/<run>/<namespace>-<空间>/users/<owner>/episodes/*.md（候选自产事实源，可作忠实度补充证据）确认提取是否发生及表述框架；若写入空间本就不在检索 principal 可读集合（隔离类负例如 D02/U05/P04），0 hits 结论不受时序影响。")
        elif has_forbidden_only:
            notes.append("0 hits 的负例：需结合上方写入回执确认「应隔离的内容确实已写入但检索不到」（隔离生效），而非「根本没写进去」。")
        elif not empty_in_case:
            notes.append("0 hits：对照写入回执判断是写入未落库（如 mem0 raw.results=[]）还是召回失败。")
    out.extend(f"- {n}" for n in dict.fromkeys(notes))
    out.append("")
    out.append("**本案例人工终判**：`<PASS|FAIL|维持自动状态>`（理由一句话，评审人填写）")
    out.append("")
    return "\n".join(out)


def render_run(run_id: str) -> Path | None:
    manifest, cases, attempt_map = load_run(run_id)
    case_defs, owners = load_definitions()
    candidate = manifest["candidate"]
    track = str(manifest["track"])
    out_path = REPORTS / f"manual_review_{run_id}.md"
    wfacts = build_write_facts(candidate, cases, owners)
    lines = [
        "# 人工语义评审记录",
        "",
        "> 判定只依据 `case_results.json` 中候选实际返回的 `hits[].text`（可参考",
        "> `native_metadata`），禁止引入 harness 已知但候选未返回的信息",
        "> （例如不得用用例里的 message ID 替 EverOS 补成「来源通过」）。",
        "> 本文件由 `scripts/make_review_skeletons.py` 预填机械证据；判定列与终判由评审人填写。",
        "",
        "## 基本信息",
        "",
        "| 项 | 值 |",
        "|---|---|",
        f"| run_id | `{run_id}` |",
        f"| 候选 / 轨道 / 套件 | {candidate} / {track} / {manifest.get('suite')} |",
        f"| 运行时间 | {manifest.get('started_at')} → {manifest.get('finished_at')}（status={manifest.get('status')}） |",
        "| 评审人 | `<姓名>` |",
        "| 评审时间 | `<YYYY-MM-DD HH:MM 时区>` |",
        f"| 证据路径 | `artifacts/{run_id}/case_results.json` |",
        f"| 输入指纹 | case_data_hash=`{str(manifest.get('case_data_hash'))[:12]}` config_hash=`{str(manifest.get('config_hash'))[:12]}` |",
        "",
        "## 评审范围",
        "",
        f"- REVIEW_REQUIRED：{', '.join(c['case_id'] for c in cases if c['status']=='REVIEW_REQUIRED') or '无'}",
        f"- FAIL（需归因复核）：{', '.join(c['case_id'] for c in cases if c['status']=='FAIL') or '无'}",
        f"- UNSUPPORTED：{', '.join(c['case_id'] for c in cases if c['status']=='UNSUPPORTED') or '无'}",
        "",
    ]
    lines += render_run_level_observations(candidate, cases, wfacts, attempt_map)
    lines += ["## 逐案例评审", ""]
    for case in cases:
        lines.append(render_case(candidate, track, case, case_defs.get(case["case_id"], {}), owners, attempt_map, wfacts))
    lines += ["## FAIL / UNSUPPORTED 归因复核", "", "| case_id | 归因类别 | 证据 | 结论 |", "|---|---|---|---|"]
    any_row = False
    for case in cases:
        for row in attribution_rows(candidate, case, wfacts, attempt_map):
            lines.append(f"| {row['case']} | {row['cat']} | {row['evidence']} | {row['concl']} |")
            any_row = True
    if not any_row:
        lines.append("| - | - | - | - |")
    lines += ["", "## 汇总", "", "| case_id | 自动状态 | 人工终判 | 备注 |", "|---|---|---|---|"]
    for case in cases:
        note = {"FAIL": "见归因表", "UNSUPPORTED": "契约缺口", "REVIEW_REQUIRED": "待逐命题判定"}.get(case["status"], "")
        lines.append(f"| {case['case_id']} | {case['status']} | `<PASS\\|FAIL>` | {note} |")
    lines += [
        "",
        "**评审声明**：本人确认以上判定仅基于候选实际返回内容，未使用候选未暴露的",
        "harness 侧信息；同一标准将用于另一候选的对应 run。",
        "",
        "签名：`<姓名>` 日期：`<YYYY-MM-DD>`",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path


def main() -> int:
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv[1:]
    if not args:
        print("usage: make_review_skeletons.py <run_id> [...] [--force]")
        return 2
    for run_id in args:
        out = REPORTS / f"manual_review_{run_id}.md"
        if out.exists() and not force:
            print(f"skip（已存在，避免覆盖人工填写；--force 覆盖）: {out}")
            continue
        path = render_run(run_id)
        print(f"generated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
