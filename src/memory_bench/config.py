from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    if not isinstance(value, dict):
        raise ValueError(f"expected mapping in {path}")
    return value


def load_dotenv(path: str | Path | None = None) -> list[str]:
    """Load KEY=VALUE pairs from a .env file into os.environ.

    Dependency-free on purpose so the controller behaves identically in any
    environment. Existing environment variables always win, so an explicit
    ``export`` in the shell overrides the file. Returns the variable names set.
    """
    target = Path(path or PROJECT_ROOT / ".env")
    if not target.is_file():
        return []
    loaded: list[str] = []
    for raw_line in target.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()
        name, _, value = line.partition("=")
        name = name.strip()
        if not name or name in os.environ:
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[name] = value
        loaded.append(name)
    return loaded


def load_bench_config(path: str | Path | None = None) -> dict[str, Any]:
    selected = Path(path or os.getenv("MEMORY_BENCH_CONFIG") or PROJECT_ROOT / "configs/bench.yaml")
    config = load_yaml(selected)
    config["_path"] = str(selected.resolve())
    return config


def public_config(config: dict[str, Any]) -> dict[str, Any]:
    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                key: ("<redacted>" if "key" in key.lower() and key != "api_key_env" else clean(item))
                for key, item in value.items()
            }
        if isinstance(value, list):
            return [clean(item) for item in value]
        return value

    return clean(config)


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def require_secret(config: dict[str, Any], provider: str) -> str:
    env_name = config["providers"][provider]["api_key_env"]
    value = os.getenv(env_name, "").strip()
    if not value:
        raise RuntimeError(f"missing environment variable: {env_name}")
    return value

