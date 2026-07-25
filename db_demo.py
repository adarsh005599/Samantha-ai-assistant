from __future__ import annotations

from sqlalchemy import text

from database import engine


def run_sql(query: str):
    """Run a raw SQL query on the same DB used by `database.py`.

    Example:
        rows = run_sql("SELECT * FROM appointments")
        print(rows)
    """
    with engine.begin() as conn:
        result = conn.execute(text(query))
        return result.fetchall() if result.returns_rows else result.rowcount


if __name__ == "__main__":
    query = "SELECT * FROM appointments"
    print(run_sql(query))