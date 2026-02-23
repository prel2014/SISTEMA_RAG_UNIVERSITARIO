#!/usr/bin/env python3
"""
Script para conectarse a PostgreSQL y ejecutar una consulta via CLI.

Uso básico:
    python scripts/query_db.py -q "SELECT * FROM users LIMIT 5"

Con parámetros:
    python scripts/query_db.py -q "SELECT * FROM users WHERE role = %s" -p admin

Sobrescribir conexión:
    python scripts/query_db.py --host localhost --port 5433 --db upao_rag -q "SELECT NOW()"

Desde archivo .sql:
    python scripts/query_db.py -f scripts/mi_consulta.sql

Ver ayuda:
    python scripts/query_db.py --help
"""

import argparse
import os
import sys

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))


# ─── CLI ──────────────────────────────────────────────────────────────────────
def parse_args():
    parser = argparse.ArgumentParser(
        description="Ejecuta una consulta SQL en PostgreSQL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Conexión (opcional, usa .env como fallback)
    conn_group = parser.add_argument_group("conexión (opcional, usa .env por defecto)")
    conn_group.add_argument("--host",     default=None, help="Host del servidor")
    conn_group.add_argument("--port",     type=int, default=None, help="Puerto (default: 5433)")
    conn_group.add_argument("--db",       default=None, dest="dbname", help="Nombre de la base de datos")
    conn_group.add_argument("--user",     default=None, help="Usuario de PostgreSQL")
    conn_group.add_argument("--password", default=None, help="Contraseña")

    # Consulta (una de las dos es requerida)
    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument("-q", "--query", help="Consulta SQL entre comillas")
    query_group.add_argument("-f", "--file",  help="Ruta a un archivo .sql")

    # Parámetros de la consulta
    parser.add_argument(
        "-p", "--params",
        nargs="+",
        metavar="VALOR",
        default=[],
        help="Parámetros para los %s en la consulta (separados por espacio)",
    )

    # Salida
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limita el número de filas mostradas (no modifica la query)",
    )

    return parser.parse_args()


# ─── Conexión ─────────────────────────────────────────────────────────────────
def build_config(args) -> dict:
    return {
        "host":     args.host     or os.getenv("POSTGRES_HOST", "localhost"),
        "port":     args.port     or int(os.getenv("POSTGRES_PORT", 5433)),
        "dbname":   args.dbname   or os.getenv("POSTGRES_DB", "upao_rag"),
        "user":     args.user     or os.getenv("POSTGRES_USER", "postgres"),
        "password": args.password or os.getenv("POSTGRES_PASSWORD", ""),
    }


# ─── Impresión ────────────────────────────────────────────────────────────────
def print_rows(rows: list, limit: int | None):
    if limit:
        rows = rows[:limit]

    if not rows:
        print("  (sin resultados)")
        return

    # Calcular ancho de cada columna
    cols = list(rows[0].keys())
    widths = {c: max(len(c), max(len(str(r[c])) for r in rows)) for c in cols}

    sep   = "+-" + "-+-".join("-" * widths[c] for c in cols) + "-+"
    header = "| " + " | ".join(c.ljust(widths[c]) for c in cols) + " |"

    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = "| " + " | ".join(str(row[c]).ljust(widths[c]) for c in cols) + " |"
        print(line)
    print(sep)


# ─── Ejecución ────────────────────────────────────────────────────────────────
def run():
    args = parse_args()
    config = build_config(args)

    # Resolver query
    if args.file:
        try:
            with open(args.file, encoding="utf-8") as f:
                query = f.read()
        except FileNotFoundError:
            print(f"Error: archivo '{args.file}' no encontrado.", file=sys.stderr)
            sys.exit(1)
    else:
        query = args.query

    params = tuple(args.params)

    # Ejecutar
    conn = None
    try:
        print(f"Conectando a {config['host']}:{config['port']}/{config['dbname']}...")
        conn = psycopg2.connect(**config, cursor_factory=psycopg2.extras.RealDictCursor)
        conn.autocommit = True

        with conn.cursor() as cur:
            cur.execute(query, params)

            if cur.description:                  # SELECT
                rows = [dict(r) for r in cur.fetchall()]
                print(f"\n{len(rows)} fila(s) encontrada(s):\n")
                print_rows(rows, args.limit)
            else:                                # INSERT / UPDATE / DELETE
                print(f"\n{cur.rowcount} fila(s) afectada(s).")

    except psycopg2.OperationalError as e:
        print(f"Error de conexión: {e}", file=sys.stderr)
        sys.exit(1)
    except psycopg2.Error as e:
        print(f"Error SQL: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if conn:
            conn.close()
            print("\nConexión cerrada.")


if __name__ == "__main__":
    run()
