"""LLM integration helpers with support for `google.genai`.

This module attempts to use the newer `google.genai` client. If it's not
available it will fall back safely and return explanatory strings.
"""
from typing import Optional, Any
import re

from app.config import GEMINI_API_KEY


_GENAI_KIND: Optional[str] = None
_GENAI = None
_GENAI_CLIENT = None
try:
    import google.genai as genai  # type: ignore

    _GENAI_KIND = "genai"
    _GENAI = genai
    try:
        _GENAI_CLIENT = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else genai.Client()
    except Exception:
        _GENAI_CLIENT = None
except Exception:
    _GENAI_KIND = None


def _extract_text_from_response(resp: Any) -> str:
    """Try common response shapes and return a text string."""
    if resp is None:
        return ""

    # common attribute 'text'
    if hasattr(resp, "text") and isinstance(getattr(resp, "text"), str):
        return resp.text

    # google.genai client often returns an object with `output` list
    out = getattr(resp, "output", None)
    if out:
        try:
            # output[0].content
            return out[0].get("content") or out[0].get("text") or str(out[0])
        except Exception:
            pass

    # candidates / choices
    cand = getattr(resp, "candidates", None) or getattr(resp, "choices", None)
    if cand:
        try:
            first = cand[0]
            if hasattr(first, "content"):
                return first.content
            if isinstance(first, dict) and "content" in first:
                return first["content"]
        except Exception:
            pass

    # fallback to string
    try:
        return str(resp)
    except Exception:
        return ""


def ask_gemini(prompt: str, model: Optional[str] = None) -> str:
    """Send `prompt` to a Gemini-compatible client and return text.

    Uses google.genai with fallback models if the primary model is unavailable.
    Returns an explanatory string if no client is configured.
    """
    if model is None:
        model = "models/gemini-2.0-flash"  # Use stable model

    if _GENAI_KIND is None:
        return "Gemini client not installed or not configured. Set GEMINI_API_KEY in .env to enable."

    # List of fallback models to try if primary fails
    models_to_try = [model, "models/gemini-2.0-flash", "models/gemini-flash-latest"]
    
    try:
        if _GENAI_KIND == "genai" and _GENAI is not None and _GENAI_CLIENT is not None:
            # Use the modern google.genai client
            last_error = None
            for current_model in models_to_try:
                try:
                    resp = _GENAI_CLIENT.models.generate_content(model=current_model, contents=prompt)
                    # Extract text from response
                    if hasattr(resp, "candidates") and resp.candidates:
                        candidate = resp.candidates[0]
                        if hasattr(candidate, "content"):
                            content = candidate.content
                            if hasattr(content, "parts") and content.parts:
                                return content.parts[0].text
                            return str(content)
                    return _extract_text_from_response(resp)
                except Exception as e:
                    last_error = e
                    continue
            
            # All models failed
            return f"Gemini request failed: {last_error}"

        return "Gemini client not available."
    except Exception as e:
        return f"Gemini request failed: {e}"


def query_llm(prompt: str) -> str:
    """Backwards-compatible helper that calls `ask_gemini`."""
    return ask_gemini(prompt)


def generate_sql_from_question(question: str, user_id: int = 1, model: Optional[str] = None) -> str:
    """Use Gemini to generate a SQLite SELECT query from a natural language question.

    Returns only the SQL string (no explanations). If Gemini is not
    configured, returns a message explaining that.
    """
    prompt_lines = [
        "You are an expert assistant that generates SQL queries.",
        "Generate a valid SQLite SELECT query only (no explanation).",
        "Use the `transactions` table.",
        f"Always filter user_id = {user_id}.",
        "Return only the SQL statement. No surrounding text, no markdown code fences.",
        f"Question: {question}",
    ]
    prompt = "\n".join(prompt_lines)

    resp = ask_gemini(prompt, model=model or "models/text-bison-001")

    # If Gemini isn't available or request failed, use a local rule-based fallback
    if not resp or resp.lower().startswith("gemini") or resp.lower().startswith("gemini request failed"):
        # Simple heuristic-based SQL builder for common queries like
        # "How much did I spend on food last month?"
        q = question.lower()
        # detect category
        categories = ["food", "travel", "shopping", "rent", "utilities", "entertainment", "salary"]
        found_cat = next((c for c in categories if c in q), None)

        from datetime import date, timedelta

        today = date.today()
        first_of_this_month = today.replace(day=1)
        prev_last = first_of_this_month - timedelta(days=1)
        prev_first = prev_last.replace(day=1)

        def month_filter() -> str:
            return f" AND transaction_date BETWEEN '{first_of_this_month.isoformat()}' AND '{today.isoformat()}'"

        def last_month_filter() -> str:
            return f" AND transaction_date BETWEEN '{prev_first.isoformat()}' AND '{prev_last.isoformat()}'"

        if "top merchant" in q or "top merchants" in q or "merchant" in q:
            where = f"user_id = {user_id}"
            if "this month" in q:
                where += month_filter()
            elif "last month" in q:
                where += last_month_filter()
            return (
                "SELECT merchant, SUM(amount) as total "
                f"FROM transactions WHERE {where} "
                "GROUP BY merchant ORDER BY total DESC LIMIT 5;"
            )

        if "by category" in q or "spending by category" in q:
            where = f"user_id = {user_id}"
            if "this month" in q:
                where += month_filter()
            elif "last month" in q:
                where += last_month_filter()
            return (
                "SELECT category, SUM(amount) as total "
                f"FROM transactions WHERE {where} "
                "GROUP BY category ORDER BY total DESC;"
            )

        if "average" in q:
            where = f"user_id = {user_id}"
            if found_cat:
                where += f" AND category = '{found_cat}'"
            if "this month" in q:
                where += month_filter()
            elif "last month" in q:
                where += last_month_filter()
            return f"SELECT AVG(amount) as average FROM transactions WHERE {where};"

        if found_cat:
            where = f"user_id = {user_id} AND category = '{found_cat}'"
        else:
            where = f"user_id = {user_id}"

        if "last month" in q:
            where += last_month_filter()
        elif "this month" in q:
            where += month_filter()

        return f"SELECT SUM(amount) as total FROM transactions WHERE {where};"

    # Clean up common wrappers (code fences or leading text) from Gemini
    m = re.search(r"```(?:sql)?\n([\s\S]*?)```", resp, flags=re.IGNORECASE)
    if m:
        sql = m.group(1).strip()
    else:
        # Find first SELECT … occurrence
        idx = resp.upper().find("SELECT")
        if idx != -1:
            sql = resp[idx:].strip()
        else:
            sql = resp.strip()

    return sql
