from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PREFIX = "@@MEMORY_BENCH@@"

# Disclosed aligned-configuration shim (same class as QwenCompatLLM and the
# SiliconFlow embedding shim). Out of the box, mem0's ADDITIVE_EXTRACTION_PROMPT
# (English, with English examples and no language-preservation rule) makes the
# LLM rewrite Chinese input into English facts, which renders Chinese
# required-token assertions unmatchable. EverOS's default episode prompt
# already carries a mandatory "output in the participants' language" rule, so
# leaving mem0 unaligned would confound the single-variable comparison. The
# locked version (2.0.20) exposes no full extraction-prompt replacement port,
# but it does expose the official `MemoryConfig.custom_instructions` field,
# injected as the highest-priority "## Custom Instructions" section of the
# extraction prompt. The text below is mem0's own canonical
# language-preservation wording (verbatim from `use_input_language` in
# mem0/configs/prompts.py, a flag this version defines but never wires up), so
# the shim activates behavior mem0 itself specifies rather than inventing new
# prompt semantics — bringing mem0 to parity with EverOS's out-of-box rule
# state, not beyond it. Out-of-box English-rewrite behavior is preserved as a
# capability finding in the pre-shim runs and the gaps table.
LANGUAGE_ALIGNMENT_INSTRUCTIONS = (
    "CRITICAL: Respond in the SAME LANGUAGE and SCRIPT as the input messages.\n"
    "1. Match the language of the user's messages exactly — if they write in Korean, extract in Korean; Japanese in Japanese; etc.\n"
    "2. Preserve the exact script/alphabet of the input.\n"
    "3. Do NOT translate or transliterate into English unless the input is already in English.\n"
    "4. Maintain all quality standards (contextual richness, temporal grounding, etc.) regardless of language.\n"
    "5. Technical terms, proper nouns, and brand names should be preserved in their original form as used in the input.\n"
    "6. If the input mixes languages (e.g., Hinglish), preserve both the mixed language style AND the script.\n"
    "7. For Japanese: explicitly resolve omitted subjects using conversation context.\n"
    "8. For CJK languages: maintain appropriate formality level from the source text."
)


def emit(payload: dict[str, Any]) -> None:
    print(PREFIX + json.dumps(payload, ensure_ascii=False), flush=True)


def _worker_config(runtime: Path) -> dict[str, Any]:
    """Build the mem0 MemoryConfig dict. Pure config, no mem0 imports, testable."""
    return {
        "version": "v1.1",
        "llm": {
            "provider": "openai",
            "config": {
                "model": os.environ["MEMORY_BENCH_LLM_MODEL"],
                "api_key": os.environ["DASHSCOPE_API_KEY"],
                "openai_base_url": os.environ["MEMORY_BENCH_LLM_BASE_URL"],
                "temperature": 0.0,
                "top_p": 0.1,
                "max_tokens": 2000,
            },
        },
        "embedder": {
            "provider": "openai",
            "config": {
                "model": os.environ["MEMORY_BENCH_EMBED_MODEL"],
                "api_key": os.environ["SILICONFLOW_API_KEY"],
                "openai_base_url": os.environ["MEMORY_BENCH_EMBED_BASE_URL"],
                "embedding_dims": 1024,
            },
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "memory_bench",
                "embedding_model_dims": 1024,
                "path": str(runtime / "qdrant"),
                "on_disk": True,
            },
        },
        "history_db_path": str(runtime / "history.db"),
        "custom_instructions": LANGUAGE_ALIGNMENT_INSTRUCTIONS,
    }


def build_memory():
    from mem0.configs.llms.openai import OpenAIConfig
    from mem0.memory.main import Memory
    from mem0.utils.factory import EmbedderFactory, LlmFactory

    from memory_bench.adapters.mem0_provider import QwenCompatLLM  # noqa: F401  (fail fast if provider module breaks)

    runtime = Path(os.environ["MEMORY_BENCH_RUNTIME_DIR"])
    runtime.mkdir(parents=True, exist_ok=True)
    # Keep the schema-recognized provider name and replace only its factory
    # implementation. MemoryConfig rejects arbitrary provider names before the
    # factory is reached.
    LlmFactory.register_provider(
        "openai",
        "memory_bench.adapters.mem0_provider.QwenCompatLLM",
        OpenAIConfig,
    )
    EmbedderFactory.provider_to_class["openai"] = "memory_bench.adapters.mem0_provider.SiliconFlowEmbedding"
    return Memory.from_config(_worker_config(runtime))


def write(memory, payload: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(payload["metadata"])
    result = memory.add(
        payload["messages"],
        user_id=payload.get("user_id"),
        agent_id=payload.get("agent_id"),
        run_id=payload.get("run_id"),
        metadata=metadata,
        infer=payload.get("infer", True),
    )
    native_ids = [str(item.get("id")) for item in result.get("results", []) if item.get("id")]
    return {"raw": result, "native_ids": native_ids}


def search(memory, payload: dict[str, Any]) -> dict[str, Any]:
    by_id: dict[str, dict[str, Any]] = {}
    for filters in payload["filter_sets"]:
        result = memory.search(
            payload["query"],
            top_k=payload["top_k"],
            filters=filters,
            threshold=0.0,
            rerank=False,
        )
        for item in result.get("results", []):
            item_id = str(item.get("id") or item.get("memory") or len(by_id))
            existing = by_id.get(item_id)
            if existing is None or float(item.get("score") or 0.0) > float(existing.get("score") or 0.0):
                by_id[item_id] = item
    ranked = sorted(by_id.values(), key=lambda item: float(item.get("score") or 0.0), reverse=True)
    return {"results": ranked[: payload["top_k"]]}


def inspect(memory, payload: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for filters in payload["filter_sets"]:
        result = memory.get_all(filters=filters, limit=100, show_expired=True)
        rows.extend(result.get("results", []))
    return {"results": rows}


def main() -> int:
    os.environ.setdefault("MEM0_TELEMETRY", "false")
    try:
        memory = build_memory()
    except Exception as exc:
        emit({"ok": False, "fatal": True, "error": str(exc), "traceback": traceback.format_exc()})
        return 1
    emit({"ok": True, "ready": True, "observed_at": datetime.now(timezone.utc).isoformat()})
    for line in sys.stdin:
        try:
            command = json.loads(line)
            name = command["command"]
            if name == "health":
                data = {"status": "ok"}
            elif name == "write":
                data = write(memory, command["payload"])
            elif name == "search":
                data = search(memory, command["payload"])
            elif name == "inspect":
                data = inspect(memory, command["payload"])
            elif name == "close":
                emit({"ok": True, "data": {"closed": True}})
                return 0
            else:
                raise ValueError(f"unknown command: {name}")
            emit({"ok": True, "data": data})
        except Exception as exc:
            emit({"ok": False, "error": str(exc), "traceback": traceback.format_exc()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
