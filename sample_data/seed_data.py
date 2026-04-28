"""Seed script to create a small finance DB for development."""
from app.database import get_connection
from datetime import date, timedelta


def seed():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            category TEXT,
            merchant TEXT,
            transaction_date TEXT
        )
        """
    )

    # Clear existing rows
    cur.execute("DELETE FROM transactions")

    # 29 sample rows across 3 users (user_id 1,2,3)
    samples = [
        (1, 250.00, "food", "Zomato", "2024-01-01"),
        (1, 500.00, "travel", "Uber", "2024-01-02"),
        (1, 1200.00, "shopping", "Amazon", "2024-01-03"),
        (1, 60.75, "food", "McDonalds", "2024-01-05"),
        (1, 15.00, "entertainment", "Netflix", "2024-01-07"),
        (1, 300.00, "utilities", "ElectricCo", "2024-01-10"),
        (2, 45.00, "food", "Dominos", "2024-01-04"),
        (2, 220.00, "travel", "Lyft", "2024-01-06"),
        (2, 75.50, "shopping", "Etsy", "2024-01-08"),
        (2, 1800.00, "rent", "Landlord", "2024-01-01"),
        (2, 12.99, "entertainment", "Spotify", "2024-01-09"),
        (2, -1500.00, "salary", "Employer", "2024-01-11"),
        (3, 9.99, "food", "Cafe", "2024-01-02"),
        (3, 320.00, "shopping", "BestBuy", "2024-01-05"),
        (3, 48.20, "travel", "Metro", "2024-01-07"),
        (3, 250.00, "food", "Zomato", "2024-01-12"),
        (3, 60.00, "utilities", "WaterCo", "2024-01-13"),
        (1, 420.00, "shopping", "Ikea", "2024-01-14"),
        (2, 30.00, "food", "KFC", "2024-01-15"),
        (3, 150.00, "entertainment", "Cinema", "2024-01-16"),
        (1, 85.00, "travel", "Uber", "2024-01-17"),
        (2, 60.00, "shopping", "Target", "2024-01-18"),
        (3, 950.00, "shopping", "Amazon", "2024-01-19"),
        (1, 20.00, "food", "StreetVendor", "2024-01-20"),
        (2, 125.00, "utilities", "InternetCo", "2024-01-21"),
        (3, 400.00, "rent", "Landlord", "2024-01-22"),
        (1, -2000.00, "salary", "Employer", "2024-01-25"),
        (2, 14.50, "entertainment", "PlayStore", "2024-01-26"),
        (3, 5.00, "food", "Bakery", "2024-01-27"),
    ]

    cur.executemany(
        "INSERT INTO transactions (user_id, amount, category, merchant, transaction_date) VALUES (?, ?, ?, ?, ?)",
        samples,
    )

    conn.commit()
    # verify count
    cur.execute("SELECT COUNT(*) as c FROM transactions")
    c = cur.fetchone()[0]
    conn.close()
    print(f"Seeded {c} transactions into the DB")


if __name__ == "__main__":
    seed()

