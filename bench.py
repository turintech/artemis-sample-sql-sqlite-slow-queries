"""Time one query and write artemis_results.csv.

Runs the target once to warm the cache, then times it --runs times and
records the median. It also checks the result against the expected
fingerprint, so a faster query that returns different rows fails.

    python3 bench.py --target sql:top_customers
    python3 bench.py --target code:customer_summary
"""
import argparse
import csv
import statistics
import sys
import time

import targets


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", required=True)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--out", default="artemis_results.csv")
    args = parser.parse_args()

    conn = targets.connect()
    rows = targets.run(args.target, conn)
    if targets.fingerprint(rows) != targets.expected_path(args.target).read_text().strip():
        print(f"FAIL {args.target}: result differs from the original query", file=sys.stderr)
        sys.exit(1)

    times = []
    for _ in range(args.runs):
        started = time.perf_counter()
        targets.run(args.target, conn)
        times.append((time.perf_counter() - started) * 1000)
    query_ms = statistics.median(times)
    db_size_mb = targets.DB.stat().st_size / 1e6

    with open(args.out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["query_ms", "db_size_mb"])
        writer.writerow([round(query_ms, 2), round(db_size_mb, 3)])
    print(f"{args.target}: {query_ms:.1f} ms median of {args.runs}, database {db_size_mb:.1f} MB, {len(rows)} rows")


if __name__ == "__main__":
    main()
