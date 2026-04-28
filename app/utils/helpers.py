"""Utility helper functions."""
def summarize_text(text: str, max_len: int = 200) -> str:
    return text if len(text) <= max_len else text[: max_len - 3] + "..."
