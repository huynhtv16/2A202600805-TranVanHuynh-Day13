from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples", type=int, default=12, help="Number of metric snapshots to collect")
    parser.add_argument("--interval", type=float, default=5.0, help="Seconds between snapshots")
    parser.add_argument(
        "--output",
        default="data/metrics_snapshots.jsonl",
        help="Output JSONL file for collected snapshots",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=10.0) as client, output_path.open("a", encoding="utf-8") as f:
        for idx in range(args.samples):
            response = client.get(f"{BASE_URL}/metrics")
            response.raise_for_status()
            payload = response.json()
            record = {
                "ts": datetime.now(timezone.utc).isoformat(),
                **payload,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"[{idx + 1}/{args.samples}] captured traffic={payload.get('traffic')} p95={payload.get('latency_p95')}")
            if idx < args.samples - 1:
                time.sleep(args.interval)


if __name__ == "__main__":
    main()
