from flytekit.models import qubole


def test_hive_query():
    q = qubole.HiveQuery(query="some query", timeout_sec=10, retry_count=0)
    q2 = qubole.HiveQuery.from_flyte_idl(q.to_flyte_idl())
