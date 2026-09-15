from memory_bench.contracts import AssertionSpec, SearchHit, Status
from memory_bench.evaluation import evaluate_hits


def hit(text: str, refs=None) -> SearchHit:
    return SearchHit(native_id="n1", text=text, source_refs=refs, observed_at="2026-09-14T00:00:00Z")


def test_hard_tokens_and_native_source_are_checked():
    spec = AssertionSpec(required_tokens=["Python"], forbidden_tokens=["Java"], source_message_ids=["m1"], source_check="any")
    assert evaluate_hits([hit("默认使用 Python", ["m1"])], spec).status == Status.PASS
    evaluation = evaluate_hits([hit("默认使用 Java", ["other"])], spec)
    assert evaluation.status == Status.FAIL
    assert len(evaluation.hard_failures) == 3


def test_semantic_claims_remain_review_required():
    spec = AssertionSpec(required_tokens=["P1"], required_propositions=["用户负责 P1"])
    evaluation = evaluate_hits([hit("P1")], spec)
    assert evaluation.status == Status.REVIEW_REQUIRED
