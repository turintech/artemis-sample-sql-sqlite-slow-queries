"""Check that the report is still exactly the same as the original one.

The original report was saved once, from the original query, in
expected/top_customers_report.txt. This runs the report again with the
current code and compares the two. Any difference fails.

    python3 compare_report.py
"""
import difflib
import sys
from pathlib import Path

import report
import targets

EXPECTED = Path(__file__).resolve().parent / "expected" / "top_customers_report.txt"


def main():
    now = report.render(targets.run("sql:top_customers", targets.connect()))
    before = EXPECTED.read_text()
    if now == before:
        print("PASS: the report matches the original report line for line")
        return
    print("FAIL: the report differs from the original report")
    sys.stdout.writelines(difflib.unified_diff(
        before.splitlines(True), now.splitlines(True), "original report", "new report"))
    sys.exit(1)


if __name__ == "__main__":
    main()
