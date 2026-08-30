import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("ALTER TABLE employees ADD COLUMN IF NOT EXISTS password_hash TEXT;")
conn.commit()
cursor.close()
conn.close()
print("Column added successfully!")