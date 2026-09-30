"""Reports the shop's dashboard runs. The SQL lives in the code."""
import sqlite3


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def customer_summary(conn, region, since):
    """Order count, delivered spend and last order date for each customer
    in a region who signed up on or after `since`, biggest spenders first."""
    customers = conn.execute(
        "SELECT id, name FROM customers WHERE region = ? AND signup_date >= ?",
        (region, since),
    ).fetchall()

    summary = []
    for customer in customers:
        orders = conn.execute(
            "SELECT id, order_date, status FROM orders WHERE customer_id = ?",
            (customer["id"],),
        ).fetchall()
        spend = 0.0
        last_order = None
        for order in orders:
            if last_order is None or order["order_date"] > last_order:
                last_order = order["order_date"]
            if order["status"] != "delivered":
                continue
            for item in conn.execute(
                "SELECT quantity, unit_price FROM order_items WHERE order_id = ?",
                (order["id"],),
            ):
                spend += item["quantity"] * item["unit_price"]
        summary.append({
            "customer_id": customer["id"],
            "name": customer["name"],
            "orders": len(orders),
            "spend": round(spend, 2),
            "last_order": last_order,
        })

    summary.sort(key=lambda row: (-row["spend"], row["customer_id"]))
    return summary


def product_search(conn, term, limit=20):
    """Products whose name contains `term`, with their average rating and
    review count, best rated first."""
    products = conn.execute(
        "SELECT id, name, category, price FROM products "
        "WHERE lower(name) LIKE '%' || lower(?) || '%'",
        (term,),
    ).fetchall()

    results = []
    for product in products:
        ratings = [row["rating"] for row in conn.execute(
            "SELECT rating FROM reviews WHERE product_id = ?", (product["id"],))]
        results.append({
            "product_id": product["id"],
            "name": product["name"],
            "category": product["category"],
            "price": product["price"],
            "reviews": len(ratings),
            "avg_rating": round(sum(ratings) / len(ratings), 3) if ratings else None,
        })

    results.sort(key=lambda row: (-(row["avg_rating"] or 0), -row["reviews"], row["product_id"]))
    return results[:limit]
