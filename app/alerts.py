from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .logging_config import get_logger
from .metrics import snapshot

ALERT_RULES_PATH = Path("config/alert_rules.yaml")
_LAST_STATUS: dict[str, str] = {}
log = get_logger()

CONDITION_RE = re.compile(
    r"^(?P<metric>[a-zA-Z0-9_]+)\s*(?P<operator>>=|<=|>|<|==)\s*(?P<threshold>[0-9]+(?:\.[0-9]+)?)(?:\s+for\s+(?P<window>[0-9]+[smhd]))?$"
)


@dataclass
class AlertRule:
    name: str
    severity: str
    condition: str
    type: str
    owner: str
    runbook: str


def load_alert_rules() -> list[AlertRule]:
    if not ALERT_RULES_PATH.exists():
        return []

    raw = yaml.safe_load(ALERT_RULES_PATH.read_text(encoding="utf-8")) or {}
    rules = raw.get("alerts", [])
    return [AlertRule(**rule) for rule in rules]


def _compare(actual: float, operator: str, threshold: float) -> bool:
    if operator == ">":
        return actual > threshold
    if operator == "<":
        return actual < threshold
    if operator == ">=":
        return actual >= threshold
    if operator == "<=":
        return actual <= threshold
    return actual == threshold


def _evaluate_condition(condition: str, values: dict[str, Any]) -> dict[str, Any]:
    match = CONDITION_RE.match(condition.strip())
    if not match:
        return {"matched": False, "status": "invalid", "detail": "Unsupported condition format"}

    metric = match.group("metric")
    operator = match.group("operator")
    threshold = float(match.group("threshold"))
    window = match.group("window")
    actual = float(values.get(metric, 0.0))
    fired = _compare(actual, operator, threshold)
    return {
        "matched": True,
        "metric": metric,
        "operator": operator,
        "threshold": threshold,
        "window": window,
        "actual": actual,
        "status": "firing" if fired else "ok",
    }


def evaluate_alerts() -> dict[str, Any]:
    values = snapshot()
    alerts = []

    for rule in load_alert_rules():
        result = _evaluate_condition(rule.condition, values)
        status = result["status"]
        previous = _LAST_STATUS.get(rule.name)

        if status == "firing" and previous != "firing":
            log.warning(
                "alert_firing",
                service="alerts",
                payload={
                    "name": rule.name,
                    "severity": rule.severity,
                    "condition": rule.condition,
                    "runbook": rule.runbook,
                    "actual": result.get("actual"),
                },
            )
        if status == "ok" and previous == "firing":
            log.info(
                "alert_resolved",
                service="alerts",
                payload={"name": rule.name, "condition": rule.condition, "runbook": rule.runbook},
            )

        _LAST_STATUS[rule.name] = status
        alerts.append(
            {
                "name": rule.name,
                "severity": rule.severity,
                "condition": rule.condition,
                "type": rule.type,
                "owner": rule.owner,
                "runbook": rule.runbook,
                **result,
            }
        )

    return {"alerts": alerts, "metrics": values}
