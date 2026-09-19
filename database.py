import os
import psycopg2
from dotenv import load_dotenv
load_dotenv()


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "enterprise_workflow",
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD")
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def test_connection():
    try:
        connection = get_connection()
        print("PostgreSQL connection successful!")
        connection.close()
    except Exception as e:
        print("PostgreSQL connection failed:")
        print(e)


if __name__ == "__main__":
    test_connection()