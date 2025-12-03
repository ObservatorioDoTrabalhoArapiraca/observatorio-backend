#!/bin/sh

# Espera o banco de dados estar pronto
# A variável de ambiente DB_HOST é definida no docker-compose.yml
echo "Waiting for postgres..."
while ! nc -z $DB_HOST 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Executa as migrações e inicia o servidor
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:8000