"""Load semua CSV ke SQLite database beone.db."""
import sqlite3
import pandas as pd
import os

os.makedirs("database", exist_ok=True)
con = sqlite3.connect("database/beone.db")
for tabel in ["leads", "opportunities", "proyek", "tiket", "konsultan"]:
    df = pd.read_csv(f"data/raw/{tabel}.csv")
    df.to_sql(tabel, con, if_exists="replace", index=False)
    print(f"{tabel:15s} -> {len(df):6d} baris")
con.close()
print("OK: database/beone.db")
