"""Print the shop's "Top customers" report, the way the sales team runs it.

    python3 report.py                   # print the report
    python3 report.py --out report.txt  # also save it to a file

The query behind it is queries/top_customers.sql.
"""
import argparse
import sys
import time

import targets

TITLE = "Top EU customers (signed up since July 2024) by 2025 spend"


def render(rows):
    lines = [TITLE, "", f"{'#':>3}  {'Customer':<16} {'Orders':>6}  {'Spend 2025':>12}"]
    for rank, row in enumerate(rows, 1):
        spend = f"{row['spend_2025'] or 0:,.2f}"
        lines.append(f"{rank:>3}  {row['name']:<16} {row['orders_2025']:>6}  {spend:>12}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out")
    args = parser.parse_args()

    conn = targets.connect()
    started = time.perf_counter()
    rows = targets.run("sql:top_customers", conn)
    elapsed = time.perf_counter() - started
    text = render(rows)
    print(text, end="")
    print(f"\nQuery took {elapsed:.2f} s", file=sys.stderr)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)


if __name__ == "__main__":
    main()
