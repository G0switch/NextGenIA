import csv, sqlite3
from pathlib import Path

ICI = Path(__file__).parent
DB = (ICI / "data" / "boutique.sqlite").resolve().as_uri() + "?mode=ro"
FICHIER = ICI / "reference-td1.csv"

with open(FICHIER, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    colonnes = reader.fieldnames
    lignes = list(reader)

con = sqlite3.connect(DB, uri=True)
for ligne in lignes:
    case = ligne["case_id"]
    sql = " ".join((ICI / "refs" / f"{case}.sql").read_text(encoding="utf-8").split())
    cur = con.execute(sql)
    res = cur.fetchall()
    assert cur.description[0][0] == "revenue_cents", f"{case} : colonne mal nommée"
    assert len(res) == 1 and len(res[0]) == 1, f"{case} : il faut 1 ligne et 1 colonne"
    ligne["sql"] = sql
    ligne["revenue_cents"] = res[0][0]
    print(case, res[0][0])
con.close()

with open(FICHIER, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=colonnes)
    w.writeheader()
    w.writerows(lignes)

print(f"reference-td1.csv rempli : {len(lignes)} lignes")