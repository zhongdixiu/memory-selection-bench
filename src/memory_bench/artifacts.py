from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: ("<redacted>" if _is_secret_key(key) else redact(item))
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def _is_secret_key(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return normalized in {
        "api_key",
        "authorization",
        "access_token",
        "refresh_token",
        "id_token",
        "secret",
        "client_secret",
    } or normalized.endswith("_api_key")


class ArtifactWriter:
    def __init__(self, root: Path, run_id: str) -> None:
        self.run_dir = root / run_id
        self.run_dir.mkdir(parents=True, exist_ok=False)
        self.events_path = self.run_dir / "events.jsonl"

    def write_json(self, name: str, value: Any) -> Path:
        path = self.run_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(redact(value), ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def event(self, kind: str, payload: Any) -> None:
        record = {"observed_at": utc_now(), "kind": kind, "payload": redact(payload)}
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
