from google.cloud import bigquery
from app.domain.ports.count_by_year_repository import BigQueryRepository

class SalaryPerSexRepository(BigQueryRepository):
    def get_dados(self):
        client = bigquery.Client()
        query = """
            SELECT
                sexo,
                APPROX_QUANTILES(`salário`, 2)[OFFSET(1)] AS mediana
                FROM
                `observatorio-do-trabalho.caged.movimentacoes`
                GROUP BY
                sexo
        """
        results = client.query(query).result()
        return [dict(row) for row in results]