#!/usr/bin/env python3
"""prefill_verdicts.py — 人工评审骨架的判定预填管线（去重 + 分层 + LLM 语义判定）。

背景：reports/manual_review_*full*.md 由 make_review_skeletons.py 生成，判定列/理由列/
终判/汇总留空待人工填写。160 个案例 × 判定单元逐条人工写非常耗时。本脚本：

  extract  解析四份 full 评审文件 → reports/prefill/units.json（全部判定单元，含分层）
           + reports/prefill/llm_batch_*.json（需要 LLM 语义判定的单元，分批）。
  apply    合并 机械层/复用层/LLM 判定（reports/prefill/llm_verdicts_*.json）→
           回填评审 md（只改占位单元格与带【AI/【机/【复】标记的单元格，人工笔迹不动），
           插入「预填导航」小节与「预填披露」声明。

分层规则（判定只依据候选实际返回的 hits[].text；everos 单次 0 hits 负例按运行级
机械观察的口径允许补充候选自产 runtime markdown 证据）：
  reuse        与 mem0-r0 已填判定单元（同候选+同命题+同 hit 文本）完全一致 → 直接复用
  mech_0hit    mem0 0 hits：required→不成立，forbidden→未出现（无内容可依据）
  mech_iso     everos 隔离类负例（D02/U05/P04）0 hits：forbidden→未出现（写入空间不在
               检索 principal 可读集合，结论不受索引时序影响）
  mech_literal required 命题全部实词字符被 hit 文本覆盖（字面全包含）→ 成立
  llm          其余（改写/翻译/部分覆盖/forbidden 语义核对/everos 0 hits + md 证据）

用法：
  python3 scripts/prefill_verdicts.py extract
  # …由 Claude subagent 逐批完成 reports/prefill/llm_batch_*.json → llm_verdicts_*.json…
  python3 scripts/prefill_verdicts.py apply [--dry-run]
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
PREFILL = os.path.join(REPORTS, "prefill")
RUNTIME = os.path.join(ROOT, "runtime")

# everos 运行级机械观察认定的隔离类负例（写入空间不在检索 principal 可读集合，
# 0 hits 结论不受索引异步收敛时序影响）
EVEROS_ISOLATION_NEGATIVES = {"D02", "U05", "P04"}

HINT_REQUIRED = "`<成立\\|不成立\\|部分成立>`"
HINT_FORBIDDEN = "`<未出现\\|出现>`"
HINT_REASON = "`<引用 hit 文本依据>`"
HINT_FINAL = "`<PASS|FAIL|维持自动状态>`"
HINT_SUMMARY = "`<PASS\\|FAIL>`"

MARK_RE = re.compile(r"【(AI·[高中低]|机[^】]*|复[^】]*)】")


# ---------------------------------------------------------------- 解析工具

def _content_chars(text: str) -> set[str]:
    return {c for c in re.findall(r"\w", text)}


def _norm_hits(text_lines: list[str]) -> str:
    return "\n".join(l.strip() for l in text_lines if l.strip())


def unit_key(candidate: str, kind: str, prop: str, norm_hits: str) -> str:
    h = hashlib.sha1(f"{candidate}|{kind}|{prop}|{norm_hits}".encode("utf-8")).hexdigest()
    return h[:14]


def parse_review_file(path: str) -> dict:
    """解析一份评审 md → {file, candidate, track, run_id, cases:[...]}。"""
    text = open(path, encoding="utf-8").read()
    lines = text.split("\n")

    m = re.search(r"\| run_id \| `?(\S+?)`? \|", text)
    run_id = m.group(1) if m else os.path.basename(path)
    m = re.search(r"\| 候选 / 轨道 / 套件 \| (\S+) / (\S+) / (\S+) \|", text)
    candidate, track = (m.group(1), m.group(2)) if m else ("?", "?")

    # 案例块边界
    starts = [i for i, l in enumerate(lines) if l.startswith("### 案例 ")]
    ends = []
    for s in starts:
        for j in range(s + 1, len(lines)):
            if lines[j].startswith("### 案例 ") or (lines[j].startswith("## ") and not lines[j].startswith("### ")):
                ends.append(j)
                break
        else:
            ends.append(len(lines))
    # 汇总表 / 归因表位置
    summary_start = next((i for i, l in enumerate(lines) if l.startswith("## 汇总")), None)

    cases = []
    for s, e in zip(starts, ends):
        block = lines[s:e]
        btext = "\n".join(block)
        mh = re.match(r"### 案例 (\S+)：(.*)", block[0])
        cid, title = mh.group(1).strip("`"), mh.group(2).strip()
        ms = re.search(r"\*\*自动判分结果\*\*：(\S+)；hard_failures：(.*)", btext)
        status = ms.group(1) if ms else "?"
        hard = ms.group(2).strip() if ms else ""

        # hit 文本（``` 围栏，位于「候选实际返回的 hit 文本」与「逐命题判定」之间）
        hit_disp, hit_text_lines = [], []
        try:
            h0 = next(i for i, l in enumerate(block) if l.startswith("**候选实际返回的 hit 文本**"))
            h1 = next(i for i, l in enumerate(block) if l.startswith("**逐命题判定**"))
        except StopIteration:
            h0 = h1 = -1
        if h0 >= 0:
            in_fence = False
            for l in block[h0:h1]:
                if l.strip() == "```":
                    in_fence = not in_fence
                    hit_disp.append(l)
                    continue
                if in_fence:
                    hit_disp.append(l)
                    if not l.startswith("[hit "):
                        hit_text_lines.append(l)
        zero_hits = (not hit_text_lines) or ("（0 hits" in btext)

        # 命题行
        rows = []
        for i, l in enumerate(block):
            mr = re.match(r"^\| (\d+) \| (required|forbidden) \| (.*)$", l)
            if not mr:
                continue
            idx, kind, rest = int(mr.group(1)), mr.group(2), mr.group(3)
            # rest = "<prop> | <verdict cell> | <reason cell> |"；verdict 未填时内含转义 \|
            parts = rest.split(" | ")
            if len(parts) < 3:
                continue
            prop = parts[0].strip().strip("`")
            vcell, rcell = parts[1].strip(), parts[2].strip().rstrip("|").strip()
            unfilled_v = "\\|" in vcell
            verdict = vcell.strip("`<> ") if not unfilled_v else ""
            reason = rcell.strip("`<> ") if "\\|" not in rcell and "引用 hit 文本依据" not in rcell else ""
            rows.append({
                "line": s + i, "idx": idx, "kind": kind, "prop": prop,
                "filled": not unfilled_v and bool(verdict),
                "verdict": verdict, "reason": reason,
                "ai_marked": bool(MARK_RE.search(rcell)),
            })

        # 终判行
        final_line = final_verdict = None
        final_filled = False
        for i, l in enumerate(block):
            if l.startswith("**本案例人工终判**："):
                final_line = s + i
                mv = re.search(r"`<([^>]*)>`", l)
                if mv:
                    v = mv.group(1)
                    final_filled = "|" not in v
                    final_verdict = v if final_filled else ""
                break

        cases.append({
            "cid": cid, "title": title, "status": status, "hard_failures": hard,
            "zero_hits": zero_hits, "hits_display": "\n".join(hit_disp),
            "norm_hits": _norm_hits(hit_text_lines), "rows": rows,
            "final_line": final_line, "final_filled": final_filled,
            "final_verdict": final_verdict,
            "block_range": (s, e),
        })

    # 汇总表行
    summary_rows = []
    if summary_start is not None:
        for i in range(summary_start, len(lines)):
            mr = re.match(r"^\| (\S+) \| (\S+) \| (.*) \| (.*) \|$", lines[i])
            if mr and mr.group(1) != "case_id" and mr.group(2) != "---":
                summary_rows.append({"line": i, "cid": mr.group(1), "status": mr.group(2),
                                     "verdict_cell": mr.group(3), "note": mr.group(4)})
    # 归因表未填结论数
    attr_unfilled = text.count("`<评审人填写>`")
    has_nav = "## 预填导航" in text
    has_disclosure = "**预填披露**" in text

    return {
        "file": path, "run_id": run_id, "candidate": candidate, "track": track,
        "cases": cases, "summary_rows": summary_rows, "attr_unfilled": attr_unfilled,
        "has_nav": has_nav, "has_disclosure": has_disclosure, "lines": lines,
    }


def review_files() -> list[str]:
    return [p for p in sorted(glob.glob(os.path.join(REPORTS, "manual_review_*.md")))
            if "TEMPLATE" not in p]


def everos_md_evidence(run_id: str, cid: str) -> str:
    """收集 everos 某案例的候选自产 runtime markdown（episodes）作为补充证据。"""
    pat = os.path.join(RUNTIME, run_id, f"bench-*-{cid.lower()}-*", "*", "users", "*", "episodes", "*.md")
    chunks = []
    for p in sorted(glob.glob(pat)):
        rel = p.split(f"{run_id}/", 1)[-1]
        body = open(p, encoding="utf-8").read().strip()
        chunks.append(f"--- {rel} ---\n{body}")
    out = "\n".join(chunks)
    return out[:4000]


# ---------------------------------------------------------------- extract

def classify(parsed_files: list[dict]) -> tuple[dict, dict]:
    """构建判定单元表并分层。返回 (units, reused_verdicts)。"""
    # 第一遍：收集已填判定供复用（人工笔迹优先于 AI 标记笔迹）
    reused: dict[str, dict] = {}
    for pf in parsed_files:
        for c in pf["cases"]:
            for r in c["rows"]:
                if not r["filled"]:
                    continue
                k = unit_key(pf["candidate"], r["kind"], r["prop"], c["norm_hits"])
                m = MARK_RE.search(r["reason"])
                conf = "高"
                if r["ai_marked"] and m:
                    mm = re.match(r"AI·([高中低])", m.group(1))
                    conf = mm.group(1) if mm else "中"
                entry = {"verdict": r["verdict"],
                         "reason": MARK_RE.sub("", r["reason"]).strip("；; "),
                         "src": f"{pf['candidate']}-{pf['track']}", "confidence": conf}
                if k not in reused or (not r["ai_marked"] and reused[k].get("ai")):
                    entry["ai"] = r["ai_marked"]
                    reused[k] = entry

    units: dict[str, dict] = {}
    for pf in parsed_files:
        cand, track = pf["candidate"], pf["track"]
        for c in pf["cases"]:
            for r in c["rows"]:
                k = unit_key(cand, r["kind"], r["prop"], c["norm_hits"])
                u = units.setdefault(k, {
                    "key": k, "kind": r["kind"], "prop": r["prop"],
                    "hits_display": c["hits_display"], "norm_hits": c["norm_hits"],
                    "zero_hits": c["zero_hits"], "candidate": cand,
                    "cids": [], "occurrences": [], "md_evidence": "",
                })
                if f"{c['cid']}[{cand}-{track}]" not in u["cids"]:
                    u["cids"].append(f"{c['cid']}[{cand}-{track}]")
                u["occurrences"].append({"file": pf["file"], "cid": c["cid"], "row": r["idx"],
                                         "filled": r["filled"], "ai_marked": r["ai_marked"]})

    # 分层
    for k, u in units.items():
        cand, kind, prop = u["candidate"], u["kind"], u["prop"]
        cids = {o["cid"] for o in u["occurrences"]}
        if k in reused:
            u["tier"] = "reuse"
            u["verdict"] = reused[k]["verdict"]
            u["reason"] = reused[k]["reason"] or prop
            u["confidence"] = reused[k]["confidence"]
            u["src"] = reused[k]["src"]
            continue
        if u["zero_hits"] and cand == "mem0":
            u["tier"] = "mech_0hit"
            u["verdict"] = "不成立" if kind == "required" else "未出现"
            u["reason"] = "0 hits——候选未返回任何内容"
            u["confidence"] = "高"
            continue
        if u["zero_hits"] and cand == "everos" and cids <= EVEROS_ISOLATION_NEGATIVES and kind == "forbidden":
            u["tier"] = "mech_iso"
            u["verdict"] = "未出现"
            u["reason"] = "0 hits；隔离类负例（写入空间不在检索 principal 可读集合），结论不受索引时序影响"
            u["confidence"] = "高"
            continue
        if kind == "required" and u["norm_hits"]:
            chars = _content_chars(prop)
            if chars and chars <= _content_chars(u["norm_hits"]):
                u["tier"] = "mech_literal"
                u["verdict"] = "成立"
                u["reason"] = f"字面全包含：hit「{u['norm_hits'].splitlines()[0][:50]}」覆盖命题全部实词字符"
                u["confidence"] = "高"
                continue
        u["tier"] = "llm"
        if u["zero_hits"] and cand == "everos":
            # 单次即时检索 0 hits：按运行级机械观察口径，附候选自产 md 作补充证据
            md = ""
            for pf in parsed_files:
                if pf["candidate"] == "everos":
                    for cid in sorted(cids):
                        md += everos_md_evidence(pf["run_id"], cid) + "\n"
            u["md_evidence"] = md.strip()[:6000]
            u["tier"] = "llm_md"

    return units, reused


def cmd_extract(batch_size: int) -> int:
    os.makedirs(PREFILL, exist_ok=True)
    parsed = [parse_review_file(f) for f in review_files()]
    units, reused = classify(parsed)

    by_tier = defaultdict(int)
    for u in units.values():
        by_tier[u["tier"]] += 1

    llm_units = [u for u in units.values() if u["tier"] in ("llm", "llm_md")]
    llm_units.sort(key=lambda u: (u["candidate"], u["cids"][0], u["kind"]))
    n_batches = max(1, math.ceil(len(llm_units) / batch_size)) if llm_units else 0
    for old in glob.glob(os.path.join(PREFILL, "llm_batch_*.json")) + glob.glob(os.path.join(PREFILL, "llm_verdicts_*.json")):
        os.remove(old)
    for b in range(n_batches):
        chunk = llm_units[b * batch_size:(b + 1) * batch_size]
        payload = [{
            "key": u["key"], "kind": u["kind"], "prop": u["prop"],
            "candidate": u["candidate"], "cases": u["cids"],
            "hits": u["hits_display"] or "（0 hits——候选未返回任何内容）",
            "md_evidence": u.get("md_evidence", ""),
        } for u in chunk]
        with open(os.path.join(PREFILL, f"llm_batch_{b:02d}.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)

    with open(os.path.join(PREFILL, "units.json"), "w", encoding="utf-8") as f:
        json.dump({"units": units}, f, ensure_ascii=False, indent=1)

    total_rows = sum(len(r) for pf in parsed for c in pf["cases"] for r in [c["rows"]])
    print(f"文件数: {len(parsed)}  命题行总数: {total_rows}  唯一判定单元: {len(units)}")
    for t in ("reuse", "mech_0hit", "mech_iso", "mech_literal", "llm", "llm_md"):
        print(f"  {t:12s}: {by_tier.get(t, 0)}")
    print(f"LLM 批次: {n_batches} × ≤{batch_size} → reports/prefill/llm_batch_*.json")
    return 0


# ---------------------------------------------------------------- apply

VERDICT_MARK = {"llm": "AI", "llm_md": "AI", "mech_0hit": "机·0hits", "mech_iso": "机·隔离负例",
                "mech_literal": "机·字面全包含", "reuse": "复"}


def _mark(u: dict, verdict_src: str) -> str:
    if verdict_src == "reuse":
        return f"【复·{u.get('src', '')}】"
    if verdict_src in ("llm", "llm_md"):
        return f"【AI·{u.get('confidence', '中')}】"
    return f"【{VERDICT_MARK[verdict_src]}】"


def case_final_suggestion(c: dict, row_verdicts: list[dict]) -> tuple[str, str, str]:
    """返回 (终判建议, 理由, 标记类别 me|ai|human)。"""
    if c["status"] == "UNSUPPORTED":
        return "FAIL", "维持自动状态：契约缺口（UNSUPPORTED，能力不支持）", "me"
    if c["status"] == "FAIL":
        return "FAIL", "维持 FAIL：归因见「FAIL / UNSUPPORTED 归因复核」表", "me"
    # REVIEW_REQUIRED：全部 required 成立 且 forbidden 未出现 → PASS
    confs = [v.get("confidence", "中") for v in row_verdicts if v.get("src") in ("llm", "llm_md")]
    mark = "ai" if confs else "me"
    if not row_verdicts:
        return "PASS", "无语义命题，机械检查已通过（REVIEW_REQUIRED 仅因需人工确认）", "me"
    bad = [v for v in row_verdicts
           if (v["kind"] == "required" and v["verdict"] != "成立")
           or (v["kind"] == "forbidden" and v["verdict"] != "未出现")]
    partial = [v for v in row_verdicts if v["verdict"] == "部分成立"]
    lowconf = [v for v in row_verdicts if v.get("confidence") in ("中", "低") and v.get("src") in ("llm", "llm_md")]
    if bad:
        props = "、".join(f"#{v['row']}{v['kind']}={v['verdict']}" for v in bad)
        return "FAIL", f"语义判定未全满足：{props}", mark
    note = ""
    if partial:
        note = "（含部分成立，需人工定夺）"
    if lowconf:
        note += f"（{len(lowconf)} 条中/低置信度，需重点复核）"
    return "PASS", f"全部 required 成立、forbidden 未出现{note}", mark


def cmd_apply(dry: bool) -> int:
    units_path = os.path.join(PREFILL, "units.json")
    if not os.path.exists(units_path):
        print("缺少 reports/prefill/units.json，请先运行 extract", file=sys.stderr)
        return 1
    units = json.load(open(units_path, encoding="utf-8"))["units"]

    # 合并 LLM 判定
    llm_verdicts: dict[str, dict] = {}
    missing = []
    for p in sorted(glob.glob(os.path.join(PREFILL, "llm_verdicts_*.json"))):
        for v in json.load(open(p, encoding="utf-8")):
            llm_verdicts[v["key"]] = v
    for k, u in units.items():
        if u["tier"] in ("llm", "llm_md"):
            if k in llm_verdicts:
                u["verdict"] = llm_verdicts[k]["verdict"]
                u["reason"] = llm_verdicts[k]["reason"]
                u["confidence"] = llm_verdicts[k].get("confidence", "中")
            else:
                missing.append((k, u["cids"]))
    if missing:
        print(f"警告：{len(missing)} 个 LLM 单元缺少判定（将保留占位）：", file=sys.stderr)
        for k, cids in missing[:20]:
            print(f"  {k} {cids}", file=sys.stderr)

    for path in review_files():
        pf = parse_review_file(path)
        lines = pf["lines"]
        cand, track = pf["candidate"], pf["track"]
        stats = defaultdict(int)
        focus: list[str] = []
        edits: dict[int, str] = {}   # line_idx -> new line

        case_row_verdicts: dict[str, list[dict]] = defaultdict(list)
        final_sugg: dict[str, tuple[str, str, str]] = {}

        for c in pf["cases"]:
            for r in c["rows"]:
                k = unit_key(cand, r["kind"], r["prop"], c["norm_hits"])
                u = units.get(k)
                if u is None or "verdict" not in u:
                    continue
                src = "llm" if u["tier"] in ("llm", "llm_md") else u["tier"]
                case_row_verdicts[c["cid"]].append({
                    "row": r["idx"], "kind": r["kind"], "verdict": u["verdict"],
                    "confidence": u.get("confidence", "高"), "src": src, "tier": u["tier"],
                })
                if r["filled"] and (not r["ai_marked"] or r["verdict"] == u.get("verdict")):
                    continue  # 人工笔迹、或已填且判定一致（保留原标记，幂等）
                mark = _mark(u, src)
                reason = f"{mark}{u['reason']}"
                if u["tier"] == "llm_md":
                    reason += "；含候选自产 md 补充证据"
                newline = (f"| {r['idx']} | {r['kind']} | {r['prop']} | "
                           f"`<{u['verdict']}>` | `<{reason}>` |")
                edits[r["line"]] = newline
                stats[src if src != "reuse" else "reuse"] += 1
                # 重点复核清单
                need = None
                if u["verdict"] == "部分成立":
                    need = "部分成立"
                elif u["kind"] == "forbidden" and u["verdict"] == "出现":
                    need = "forbidden 判为出现"
                elif u.get("confidence") == "低":
                    need = "低置信度"
                elif u.get("confidence") == "中" and src in ("llm", "llm_md"):
                    need = "中置信度"
                elif u["tier"] == "llm_md":
                    need = "0 hits，依据候选自产 md 判定"
                if need:
                    focus.append(f"{c['cid']} #{r['idx']}（{u['kind']}「{u['prop'][:24]}」→ {u['verdict']}：{need}）")

            # 终判
            if c["final_line"] is not None and c["final_filled"]:
                fl = lines[c["final_line"]]
                mr = re.search(r"`<(\w+)>`（(.*?)）\s*$", fl)
                v = mr.group(1) if mr else c["final_verdict"]
                why = mr.group(2) if mr else "已有判定（前期填写）"
                mark_cat = "ai" if "【AI" in why else "me"
                final_sugg[c["cid"]] = (v, why, mark_cat)
            elif c["final_line"] is not None and (not c["rows"] or len(case_row_verdicts[c["cid"]]) == len(c["rows"])):
                rv = case_row_verdicts[c["cid"]]
                v, why, mark_cat = case_final_suggestion(c, rv)
                tag = "【机】" if mark_cat == "me" else f"【AI·{max((x['confidence'] for x in rv if x['src'] == 'llm'), default='高', key='高中低'.index)}】"
                edits[c["final_line"]] = f"**本案例人工终判**：`<{v}>`（{tag}{why}）"
                final_sugg[c["cid"]] = (v, why, mark_cat)
                stats["final"] += 1
                if v == "FAIL" and c["status"] == "REVIEW_REQUIRED":
                    focus.append(f"{c['cid']}（REVIEW_REQUIRED → 建议改判 FAIL：{why}）")
                if any(x.get("confidence") in ("中", "低") for x in rv if x["src"] in ("llm", "llm_md")) and c["status"] != "FAIL":
                    focus.append(f"{c['cid']}（终判含中/低置信度命题，请重点复核）")

        # 汇总表
        for sr in pf["summary_rows"]:
            fs = final_sugg.get(sr["cid"])
            rewritable = HINT_SUMMARY in sr["verdict_cell"] or sr["note"].startswith(("【AI】", "【机】"))
            if fs and rewritable:
                tag = "" if fs[1].startswith("【") else ("【机】" if fs[2] == "me" else "【AI】")
                edits[sr["line"]] = f"| {sr['cid']} | {sr['status']} | `{fs[0]}` | {tag}{fs[1]} |"

        # 预填导航小节（插在「## 运行级机械观察」之前，或「## 逐案例评审」之前）
        anchor = next((i for i, l in enumerate(lines) if l.startswith("## 运行级机械观察")),
                      next((i for i, l in enumerate(lines) if l.startswith("## 逐案例评审")), None))
        nav = ["## 预填导航（脚本+LLM 预填，供人工复核）", ""]
        nav.append(f"判定来源统计：AI 语义判定 {stats['llm']} 条，复用（{cand}-r0 已填同款单元）{stats['reuse']} 条，"
                   f"机械层 {stats['mech_0hit'] + stats['mech_iso'] + stats['mech_literal']} 条"
                   f"（0 hits {stats['mech_0hit']}／隔离负例 {stats['mech_iso']}／字面全包含 {stats['mech_literal']}），"
                   f"终判建议 {stats['final']} 条。")
        nav.append("标记说明：【AI·高/中/低】LLM 语义判定及置信度；【机·…】机械可证；【复·…】跨文件复用同款判定。"
                   "所有预填均为建议，人工确认后请去掉尖括号 `<>`；改判直接覆盖并删标记。")
        nav.append("")
        nav.append(f"**建议复核顺序**：先看下面 {len(set(f.split(' ')[0] for f in focus))} 个重点案例，再抽查高置信度条目。")
        nav.append("")
        seen = set()
        for f in focus:
            if f not in seen:
                seen.add(f)
                nav.append(f"- {f}")
        if pf["attr_unfilled"]:
            nav.append(f"- 归因表尚有 {pf['attr_unfilled']} 处 `<评审人填写>` 结论未预填（需人工）")
        nav += ["", ""]
        insert_nav = (anchor is not None and not pf["has_nav"])

        # 预填披露（插在「**评审声明**」段之前）
        decl = next((i for i, l in enumerate(lines) if l.startswith("**评审声明**")), None)
        disclosure = [
            "**预填披露**：本文件的逐命题判定、理由与终判建议由 `scripts/prefill_verdicts.py`",
            "（机械层）与 LLM 语义判定（标记【AI·置信度】）预填，跨轨道相同判定单元已复用",
            "（标记【复】）；判定输入仅为候选实际返回的 hits[].text（everos 单次 0 hits 负例",
            "另附候选自产 runtime markdown 补充证据），未引入候选未暴露的 harness 侧信息。",
            "预填仅为建议：评审人须按「预填导航」逐条复核并确认或改判（确认后去掉",
            "尖括号与标记），最终判定以下方签名为准。",
            "",
        ]
        insert_disc = (decl is not None and not pf["has_disclosure"])

        # 重建输出
        out_lines = []
        for i, l in enumerate(lines):
            if insert_nav and i == anchor:
                out_lines.extend(nav)
            if insert_disc and i == decl:
                out_lines.extend(disclosure)
            out_lines.append(edits[i] if i in edits and edits[i] is not None else l)

        print(f"{os.path.basename(path)}: 命题 {sum(v for k, v in stats.items() if k.startswith(('llm','mech','reuse')))} 条、"
              f"终判 {stats['final']} 条、汇总 {len(pf['summary_rows'])} 行、重点复核 {len(seen)} 项"
              f"{'（dry-run，未写盘）' if dry else ''}")
        if not dry:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(out_lines))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_ex = sub.add_parser("extract")
    p_ex.add_argument("--batch-size", type=int, default=20)
    p_ap = sub.add_parser("apply")
    p_ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cmd == "extract":
        return cmd_extract(args.batch_size)
    if args.cmd == "apply":
        return cmd_apply(args.dry_run)
    return 2


if __name__ == "__main__":
    sys.exit(main())
