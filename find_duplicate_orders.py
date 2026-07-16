#!/usr/bin/env python3
"""
CLI tool to scan a large log/CSV dump for duplicate order numbers:
`ln` (legacy order number), `lln` (long order number), and `sn` (short
order number).

Log lines look like:

    Response
    Body:{"messages": {...}, "orderNumbersSet": [{"ln": "26197IJS6L", "lln": "...", "sn": "..."}]}

Only lines starting with `Body:` are parsed as JSON. Every entry in
`orderNumbersSet` contributes its `ln`, `lln`, and `sn` to their own
running counts. After scanning the whole file, any values seen more than
once are reported per field.

Usage:
    python find_duplicate_orders.py /path/to/yourfile.csv
"""

import argparse
import json
import sys
from collections import Counter

BODY_PREFIX = "Body:"
ORDER_NUMBER_FIELDS = ("ln", "lln", "sn")


def scan_file(path: str) -> dict:
    counts = {field: Counter() for field in ORDER_NUMBER_FIELDS}
    body_lines_seen = 0

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for lineno, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped.startswith(BODY_PREFIX):
                continue

            body_lines_seen += 1
            payload = stripped[len(BODY_PREFIX):]

            try:
                data = json.loads(payload)
            except json.JSONDecodeError as exc:
                print(f"[warn] line {lineno}: could not parse JSON ({exc})", file=sys.stderr)
                continue

            order_numbers_set = data.get("orderNumbersSet") or []
            if not isinstance(order_numbers_set, list):
                print(f"[warn] line {lineno}: 'orderNumbersSet' is not a list, skipping", file=sys.stderr)
                continue

            for item in order_numbers_set:
                if not isinstance(item, dict):
                    continue
                for field in ORDER_NUMBER_FIELDS:
                    value = item.get(field)
                    if value:
                        counts[field][value] += 1

    print(f"\nScanned {body_lines_seen} 'Body:' line(s).")
    return counts


def report(counts: dict) -> None:
    for field in ORDER_NUMBER_FIELDS:
        field_counts = counts[field]
        total = sum(field_counts.values())
        unique = len(field_counts)

        print(f"\n--- {field} ---")
        print(f"Total values collected: {total}")
        print(f"Unique values: {unique}")

        duplicates = {value: count for value, count in field_counts.items() if count > 1}

        if not duplicates:
            print(f"No duplicate {field} values found.")
            continue

        print(f"Found {len(duplicates)} duplicate {field} value(s):")
        for value, count in sorted(duplicates.items(), key=lambda kv: -kv[1]):
            print(f"  {value}: {count} occurrences")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan a log/CSV file for duplicate ln, lln, and sn values."
    )
    parser.add_argument("file", help="Path to the log/CSV file to scan")
    args = parser.parse_args()

    counts = scan_file(args.file)
    report(counts)


if __name__ == "__main__":
    main()
