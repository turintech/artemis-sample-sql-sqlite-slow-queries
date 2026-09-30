"""Check that a query still returns exactly the same rows as the original.

This project has no unit tests; this check is the test. The expected
fingerprints in expected/ were recorded from the original queries on the
seeded database, so any change that alters the result fails here.

    python3 check.py --target sql:top_customers
    python3 check.py --all
"""
import argparse
import sys

import targets


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", action="append", default=[])
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--record", action="store_true",
                        help="overwrite the expected fingerprints (only on the original code)")
    args = parser.parse_args()
    chosen = targets.names() if args.all else args.target
    if not chosen:
        parser.error("pass --target or --all")

    conn = targets.connect()
    failed = 0
    for target in chosen:
        got = targets.fingerprint(targets.run(target, conn))
        path = targets.expected_path(target)
        if args.record:
            path.write_text(got + "\n")
            print(f"recorded {target}")
            continue
        want = path.read_text().strip()
        ok = got == want
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'} {target}" + ("" if ok else f" (got {got[:12]}, want {want[:12]})"))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
