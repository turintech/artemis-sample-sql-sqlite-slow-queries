# Shop analytics on SQLite

A small shop-analytics app with slow SQL, for trying query optimisation with [Artemis](https://turintech.ai). It needs Python 3.10 or newer and nothing else: SQLite ships with Python.

The database is synthetic. `scripts/make_db.py` builds `data/shop.db` from `schema.sql` with a fixed seed, so every build has the same 20,000 customers, 2,000 products, 150,000 orders, about 450,000 order items and 60,000 reviews.

## The queries

Some queries live in `.sql` files, and some are written into the application code, the way they usually are in a real codebase.

| Target | Where | What it does |
|---|---|---|
| `sql:top_customers` | `queries/top_customers.sql` | Top 20 EU customers by 2025 spend, using correlated subqueries |
| `sql:unreviewed_bestsellers` | `queries/unreviewed_bestsellers.sql` | Best-selling tech products with no reviews |
| `sql:monthly_category_revenue` | `queries/monthly_category_revenue.sql` | Monthly revenue per category for 2025 |
| `code:customer_summary` | `app/reports.py` | Per-customer dashboard summary, one query per customer and per order |
| `code:product_search` | `app/reports.py` | Product search with ratings, one query per product |

Only primary keys are indexed.

## The report

The sales team runs the "Top customers" report, which is built on `queries/top_customers.sql`:

```bash
python3 scripts/make_db.py   # build the database
python3 report.py            # print the report (the query takes about 5 seconds)
```

To check a change to the query, compare the report with the original one. The original report was saved once, before any changes, in `expected/top_customers_report.txt`:

```bash
python3 compare_report.py    # PASS if the report is identical, FAIL with the differences if not
```

## Build, check, benchmark

```bash
python3 scripts/make_db.py                        # build data/shop.db
python3 check.py --target sql:top_customers       # same rows as the original?
python3 bench.py --target sql:top_customers       # time it, write artemis_results.csv
```

There are no unit tests. `check.py` is the test: it runs the query and compares a fingerprint of its rows, in order, with the fingerprint recorded from the original query in `expected/`. A change that makes a query faster but alters its result fails. `bench.py` runs the same check before timing, then writes `query_ms` (median of three timed runs after a warm-up) and `db_size_mb` to `artemis_results.csv`. Indexes usually trade one against the other.

Run `python3 check.py --all` to check every target.

## Commands for Artemis

To optimise one target, point the Script at it:

| Phase | Command |
|---|---|
| Build | `python3 scripts/make_db.py` |
| Test | `python3 compare_report.py` (or `python3 check.py --target sql:top_customers`) |
| Benchmark | `python3 bench.py --target sql:top_customers` |

For a query in the code, use `code:customer_summary` in the test and benchmark commands instead. Metrics: `query_ms` (lower is better) and `db_size_mb` (lower is better).

Changes can go anywhere that keeps the result identical: the query, the Python around it, or `schema.sql` (for example an index, which the build step creates). Don't edit `expected/`, `check.py` or `bench.py`; they define what "the same result" and "faster" mean.
