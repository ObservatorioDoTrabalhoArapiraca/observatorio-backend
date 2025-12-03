FROM python:3.9-slim

WORKDIR /app

# Instala netcat para verificar se o banco está pronto
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Caso tenha o arquivo de credenciais do BigQuery, copie para dentro do contêiner
# COPY auth_json/prefeitura-437123-bcbdff5c94df.json  auth_json/prefeitura-437123-bcbdff5c94df.json

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
# CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]