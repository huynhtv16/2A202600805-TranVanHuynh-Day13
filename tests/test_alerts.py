from app.alerts import _evaluate_condition


def test_evaluate_condition_firing() -> None:
    result = _evaluate_condition("latency_p95_ms > 2500 for 1m", {"latency_p95_ms": 2650.0})
    assert result["matched"] is True
    assert result["status"] == "firing"


def test_evaluate_condition_ok() -> None:
    result = _evaluate_condition("error_rate_pct > 5 for 1m", {"error_rate_pct": 0.0})
    assert result["matched"] is True
    assert result["status"] == "ok"
