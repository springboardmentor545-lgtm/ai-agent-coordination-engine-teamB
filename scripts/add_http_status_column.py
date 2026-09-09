import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS http_status INTEGER;")
conn.commit()
cursor.close()
conn.close()
print("http_status column added successfully!")