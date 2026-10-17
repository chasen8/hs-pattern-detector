"""Read an ordered CSV with a price column and emit JSON."""
import argparse
import csv
from dataclasses import asdict
import json

from .detector import detect_patterns


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Experimental HS/IHS geometric detector")
    parser.add_argument("csv_file", help="CSV with a price column; rows in chronological order")
    parser.add_argument("--pivot-window", type=int, default=1)
    parser.add_argument("--shoulder-tolerance", type=float, default=0.25)
    parser.add_argument("--neckline-tolerance", type=float, default=0.30)
    parser.add_argument("--min-head-prominence", type=float, default=0.10)
    parser.add_argument("--max-time-ratio", type=float, default=2.0)
    args = parser.parse_args(argv)
    try:
        with open(args.csv_file, newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames or "price" not in reader.fieldnames:
                raise ValueError("CSV must contain a price column")
            prices = [float(row["price"]) for row in reader]
        patterns = detect_patterns(
            prices, pivot_window=args.pivot_window,
            shoulder_tolerance=args.shoulder_tolerance,
            neckline_tolerance=args.neckline_tolerance,
            min_head_prominence=args.min_head_prominence,
            max_time_ratio=args.max_time_ratio,
        )
    except (OSError, ValueError, TypeError, csv.Error) as exc:
        parser.error(str(exc))
    payload = []
    for pattern in patterns:
        item = asdict(pattern)
        item["neckline"] = [asdict(p) for p in pattern.neckline]
        payload.append(item)
    print(json.dumps({
        "message": f"Detected {len(patterns)} pattern(s)." if patterns else "No patterns detected.",
        "patterns": payload,
    }, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
