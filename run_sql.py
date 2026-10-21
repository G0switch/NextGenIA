import sqlite3, sys
from pathlib import Path

DB = (Path(__file__).parent / "data" / "boutique.sqlite").resolve().as_uri() + "?mode=ro"

if len(sys.argv) < 2:
    print('Usage : python run_sql.py "SELECT ..."   ou   python run_sql.py fichier.sql')
    sys.exit()

arg = sys.argv[1]
sql = Path(arg).read_text(encoding="utf-8") if arg.endswith(".sql") else arg

con = sqlite3.connect(DB, uri=True)
cur = con.execute(sql)
print(" | ".join(d[0] for d in cur.description))
for row in cur.fetchall():
    print(" | ".join(str(v) for v in row))
con.close()