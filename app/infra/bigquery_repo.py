from google.cloud import bigquery
from app.interfaces.repositories import BigQueryRepository

class BigQueryRepositoryImpl(BigQueryRepository):
    def __init__(self):
        self.client = bigquery.Client()

    def buscar_dados(self, query: str):
        query_job = self.client.query(query)
        return [dict(row) for row in query_job.result()]
