from google.cloud import bigquery
from app.domain.ports.count_by_year_repository import BigQueryRepository

class CountByYearRepository(BigQueryRepository):
    def get_dados(self):
        client = bigquery.Client()
        query = """
            SELECT SUBSTR(`competênciamov`, 1, 4) AS ano, COUNT(*) AS total
            FROM `observatorio-do-trabalho.caged.movimentacoes`
            GROUP BY ano
            ORDER BY ano;SELECT * 
            FROM `observatorio-do-trabalho.caged.movimentacoes`
            LIMIT 10
        """
        results = client.query(query).result()
        return [dict(row) for row in results]
