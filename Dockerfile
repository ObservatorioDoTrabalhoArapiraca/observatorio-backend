FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Caso tenha o arquivo de credenciais do BigQuery, copie para dentro do contêiner
COPY auth_json/observatorio-do-trabalho-f5b9d719a42e.json  /app/observatorio-do-trabalho-f5b9d719a42e.json

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]