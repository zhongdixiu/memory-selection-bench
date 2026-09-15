from __future__ import annotations

from dataclasses import dataclass, field

from .contracts import AssertionSpec, SearchHit, Status


@dataclass
class Evaluation:
    status: Status
    hard_failures: list[str] = field(default_factory=list)
    review_items: list[str] = field(default_factory=list)
    matched_required_tokens: list[str] = field(default_factory=list)


def evaluate_hits(hits: list[SearchHit], spec: AssertionSpec) -> Evaluation:
    text = "\n".join(hit.text for hit in hits)
    failures: list[str] = []
    matched: list[str] = []
    for token in spec.required_tokens:
        if token in text:
            matched.append(token)
        else:
            failures.append(f"missing required token: {token}")
    for token in spec.forbidden_tokens:
        if token in text:
            failures.append(f"found forbidden token: {token}")

    if spec.source_check != "none" and hits:
        available = {ref for hit in hits for ref in (hit.source_refs or [])}
        expected = set(spec.source_message_ids)
        if spec.source_check == "any" and expected and not (available & expected):
            failures.append("no expected native source reference found")
        if spec.source_check == "per_claim" and expected and not expected.issubset(available):
            failures.append("native source references are incomplete")

    reviews = [f"required: {item}" for item in spec.required_propositions]
    reviews.extend(f"forbidden: {item}" for item in spec.forbidden_propositions)
    if failures:
        status = Status.FAIL
    elif reviews:
        status = Status.REVIEW_REQUIRED
    else:
        status = Status.PASS
    return Evaluation(status=status, hard_failures=failures, review_items=reviews, matched_required_tokens=matched)

