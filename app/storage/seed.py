from __future__ import annotations

import pandas as pd

from .db import connect, init_db, insert_metrics_dataframe


def main() -> None:
    conn = connect()
    init_db(conn)
    df = pd.DataFrame({
        "category": ["Revenue", "Expenses", "Profit"],
        "amount": [120.0, 80.0, 40.0],
        "source": ["seed", "seed", "seed"],
    })
    insert_metrics_dataframe(conn, df)
    print("Seeded database at data/app.db with sample metrics.")


if __name__ == "__main__":
    main()
