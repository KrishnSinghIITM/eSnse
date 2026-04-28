"""Generate human-friendly insights from query results using Gemini."""
from typing import Any, Optional
import json

from app.services.llm_service import ask_gemini


def generate_insight(question: str, result: Any, rows: Optional[list] = None) -> str:
    """Generate a friendly, human-readable answer from query result.

    Takes the original question and the SQL result, sends it to Gemini
    to generate a natural, conversational response.

    Args:
        question: The original user question (e.g., "How much did I spend on food?")
        result: The query result (could be a single value, list, or formatted string)
        rows: Optional raw rows from the query for context

    Returns:
        A friendly, human-readable answer.
    """
    # Format result for Gemini
    if isinstance(result, (list, tuple)):
        try:
            result_str = json.dumps(result, indent=2, default=str)
        except Exception:
            result_str = str(result)
    else:
        result_str = str(result)

    prompt_lines = [
        "You are a friendly financial assistant.",
        "A user asked: " + question,
        "The query result is: " + result_str,
        "Write a short, friendly, non-technical answer to the user's question based on the result.",
        "Use casual language and format numbers nicely (e.g., use ₹ for Indian rupees if appropriate).",
        "Keep the answer to 1-2 sentences max.",
        "Respond ONLY with the answer, no preamble.",
    ]
    prompt = "\n".join(prompt_lines)

    friendly_answer = ask_gemini(prompt)
    if friendly_answer and not friendly_answer.lower().startswith("gemini") and "request failed" not in friendly_answer.lower():
        return friendly_answer

    def _normalize_rows(data: Any) -> list[dict]:
        normalized: list[dict] = []
        if not isinstance(data, list):
            return normalized

        for item in data:
            if isinstance(item, dict):
                normalized.append(item)
                continue
            if hasattr(item, "keys"):
                try:
                    normalized.append({key: item[key] for key in item.keys()})
                    continue
                except Exception:
                    pass
            normalized.append({"value": str(item)})
        return normalized

    def _format_currency(value: Any) -> str:
        try:
            number = float(value)
            if number.is_integer():
                return f"₹{int(number)}"
            return f"₹{number:.2f}"
        except Exception:
            return str(value)

    normalized_rows = _normalize_rows(rows if rows is not None else result)

    if isinstance(result, dict):
        normalized = {str(key).lower(): value for key, value in result.items()}
        if "average" in normalized or "avg" in normalized:
            value = normalized.get("average", normalized.get("avg"))
            return f"Your average spend was {_format_currency(value)}."
        if "total" in normalized:
            value = normalized.get("total")
            if "food" in question.lower():
                return f"You've spent {_format_currency(value)} on food."
            if "travel" in question.lower():
                return f"You've spent {_format_currency(value)} on travel."
            return f"Your total spending was {_format_currency(value)}."

    if len(normalized_rows) == 1:
        row = normalized_rows[0]
        lowered = {str(key).lower(): key for key in row.keys()}
        if "average" in lowered or "avg" in lowered:
            value = row[lowered.get("average", lowered.get("avg"))]
            return f"Your average spend was {_format_currency(value)}."
        if "total" in lowered:
            value = row[lowered["total"]]
            if "food" in question.lower():
                return f"You've spent {_format_currency(value)} on food."
            if "travel" in question.lower():
                return f"You've spent {_format_currency(value)} on travel."
            return f"Your total spending was {_format_currency(value)}."

    if normalized_rows:
        if all("category" in {str(key).lower() for key in item.keys()} for item in normalized_rows):
            parts = []
            for item in normalized_rows[:5]:
                lower_keys = {str(key).lower(): key for key in item.keys()}
                category_key = lower_keys.get("category")
                total_key = lower_keys.get("total")
                if category_key and total_key:
                    parts.append(f"{item[category_key]} {_format_currency(item[total_key])}")
            if parts:
                return "Spending by category: " + ", ".join(parts) + "."

        if all("merchant" in {str(key).lower() for key in item.keys()} for item in normalized_rows):
            parts = []
            for item in normalized_rows[:5]:
                lower_keys = {str(key).lower(): key for key in item.keys()}
                merchant_key = lower_keys.get("merchant")
                total_key = lower_keys.get("total")
                if merchant_key and total_key:
                    parts.append(f"{item[merchant_key]} {_format_currency(item[total_key])}")
            if parts:
                return "Top merchants this month: " + ", ".join(parts) + "."

    return result_str
