"""Recompute C11 from the three source CSV files in integer cents."""

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "td1" / "data"
REFERENCE_DATE = date(2026, 12, 1)


def read_csv(name):
    with (DATA / name).open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle)


def main():
    births = {}
    for row in read_csv("customers.csv"):
        if row["birth_date"]:
            births[row["customer_id"]] = date.fromisoformat(row["birth_date"])

    customers_age_25 = {}
    for customer_id, birth in births.items():
        birthday_passed = (birth.month, birth.day) <= (REFERENCE_DATE.month, REFERENCE_DATE.day)
        age = REFERENCE_DATE.year - birth.year - int(not birthday_passed)
        if age == 25:
            customers_age_25[customer_id] = birth

    prices = {row["product_id"]: int(row["price"]) for row in read_csv("product.csv")}
    orders = defaultdict(set)
    revenue = defaultdict(int)
    for row in read_csv("orders.csv"):
        customer_id = row["customer_id"]
        if customer_id in customers_age_25:
            orders[customer_id].add(row["order_id"])
            revenue[customer_id] += int(row["quantity_product"]) * prices[row["product_id"]]

    print("customer_id | birth_date | distinct_orders | revenue_cents")
    for customer_id, amount in sorted(revenue.items()):
        birth = customers_age_25[customer_id]
        print(f"{customer_id} | {birth} | {len(orders[customer_id])} | {amount}")

    print(f"Customers with orders: {len(revenue)}")
    print(f"Distinct orders: {len(set().union(*orders.values()))}")
    print(f"Total revenue (cents): {sum(revenue.values())}")


if __name__ == "__main__":
    main()
