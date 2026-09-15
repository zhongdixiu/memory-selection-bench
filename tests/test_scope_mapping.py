from memory_bench.adapters.everos import EverOSAdapter
from memory_bench.adapters.mem0 import Mem0Adapter
from memory_bench.cases import load_principals
from memory_bench.config import PROJECT_ROOT, load_bench_config
from memory_bench.contracts import Track


def test_mem0_read_filters_never_fall_back_to_unfiltered():
    config = load_bench_config()
    principals = load_principals(PROJECT_ROOT / "data/principals.yaml")
    adapter = object.__new__(Mem0Adapter)
    adapter.track = Track.R0
    filters = adapter._filter_sets("ns", principals["principal_u1_mail"])
    assert filters
    assert all(item["user_id"] == "U1" and item["bench_namespace"] == "ns" for item in filters)
    assert adapter._filter_sets("ns", principals["principal_missing"]) == []


def test_everos_authorized_spaces_are_server_side_mapped():
    config = load_bench_config()
    principals = load_principals(PROJECT_ROOT / "data/principals.yaml")
    adapter = object.__new__(EverOSAdapter)
    adapter.track = Track.R0
    spaces = adapter._read_spaces("ns", principals["principal_u1_report"])
    assert ("ns-shared", "ns-default") in spaces
    assert ("ns-domain-report", "ns-default") in spaces
    assert ("ns-projects", "ns-P1") in spaces
    assert ("ns-domain-email", "ns-default") not in spaces
    assert adapter._read_spaces("ns", principals["principal_missing"]) == []
