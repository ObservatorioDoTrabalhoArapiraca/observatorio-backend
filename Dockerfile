FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Caso tenha o arquivo de credenciais do BigQuery, copie para dentro do contêiner
COPY auth_json/prefeitura-437123-bcbdff5c94df.json  auth_json/prefeitura-437123-bcbdff5c94df.json

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000"]