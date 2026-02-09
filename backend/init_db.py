"""Initialize the database by running tables.sql and procedures.sql."""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)

# Build DATABASE_URL
DATABASE_URL = os.getenv('DATABASE_URL') or (
    f"postgresql://{os.getenv('POSTGRES_USER', 'upao_user')}"
    f":{os.getenv('POSTGRES_PASSWORD', 'upao_secret_2024')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}"
    f":{os.getenv('POSTGRES_PORT', '5433')}"
    f"/{os.getenv('POSTGRES_DB', 'upao_rag')}"
)

SQL_DIR = Path(__file__).resolve().parent.parent / 'postgresql'


def run_sql_file(conn, filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()
    print(f"  OK: {filepath.name}")


def main():
    print(f"Connecting to: {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    try:
        print("Running tables.sql...")
        run_sql_file(conn, SQL_DIR / 'tables.sql')
        print("Running procedures.sql...")
        run_sql_file(conn, SQL_DIR / 'procedures.sql')
        print("Database initialized successfully.")
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        conn.rollback()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
