"""Simple SQLite helpers.

Provides `connect_db()` to get a connection and `run_query()` to execute
queries without repeating boilerplate.
"""
import sqlite3
from pathlib import Path
from typing import Iterable, Optional, Sequence, Any
from .config import DATA_DIR


def connect_db(path: Path = DATA_DIR / "finance.db") -> sqlite3.Connection:
    """Return a sqlite3 connection with row factory set.

    Ensures parent directories exist.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def run_query(sql: str, params: Optional[Sequence[Any]] = None, *, fetch: bool = True):
    """Execute `sql` with optional `params`.

    If `fetch` is True return all rows, otherwise return lastrowid.
    """
    conn = connect_db()
    cur = conn.cursor()
    if params:
        cur.execute(sql, params)
    else:
        cur.execute(sql)

    if fetch:
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    else:
        conn.commit()
        lastrowid = cur.lastrowid
        conn.close()
        return lastrowid


# Backwards-compatible alias
get_connection = connect_db


def rows_to_dicts(rows: Optional[Iterable[Any]]) -> list[dict]:
    """Convert sqlite3.Row or dict-like rows to a list of plain dicts.

    Safe to call with None; returns an empty list.
    """
    if not rows:
        return []
    out: list[dict] = []
    for r in rows:
        if isinstance(r, dict):
            out.append(r)
            continue
        if hasattr(r, "keys"):
            try:
                out.append({k: r[k] for k in r.keys()})
                continue
            except Exception:
                pass
        out.append({"value": str(r)})
    return out
