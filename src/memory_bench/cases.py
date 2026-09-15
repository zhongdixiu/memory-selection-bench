from __future__ import annotations

from collections import Counter
from pathlib import Path

import yaml

from .contracts import Case, Principal


EXPECTED_GROUPS = {
    "fact": "F",
    "negative": "N",
    "user": "U",
    "domain": "D",
    "project": "P",
    "conflict": "C",
    "temporal": "T",
    "experience": "E",
}


def load_cases(path: str | Path) -> list[Case]:
    with Path(path).open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    return [Case.model_validate(item) for item in raw.get("cases", [])]


def load_principals(path: str | Path) -> dict[str, Principal]:
    with Path(path).open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}
    principals = [Principal.model_validate(item) for item in raw.get("principals", [])]
    return {item.id: item for item in principals}


def validate_suite(cases: list[Case], principals: dict[str, Principal]) -> list[str]:
    errors: list[str] = []
    ids = [case.id for case in cases]
    duplicates = [item for item, count in Counter(ids).items() if count > 1]
    if duplicates:
        errors.append(f"duplicate case ids: {duplicates}")
    if len(cases) != 40:
        errors.append(f"expected 40 cases, found {len(cases)}")
    counts = Counter(case.group for case in cases)
    for group in EXPECTED_GROUPS:
        if counts[group] != 5:
            errors.append(f"group {group} expected 5 cases, found {counts[group]}")
    for case in cases:
        if not case.id.startswith(EXPECTED_GROUPS[case.group]):
            errors.append(f"{case.id}: id does not match group {case.group}")
        for op in case.operations:
            if op.principal_id and op.principal_id not in principals:
                errors.append(f"{case.id}: unknown principal {op.principal_id}")
            for message in op.messages:
                if not (message.occurred_at.endswith("Z") or "+" in message.occurred_at[10:]):
                    errors.append(f"{case.id}/{message.message_id}: occurred_at needs timezone")
    return errors

