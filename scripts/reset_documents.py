#!/usr/bin/env python3
"""
Reset completo de datos: borra documentos, chunks/embeddings, thesis_checks,
chat_history, feedbacks y sus archivos físicos. Conserva users y categories.

Uso:
    python scripts/reset_documents.py
"""

import os
import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / '.env')

DATABASE_URL = os.getenv('DATABASE_URL') or (
    f"postgresql://{os.getenv('POSTGRES_USER', 'upao_user')}"
    f":{os.getenv('POSTGRES_PASSWORD', 'upao_secret_2024')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}"
    f":{os.getenv('POSTGRES_PORT', '5433')}"
    f"/{os.getenv('POSTGRES_DB', 'upao_rag')}"
)

print(f"Conectando a la base de datos...")

try:
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
except psycopg2.OperationalError as e:
    print(f"Error de conexión: {e}", file=sys.stderr)
    sys.exit(1)

cur = conn.cursor()

# 1. Recoger rutas de archivos físicos
cur.execute("SELECT file_path FROM documents")
rows = cur.fetchall()

deleted_files = 0
missing_files = 0
for row in rows:
    fp = row['file_path']
    if fp:
        if os.path.exists(fp):
            os.remove(fp)
            deleted_files += 1
        else:
            missing_files += 1

# 2. Borrar todos los documentos (CASCADE → document_chunks + embeddings)
cur.execute("DELETE FROM documents")
doc_count = cur.rowcount

# 3. Borrar thesis_checks y sus archivos físicos
cur.execute("SELECT file_path FROM thesis_checks")
thesis_rows = cur.fetchall()
deleted_thesis_files = 0
missing_thesis_files = 0
for row in thesis_rows:
    fp = row['file_path']
    if fp and os.path.exists(fp):
        os.remove(fp)
        deleted_thesis_files += 1
    elif fp:
        missing_thesis_files += 1

cur.execute("DELETE FROM thesis_checks")
thesis_count = cur.rowcount

# 4. Borrar chat_history (CASCADE → feedbacks automáticamente)
cur.execute("DELETE FROM chat_history")
chat_count = cur.rowcount

# 5. Resetear contadores de categorías
cur.execute("UPDATE categories SET document_count = 0")

conn.commit()
cur.close()
conn.close()

print(f"\nLimpieza completada:")
print(f"  {doc_count} documentos eliminados de la DB (chunks y embeddings incluidos via CASCADE)")
print(f"  {deleted_files} archivos físicos de documentos borrados")
if missing_files:
    print(f"  {missing_files} rutas de documento no encontradas en disco (ya borradas previamente)")
print(f"  {thesis_count} thesis_checks eliminados de la DB")
print(f"  {deleted_thesis_files} archivos físicos de tesis borrados")
if missing_thesis_files:
    print(f"  {missing_thesis_files} rutas de tesis no encontradas en disco (ya borradas previamente)")
print(f"  {chat_count} mensajes de chat_history eliminados (feedbacks incluidos via CASCADE)")
print(f"  Contadores de categorías reseteados a 0")
