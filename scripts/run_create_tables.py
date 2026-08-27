import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

with open("scripts/create_tables.sql", "r") as f:
    sql = f.read()

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    print("Tables created successfully!")
    cursor.close()
    conn.close()
except Exception as e:
    print("Table creation failed.")
    print("Error:", e)