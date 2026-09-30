"""Build data/shop.db from schema.sql with seeded synthetic data.

The same seed always produces the same rows, so query results can be
compared across code changes.
"""
import argparse
import datetime as dt
import random
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS = ["EU", "NA", "APAC", "LATAM", "MEA"]
CATEGORIES = ["books", "games", "garden", "kitchen", "music", "outdoor", "tech", "toys"]
STATUSES = ["delivered"] * 7 + ["shipped", "cancelled", "returned"]
WORDS = ["alpha", "bold", "classic", "deluxe", "eco", "fresh", "grand", "hyper",
         "lite", "max", "nova", "prime", "pro", "smart", "ultra", "zen"]
START = dt.date(2023, 1, 1)


def day(rng, span_days):
    return (START + dt.timedelta(days=rng.randrange(span_days))).isoformat()


def build(path, scale, seed):
    rng = random.Random(seed)
    n_customers, n_products = 20_000 * scale, 2_000 * scale
    n_orders, n_reviews = 150_000 * scale, 60_000 * scale

    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript((ROOT / "schema.sql").read_text())

    conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?)",
        ((i, f"Customer {i}", f"customer{i}@example.com", rng.choice(REGIONS), day(rng, 900))
         for i in range(1, n_customers + 1)))
    prices = {}
    rows = []
    for i in range(1, n_products + 1):
        prices[i] = round(rng.uniform(2, 400), 2)
        name = f"{rng.choice(WORDS).title()} {rng.choice(WORDS).title()} {i}"
        rows.append((i, name, rng.choice(CATEGORIES), prices[i]))
    conn.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", rows)

    orders, items, item_id = [], [], 0
    for i in range(1, n_orders + 1):
        orders.append((i, rng.randint(1, n_customers), day(rng, 1000), rng.choice(STATUSES)))
        for _ in range(rng.randint(1, 5)):
            item_id += 1
            product = rng.randint(1, n_products)
            items.append((item_id, i, product, rng.randint(1, 4), prices[product]))
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
    conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", items)

    # Most reviews go to a popular subset, so plenty of products have none.
    popular = n_products // 3
    conn.executemany(
        "INSERT INTO reviews VALUES (?, ?, ?, ?, ?)",
        ((i, rng.randint(1, popular), rng.randint(1, n_customers), rng.randint(1, 5), day(rng, 1000))
         for i in range(1, n_reviews + 1)))
    conn.commit()
    conn.execute("ANALYZE")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default=str(ROOT / "data" / "shop.db"))
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    started = time.perf_counter()
    build(Path(args.db), args.scale, args.seed)
    print(f"built {args.db} in {time.perf_counter() - started:.1f}s")


if __name__ == "__main__":
    main()
