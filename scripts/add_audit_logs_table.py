import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id SERIAL PRIMARY KEY,
        thread_id VARCHAR(100) NOT NULL,
        employee_id VARCHAR(20),
        agent_name VARCHAR(50) NOT NULL,
        action VARCHAR(50) NOT NULL,
        tool_name VARCHAR(100),
        status VARCHAR(20) NOT NULL,
        duration_ms INTEGER,
        detail TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
""")
conn.commit()
cursor.close()
conn.close()
print("audit_logs table created successfully!")