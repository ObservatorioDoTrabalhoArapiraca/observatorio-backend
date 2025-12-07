#!/bin/sh

# Verifica se está rodando no Render (tem DATABASE_URL) ou Docker local (tem DB_HOST)
if [ -n "$DATABASE_URL" ]; then
    # Rodando no Render/Produção
    echo "Running in production mode (Render)..."
    echo "Skipping host check, using DATABASE_URL..."
else
    # Rodando no Docker local
    echo "Running in development mode (Docker)..."
    echo "Waiting for postgres..."
    while ! nc -z ${DB_HOST:-postgres} 5432; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

# Coleta arquivos estáticos
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Executa as migrações
echo "Running migrations..."
python manage.py migrate

# Inicia o servidor
echo "Starting gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --timeout 120