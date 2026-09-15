from memory_bench.cases import load_cases, load_principals, validate_suite
from memory_bench.config import PROJECT_ROOT
from memory_bench.runner import DECISION_CASE_IDS, P_NATIVE_CASE_IDS, select_cases


def test_complete_suite_is_valid():
    cases = load_cases(PROJECT_ROOT / "data/cases.yaml")
    principals = load_principals(PROJECT_ROOT / "data/principals.yaml")
    assert len(cases) == 40
    assert validate_suite(cases, principals) == []


def test_suite_selection_is_explicit_and_stable():
    cases = load_cases(PROJECT_ROOT / "data/cases.yaml")
    assert [item.id for item in select_cases(cases, "decision")] == list(DECISION_CASE_IDS)
    assert [item.id for item in select_cases(cases, "probe")] == list(P_NATIVE_CASE_IDS)
    assert [item.id for item in select_cases(cases, "smoke")] == ["F02"]
