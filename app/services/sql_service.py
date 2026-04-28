"""Simple SQL helper service."""
from app.database import get_connection


def run_query(sql: str, params: tuple = ()): 
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows
