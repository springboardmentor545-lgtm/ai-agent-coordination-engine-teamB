import os
import psycopg2
from dotenv import load_dotenv
from datetime import date

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def seed_holidays():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM holidays;")

    holidays = [
        (date(2026, 1, 26), "Republic Day"),
        (date(2026, 8, 15), "Independence Day"),
        (date(2026, 10, 2), "Gandhi Jayanti"),
        (date(2026, 9, 11), "Test Holiday (mid-week, for demo purposes)"),
        (date(2026, 12, 25), "Christmas"),
    ]
    cursor.executemany(
        "INSERT INTO holidays (holiday_date, name) VALUES (%s, %s);",
        holidays
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Holidays seeded successfully!")

if __name__ == "__main__":
    seed_holidays()