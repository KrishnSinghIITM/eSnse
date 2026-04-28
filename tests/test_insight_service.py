from app.services.insight_service import generate_insight


def test_generate_insight_formats_aliased_sum(monkeypatch):
    monkeypatch.setattr(
        "app.services.insight_service.ask_gemini",
        lambda prompt: "Gemini client not installed or not configured. Set GEMINI_API_KEY in .env to enable.",
    )

    rows = [{"SUM(amount)": 330.75}]

    assert generate_insight("How much did I spend on food?", rows, rows) == "You've spent ₹330.75 on food."


def test_generate_insight_formats_category_sums(monkeypatch):
    monkeypatch.setattr(
        "app.services.insight_service.ask_gemini",
        lambda prompt: "Gemini client not installed or not configured. Set GEMINI_API_KEY in .env to enable.",
    )

    rows = [
        {"category": "shopping", "SUM(amount)": 1620},
        {"category": "travel", "SUM(amount)": 585},
        {"category": "food", "SUM(amount)": 330.75},
    ]

    assert generate_insight("Show spending by category", rows, rows) == (
        "Spending by category: shopping ₹1620, travel ₹585, food ₹330.75."
    )