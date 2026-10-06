"""Check that the report is still exactly the same as the original one.

The original report was saved once, from the original query, in
expected/top_customers_report.txt. This runs the report again with the
current code and compares the two. Any difference fails.

The report doesn't show every column the query returns (the customer id,
for one), so once the report matches, the query's rows are also checked
against the same fingerprint bench.py uses. A change the report can't see
(a hidden column's values, or the columns added, removed or reordered)
fails here rather than later in the benchmark.

    python3 compare_report.py
"""
import difflib
import sys
from pathlib import Path

import report
import targets

TARGET = "sql:top_customers"
EXPECTED = Path(__file__).resolve().parent / "expected" / "top_customers_report.txt"


def main():
    rows = targets.run(TARGET, targets.connect())
    now = report.render(rows)
    before = EXPECTED.read_text()
    if now != before:
        print("FAIL: the report differs from the original report")
        sys.stdout.writelines(difflib.unified_diff(
            before.splitlines(True), now.splitlines(True), "original report", "new report"))
        sys.exit(1)
    if targets.fingerprint(rows) != targets.expected_path(TARGET).read_text().strip():
        print("FAIL: the report matches, but the query's rows differ from the original query's")
        print("A column the report doesn't show changed, or columns were added, removed or reordered. "
              "Keep the query's columns and their order exactly as they were.")
        sys.exit(1)
    print("PASS: the report matches the original report line for line")


if __name__ == "__main__":
    main()
