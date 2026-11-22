"""Run every '-- Q<n>:' block in an SQL file against the warehouse; save each result to CSV."""
import re, sqlite3, sys
from pathlib import Path
import pandas as pd

def run(sql_file="sql/02_analytics.sql", out="outputs/day02", db="db/finops.db"):
    Path(out).mkdir(parents=True, exist_ok=True)
    blocks = re.split(r"(?m)^-- (Q\d+):", Path(sql_file).read_text())[1:]
    con = sqlite3.connect(db)
    for name, body in zip(blocks[::2], blocks[1::2]):
        title, _, sql = body.partition("\n")
        df = pd.read_sql_query(sql.strip().rstrip(";"), con)
        df.to_csv(f"{out}/{name}.csv", index=False)
        print(f"{name}: {len(df):>4} rows | {title.strip()}")
    con.close()

if __name__ == "__main__":
    run(*sys.argv[1:])
