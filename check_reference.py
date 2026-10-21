import csv
from datetime import date, datetime
from pathlib import Path

ICI = Path(__file__).parent

def lire(nom):
    with open(ICI / "data" / nom, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

prix = {r["product_id"]: int(r["price"]) for r in lire("product.csv")}
naissance = {r["customer_id"]: date.fromisoformat(r["birth_date"]) for r in lire("customers.csv")}
commandes = lire("orders.csv")

def ts(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

def age(ne, le):  
    return le.year - ne.year - ((le.month, le.day) < (ne.month, ne.day))

def ca(debut=None, fin=None, produits=None, age_le=None, age_commande=False):
    total = 0
    for o in commandes:
        quand = ts(o["date"])
        ne = naissance[o["customer_id"]]
        if debut and quand < ts(debut): continue
        if fin and quand >= ts(fin): continue
        if produits and o["product_id"] not in produits: continue
        if age_le and age(ne, date.fromisoformat(age_le)) != 25: continue
        if age_commande and age(ne, quand.date()) != 25: continue
        total += int(o["quantity_product"]) * prix[o["product_id"]]
    return total

ABC = {"a", "b", "c"}
QUESTIONS = {
    "C01": dict(debut="2026-03-01 00:00:00", fin="2026-06-01 00:00:00"),
    "C02": dict(age_le="2026-09-25"),
    "C03": dict(produits=ABC, debut="2026-01-01 00:00:00", fin="2026-07-01 00:00:00"),
    "C04": dict(debut="2026-01-01 00:00:00", fin="2026-10-01 00:00:00"),
    "C05": dict(debut="2026-06-01 00:00:00", fin="2026-06-02 00:00:00"),
    "C06": dict(debut="2025-01-01 00:00:00", fin="2026-01-01 00:00:00"),
    "C07": dict(debut="2026-05-31 00:00:00", fin="2026-06-01 00:00:00"),
    "C08": dict(age_le="2026-09-24"),
    "C09": dict(age_le="2026-09-26"),
    "C10": dict(age_commande=True),
    "C11": dict(age_le="2026-12-01"),
    "C12": dict(produits=ABC),
    "C13": dict(produits={"a", "c"}, debut="2026-04-01 00:00:00", fin="2026-05-01 00:00:00"),
    "C14": dict(produits=ABC, debut="2026-10-01 00:00:00", fin="2026-12-01 00:00:00"),
    "C15": dict(debut="2026-03-01 00:00:00", fin="2026-06-01 00:00:00", age_le="2026-09-25"),
    "C16": dict(produits=ABC, age_le="2026-09-25"),
    "C17": dict(produits=ABC, debut="2026-01-01 00:00:00", fin="2026-07-01 00:00:00", age_le="2026-09-25"),
    "C18": dict(debut="2026-05-01 00:00:00", fin="2026-06-01 00:00:00", age_commande=True),
    "C19": dict(produits={"d"}, debut="2026-09-01 00:00:00", fin="2026-10-01 00:00:00", age_le="2026-09-25"),
    "C20": dict(debut="2026-06-01 00:00:00", fin="2026-09-01 00:00:00"),
}

with open(ICI / "reference-td1.csv", encoding="utf-8-sig", newline="") as f:
    refs = {r["case_id"]: int(r["revenue_cents"]) for r in csv.DictReader(f)}

ok = 0
for case, filtres in QUESTIONS.items():
    v = ca(**filtres)
    ok += v == refs[case]
    print(f"{case}  SQL={refs[case]:>9}  CSV={v:>9}  {'OK' if v == refs[case] else 'ECART'}")
print(f"\n{ok}/20 identiques")