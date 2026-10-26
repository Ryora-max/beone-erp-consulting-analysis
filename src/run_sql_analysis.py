"""Eksekusi semua query di database/queries.sql, simpan hasil ke CSV."""
import sqlite3, os
import pandas as pd

os.makedirs("outputs/sql_results", exist_ok=True)
con = sqlite3.connect("database/beone.db")
queries = [q.strip() for q in
           open("database/queries.sql", encoding="utf-8").read().split(";")
           if q.strip() and "-- Q" not in q.strip()[:4]]
# split manual per marker komentar
raw = open("database/queries.sql", encoding="utf-8").read()
blocks, cur = [], []
for line in raw.splitlines():
    if line.strip().startswith("-- Q") and cur:
        blocks.append("\n".join(cur)); cur = []
    cur.append(line)
blocks.append("\n".join(cur))
for i, q in enumerate([b for b in blocks if "SELECT" in b], 1):
    df = pd.read_sql_query(q, con)
    df.to_csv(f"outputs/sql_results/q{i}.csv", index=False)
    print(f"Q{i}: {len(df)} baris")
con.close()
