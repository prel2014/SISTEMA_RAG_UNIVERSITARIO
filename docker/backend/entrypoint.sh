#!/bin/bash
set -e

echo "Esperando a que PostgreSQL este listo..."
while ! python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
    sleep 2
done
echo "PostgreSQL listo."

echo "Ejecutando migraciones..."
if [ ! -f "migrations/env.py" ]; then
    echo "Inicializando migraciones por primera vez..."
    rm -rf migrations
    flask db init
    flask db migrate -m "Initial migration"
fi
flask db upgrade

echo "Ejecutando seeds..."
flask seed run

echo "Iniciando servidor..."
if [ "$FLASK_ENV" = "development" ]; then
    flask run --host=0.0.0.0 --port=5050 --reload
else
    gunicorn -w 4 -b 0.0.0.0:5050 --timeout 120 wsgi:app
fi
