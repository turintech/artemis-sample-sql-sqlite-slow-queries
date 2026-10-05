# SQL: slow SQLite queries for shop analytics

A small shop-analytics app of the kind an e-commerce or retail analytics team maintains, with slow SQL in it. Some queries live in `.sql` files and some are written into the application code, the way they usually are in a real codebase. The database is synthetic: `scripts/make_db.py` builds `data/shop.db` from `schema.sql` with a fixed seed, so every build has the same 20,000 customers, 2,000 products, 150,000 orders, about 450,000 order items and 60,000 reviews.

## What to optimise

The queries return the right rows but are slow, and only primary keys are indexed. There are five targets:

| Target | Where | What it does | Baseline |
|---|---|---|---|
| `sql:top_customers` | `queries/top_customers.sql` | top 20 EU customers by 2025 spend, using correlated subqueries | about 7.5 s |
| `sql:unreviewed_bestsellers` | `queries/unreviewed_bestsellers.sql` | the 25 best-selling tech products with no reviews | about 3 s |
| `sql:monthly_category_revenue` | `queries/monthly_category_revenue.sql` | monthly revenue per category for 2025 | about 85 ms |
| `code:customer_summary` | `app/reports.py` | per-customer dashboard summary, with one query per customer and another per order | about 7.5 s |
| `code:product_search` | `app/reports.py` | product search with ratings, with one query per product | about 235 ms |

The default target, and the one the sales team's "Top customers" report runs on, is `sql:top_customers`. The levers are the query text (for example replacing the correlated subqueries with a join and `GROUP BY`, or a date-range filter that can use an index instead of `strftime`), the Python around the in-code queries (one query instead of one per row), and indexes in `schema.sql`. A good result is a query that is many times faster, returns exactly the same rows in the same order, and doesn't grow the database much. Indexes usually trade query time against database size.

## Metrics

`bench.py` writes these to `artemis_results.csv` for the target it is given.

| Metric | Meaning | Unit | Better |
|---|---|---|---|
| `query_ms` | median time of three runs of the target, after one warm-up run | milliseconds | lower |
| `db_size_mb` | size of `data/shop.db`, which grows when indexes are added | MB | lower |

## How a change is judged

`check.py` runs a target and compares a SHA-256 fingerprint of its rows, in order and with floats rounded to cents, with the fingerprint recorded from the original query in `expected/`. A change that makes a query faster but alters its result fails. `bench.py` runs the same check before timing and exits with an error if it fails, so a wrong query never gets a time. `python3 check.py --all` checks all five targets.

For the "Top customers" report, `compare_report.py` renders the report from the current query and compares it line by line with `expected/top_customers_report.txt`, the report saved once from the original query.

There are no unit tests and no held-out set. The check is that the result is identical.

## Install

You need Python 3.10 or newer (checked with 3.12 on Ubuntu 24.04). SQLite ships with Python and the code uses only the standard library, so there is nothing to install and no GPU is needed. The database takes about 20 MB of disk and builds in about a second.

```bash
git clone https://github.com/turintech/artemis-sample-sql-sqlite-slow-queries.git
cd artemis-sample-sql-sqlite-slow-queries
python3 scripts/make_db.py
```

`data/` is not committed. `scripts/make_db.py` rebuilds it from `schema.sql`, so run it again after any change to `schema.sql`.

## Run it

```bash
python3 check.py --all                            # PASS or FAIL for every target
python3 check.py --target sql:top_customers       # one target
python3 bench.py --target sql:top_customers       # time it, write artemis_results.csv
python3 report.py                                 # print the "Top customers" report
python3 compare_report.py                         # PASS if the report is identical to the original
```

## Commands for Artemis

These optimise the default target. For another target, put its name in the Test and Benchmark commands instead, for example `code:customer_summary`.

| Phase | Command |
|---|---|
| Setup | `python3 scripts/make_db.py` |
| Test | `python3 check.py --target sql:top_customers` (or `python3 compare_report.py` for the report) |
| Benchmark | `python3 bench.py --target sql:top_customers` |

Changes can go anywhere that keeps the result identical: the `.sql` files in `queries/`, `app/reports.py`, or `schema.sql` (for example an index, which the setup step creates). Don't edit `expected/`, `check.py`, `bench.py`, `targets.py`, `compare_report.py`, `report.py` or `scripts/`; they define what "the same result" and "faster" mean.

## Baseline results

Measured on a 32-core Linux workstation with Python 3.12 and SQLite 3.45. `db_size_mb` was 19.239 for every target.

| Target | `query_ms` |
|---|---|
| `sql:top_customers` | 7,310 and 7,655 (two runs) |
| `sql:unreviewed_bestsellers` | 3,018 |
| `sql:monthly_category_revenue` | 85 |
| `code:customer_summary` | 7,777 and 7,490 (two runs) |
| `code:product_search` | 235 |

All five targets pass `check.py --all`, and `compare_report.py` passes.

## Files

| Path | What it is | Change it? |
|---|---|---|
| `queries/` | the three SQL targets | yes |
| `app/reports.py` | the two in-code targets and the database connection | yes |
| `schema.sql` | table definitions; indexes can be added here | yes |
| `bench.py` | the benchmark: checks a target, times it, writes `artemis_results.csv` | no |
| `check.py` | the correctness check against the fingerprints in `expected/` | no |
| `targets.py` | the list of targets, how each is run, and the fingerprint | no |
| `report.py` | prints the "Top customers" report | no |
| `compare_report.py` | compares the report with the saved original | no |
| `expected/` | fingerprints of the original results and the original report | no |
| `scripts/make_db.py` | builds the seeded synthetic database in `data/` | no |
| `LICENSE` | MIT licence | no |
