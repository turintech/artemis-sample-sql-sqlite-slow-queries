"""Every query the benchmark and the result check know about.

A target is either a .sql file under queries/ (`sql:<name>`) or a report
function in app/reports.py (`code:<name>`), with the arguments the
dashboard calls it with.
"""
import json
import hashlib
from pathlib import Path

from app import reports

ROOT = Path(__file__).resolve().parent
DB = ROOT / "data" / "shop.db"

CODE_TARGETS = {
    "customer_summary": lambda conn: reports.customer_summary(conn, "EU", "2025-05-01"),
    "product_search": lambda conn: reports.product_search(conn, "eco"),
}


def connect():
    return reports.connect(DB)


def names():
    sql = sorted(f"sql:{p.stem}" for p in (ROOT / "queries").glob("*.sql"))
    return sql + [f"code:{name}" for name in CODE_TARGETS]


def run(target, conn):
    kind, _, name = target.partition(":")
    if kind == "sql":
        return conn.execute((ROOT / "queries" / f"{name}.sql").read_text()).fetchall()
    if kind == "code":
        return CODE_TARGETS[name](conn)
    raise SystemExit(f"unknown target {target!r}; choose from {', '.join(names())}")


def fingerprint(rows):
    """Hash of the result, in order, with floats rounded to cents."""
    def plain(value):
        if isinstance(value, float):
            return round(value, 2)
        if isinstance(value, dict):
            return {k: plain(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)) or hasattr(value, "keys"):
            return [plain(v) for v in (tuple(value) if hasattr(value, "keys") else value)]
        return value
    data = json.dumps([plain(r) for r in rows], separators=(",", ":"))
    return hashlib.sha256(data.encode()).hexdigest()


def expected_path(target):
    return ROOT / "expected" / (target.replace(":", "__") + ".sha256")
