"""Generate human-friendly insights from query results using Gemini."""
from typing import Any, Optional
import json

from app.services.llm_service import ask_gemini


def _normalize_key(name: Any) -> str:
    return str(name).strip().lower()


def _is_metric_key(name: Any, metric: str) -> bool:
    normalized = _normalize_key(name)
    return metric in normalized or normalized.startswith(f"{metric}(") or normalized.endswith(f"_{metric}")


def _find_key(row: dict, candidates: tuple[str, ...], metric: str | None = None) -> str | None:
    lowered = {_normalize_key(key): key for key in row.keys()}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    if metric is not None:
        for key in row.keys():
            if _is_metric_key(key, metric):
                return key
    return None


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
        normalized = {_normalize_key(key): value for key, value in result.items()}
        average_value = normalized.get("average", normalized.get("avg"))
        if average_value is not None:
            return f"Your average spend was {_format_currency(average_value)}."
        total_value = normalized.get("total")
        if total_value is not None:
            if "food" in question.lower():
                return f"You've spent {_format_currency(total_value)} on food."
            if "travel" in question.lower():
                return f"You've spent {_format_currency(total_value)} on travel."
            return f"Your total spending was {_format_currency(total_value)}."

    if len(normalized_rows) == 1:
        row = normalized_rows[0]
        average_key = _find_key(row, ("average", "avg"), metric="avg")
        if average_key is not None:
            value = row[average_key]
            return f"Your average spend was {_format_currency(value)}."
        total_key = _find_key(row, ("total",), metric="sum")
        if total_key is not None:
            value = row[total_key]
            if "food" in question.lower():
                return f"You've spent {_format_currency(value)} on food."
            if "travel" in question.lower():
                return f"You've spent {_format_currency(value)} on travel."
            return f"Your total spending was {_format_currency(value)}."

    if normalized_rows:
        if all(any(_normalize_key(key) == "category" for key in item.keys()) for item in normalized_rows):
            parts = []
            for item in normalized_rows[:5]:
                category_key = _find_key(item, ("category",))
                total_key = _find_key(item, ("total",), metric="sum")
                if category_key and total_key:
                    parts.append(f"{item[category_key]} {_format_currency(item[total_key])}")
            if parts:
                return "Spending by category: " + ", ".join(parts) + "."

        if all(any(_normalize_key(key) == "merchant" for key in item.keys()) for item in normalized_rows):
            parts = []
            for item in normalized_rows[:5]:
                merchant_key = _find_key(item, ("merchant",))
                total_key = _find_key(item, ("total",), metric="sum")
                if merchant_key and total_key:
                    parts.append(f"{item[merchant_key]} {_format_currency(item[total_key])}")
            if parts:
                return "Top merchants this month: " + ", ".join(parts) + "."

    return result_str
