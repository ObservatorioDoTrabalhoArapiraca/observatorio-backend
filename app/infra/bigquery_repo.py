# app/infra/bigquery_repo.py

from google.cloud import bigquery
from app.interfaces.repositories import BigQueryRepository

class BigQueryRepositorio(BigQueryRepository):
    def __init__(self):
        self.client = bigquery.Client()

    def buscar_dados(self):
        query = """
            SELECT * 
            FROM `observatorio-do-trabalho.caged.movimentacoes`
            LIMIT 10
        """
        query_job = self.client.query(query)
        results = query_job.result()
        return [dict(row) for row in results]
