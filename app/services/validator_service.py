"""Input validation helpers."""
import re
from typing import Tuple


def validate_query_text(text: str) -> bool:
    return bool(text and len(text.strip()) > 0)


def validate_sql(sql: str) -> Tuple[bool, str]:
    """Validate SQL to ensure it's a safe SELECT query.

    Returns (is_valid, error_message).
    """
    if not sql or not isinstance(sql, str):
        return False, "SQL is empty or invalid type"

    sql_clean = sql.strip()

    # Must start with SELECT (case-insensitive)
    if not sql_clean.upper().startswith("SELECT"):
        return False, "SQL must start with SELECT"

    # Block dangerous operations
    dangerous = ["DELETE", "DROP", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]
    sql_upper = sql_clean.upper()
    for keyword in dangerous:
        # Use word boundary to avoid false positives
        if re.search(r"\b" + keyword + r"\b", sql_upper):
            return False, f"SQL cannot contain {keyword} operations"

    return True, ""
