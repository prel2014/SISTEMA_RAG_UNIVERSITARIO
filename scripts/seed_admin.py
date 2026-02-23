"""
Seed admin user into PostgreSQL.
Uses Werkzeug's generate_password_hash directly (same as Flask backend).

Usage:
    python scripts/seed_admin.py
"""

import os
import sys
import psycopg2
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@upao.edu.pe')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Clave123')
ADMIN_FULL_NAME = os.getenv('ADMIN_FULL_NAME', 'Administrador')

DB_CONFIG = {
    'user': os.getenv('POSTGRES_USER', 'upao_user'),
    'password': os.getenv('POSTGRES_PASSWORD', 'Clave123'),
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5433')),
    'dbname': os.getenv('POSTGRES_DB', 'upao_rag'),
}


def main():
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print(f"Conectado a PostgreSQL ({DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']})")

        # Check if admin already exists
        cur.execute("SELECT id, email FROM users WHERE email = %s", (ADMIN_EMAIL,))
        existing = cur.fetchone()

        if existing:
            print(f"Admin ya existe: {ADMIN_EMAIL} (id: {existing[0]})")
            return

        # Generate hash with Werkzeug (mismo algoritmo que el backend)
        password_hash = generate_password_hash(ADMIN_PASSWORD)

        cur.execute(
            """INSERT INTO users (email, password_hash, full_name, role, is_active)
               VALUES (%s, %s, %s, 'admin', TRUE)
               RETURNING id, email, full_name, role""",
            (ADMIN_EMAIL, password_hash, ADMIN_FULL_NAME)
        )
        admin = cur.fetchone()
        conn.commit()

        print("Admin creado exitosamente:")
        print(f"  ID:     {admin[0]}")
        print(f"  Email:  {admin[1]}")
        print(f"  Nombre: {admin[2]}")
        print(f"  Role:   {admin[3]}")
        print(f"  Pass:   {ADMIN_PASSWORD}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    main()
