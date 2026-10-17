"""Generate original toy sequences; optionally export one for the CLI."""
import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path

from hs_pattern_detector import detect_patterns


def synthetic_prices(kind: str) -> list[float]:
    if kind not in {"HS", "IHS"}:
        raise ValueError("kind must be HS or IHS")
    anchors = [100.0, 110.0, 102.0, 118.0, 102.0, 110.0, 100.0]
    # Linear interpolation adds two observations between each pair of anchors.
    values = [a+(b-a)*j/3 for a, b in zip(anchors, anchors[1:]) for j in range(3)]
    values.append(anchors[-1])
    return values if kind == "HS" else [220.0-v for v in values]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, help="Optional output CSV path")
    parser.add_argument("--kind", choices=["HS", "IHS"], default="HS")
    args = parser.parse_args()
    for kind in ("HS", "IHS"):
        patterns = detect_patterns(synthetic_prices(kind))
        print(json.dumps({"synthetic": kind, "patterns": [asdict(p) for p in patterns]}))
    if args.csv:
        with args.csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["price"])
            writer.writerows((p,) for p in synthetic_prices(args.kind))
        print(f"Wrote synthetic {args.kind} CSV: {args.csv}")


if __name__ == "__main__":
    main()
