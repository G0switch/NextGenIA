"""Independent cross-check of reference-td1.csv, computed from the CSV files (no SQL).

Run from kit-td1:  python crosscheck_csv.py
Coding assistance disclosed: script drafted with Claude, to be read and verified by the sub-group.
"""
import csv
from datetime import date, datetime
from pathlib import Path

DATA = Path("data")


def read(name):
    with open(DATA / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


prices = {r["product_id"]: int(r["price"]) for r in read("product.csv")}
births = {r["customer_id"]: date.fromisoformat(r["birth_date"]) for r in read("customers.csv")}
lines = []
for r in read("orders.csv"):
    lines.append({
        "dt": datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S"),
        "customer": r["customer_id"],
        "product": r["product_id"],
        "amount": int(r["quantity_product"]) * prices[r["product_id"]],
    })


def age(birth, ref):
    """Completed age: one year less if the birthday has not yet come in the reference year."""
    return ref.year - birth.year - ((ref.month, ref.day) < (birth.month, birth.day))


def dt(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def revenue(start=None, end=None, products=None, age_on=None, age_at_order=False):
    total = 0
    for l in lines:
        if start and not (dt(start) <= l["dt"] < dt(end)):  # closed left, open right
            continue
        if products and l["product"] not in products:
            continue
        if age_on and age(births[l["customer"]], date.fromisoformat(age_on)) != 25:
            continue
        if age_at_order and age(births[l["customer"]], l["dt"].date()) != 25:
            continue
        total += l["amount"]
    return total  # 0 when nothing matches


ABC = {"a", "b", "c"}
cases = {
    "C01": revenue("2026-03-01 00:00:00", "2026-06-01 00:00:00"),
    "C02": revenue(age_on="2026-09-25"),
    "C03": revenue("2026-01-01 00:00:00", "2026-07-01 00:00:00", ABC),
    "C04": revenue("2026-01-01 00:00:00", "2026-10-01 00:00:00"),
    "C05": revenue("2026-06-01 00:00:00", "2026-06-02 00:00:00"),
    "C06": revenue("2025-01-01 00:00:00", "2026-01-01 00:00:00"),
    "C07": revenue("2026-05-31 00:00:00", "2026-06-01 00:00:00"),
    "C08": revenue(age_on="2026-09-24"),
    "C09": revenue(age_on="2026-09-26"),
    "C10": revenue(age_at_order=True),
    "C11": revenue(age_on="2026-12-01"),
    "C12": revenue(products=ABC),
    "C13": revenue("2026-04-01 00:00:00", "2026-05-01 00:00:00", {"a", "c"}),
    "C14": revenue("2026-10-01 00:00:00", "2026-12-01 00:00:00", ABC),
    "C15": revenue("2026-03-01 00:00:00", "2026-06-01 00:00:00", age_on="2026-09-25"),
    "C16": revenue(products=ABC, age_on="2026-09-25"),
    "C17": revenue("2026-01-01 00:00:00", "2026-07-01 00:00:00", ABC, age_on="2026-09-25"),
    "C18": revenue("2026-05-01 00:00:00", "2026-06-01 00:00:00", age_at_order=True),
    "C19": revenue("2026-09-01 00:00:00", "2026-10-01 00:00:00", {"d"}, age_on="2026-09-25"),
    "C20": revenue("2026-06-01 00:00:00", "2026-09-01 00:00:00"),
}

with open("reference-td1.csv", newline="", encoding="utf-8") as f:
    ref = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(f)}

diff = 0
for cid, value in cases.items():
    ok = ref.get(cid) == value
    diff += not ok
    print(f"{'[OK]  ' if ok else '[DIFF]'} {cid}  csv={value}  reference={ref.get(cid)}")
print(f"\n{20 - diff}/20 identical")
