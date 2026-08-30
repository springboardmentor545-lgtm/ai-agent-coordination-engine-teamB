import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("ALTER TABLE sessions ADD COLUMN IF NOT EXISTS extend_locked BOOLEAN NOT NULL DEFAULT FALSE;")
conn.commit()
cursor.close()
conn.close()
print("Column added successfully!")