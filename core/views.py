from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from google.cloud import bigquery
import os

class MedianaSalarioView(APIView):
    def get(self, request):
        data = cache.get('mediana_salario_por_sexo')
        if data is None:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
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
            query_job = client.query(query)
            results = query_job.result()

            data = []
            for row in results:
                data.append({'sexo': row.sexo, 'mediana': row.mediana})


            cache.set('mediana_salario_por_sexo', data, 3456000)

        return Response(data)


class AnoTotalMovimentacoesView(APIView):
    def get(self, request):
        data = cache.get('ano_total_movimentacoes')
        if data is None:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
            client = bigquery.Client()

            query_ano_total = """
                SELECT
                    SUBSTR(`competênciamov`, 1, 4) AS ano,
                    COUNT(*) AS total
                FROM `observatorio-do-trabalho.caged.movimentacoes`
                GROUP BY ano
                ORDER BY ano
            """

            results_ano_total = client.query(query_ano_total).result()

            ano_total_list = []
            for row in results_ano_total:
                ano_total_list.append({
                    "ano": row.ano,
                    "total": row.total
                })

            data = {
                "ano_total_results": ano_total_list,
            }
            cache.set('ano_total_movimentacoes', data, 3456000)

        return Response(data)


class MedianaSalarioPorEscolaridadeView(APIView): 
    def get(self, request):
        data = cache.get('salario_por_escolaridade')
        if data is None:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
            client = bigquery.Client()

            query_salario_por_escolaridade = """
                  SELECT `graudeinstrução` as escolaridade, APPROX_QUANTILES(`salário`, 2)[OFFSET(1)] as saldo, max(`salário`) as maior ,min(`salário`) as menor 
                  FROM `observatorio-do-trabalho.caged.movimentacoes` 
                  group by `graudeinstrução` 
            """

            results_salario_por_escolaridade = client.query(query_salario_por_escolaridade).result()

            salario_por_escoalridade_list = []
            for row in results_salario_por_escolaridade:
                salario_por_escoalridade_list.append({
                    "escolaridade": row.escolaridade,
                    "saldo": row.saldo,
                    "maior": row.maior,
                    "menor": row.menor
                })

            data = {
                "salario_por_escolaridade": salario_por_escoalridade_list,
            }
            cache.set('salario_por_escolaridade', data, 3456000)

        return Response(data)

class MedianaSalarioPorFaixaEtariaView(APIView):
    def get(self, request):
        data = cache.get('mediana_salario_faixa_etaria')

        if data is None:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
            client = bigquery.Client()

            query = """
                SELECT
                    CASE
                        WHEN idade BETWEEN 40 AND 49 THEN '40 A 49 anos'
                        WHEN idade BETWEEN 50 AND 64 THEN '50 A 64 anos'
                        WHEN idade BETWEEN 30 AND 39 THEN '30 A 39 anos'
                        WHEN idade BETWEEN 18 AND 24 THEN '18 A 24 anos'
                        WHEN idade BETWEEN 25 AND 29 THEN '25 A 29 anos'
                        WHEN idade >= 65 THEN '65 anos ou mais'
                        WHEN idade BETWEEN 15 AND 17 THEN '15 A 17 anos'
                        WHEN idade BETWEEN 10 AND 14 THEN '10 A 14 anos'
                        ELSE 'Outras idades'
                    END AS faixa_etaria,
                    APPROX_QUANTILES(`salário`, 2)[OFFSET(1)] AS mediana_salario
                FROM `observatorio-do-trabalho.caged.movimentacoes`
                GROUP BY faixa_etaria
                ORDER BY CASE
                    WHEN faixa_etaria = '10 A 14 anos' THEN 1
                    WHEN faixa_etaria = '15 A 17 anos' THEN 2
                    WHEN faixa_etaria = '18 A 24 anos' THEN 3
                    WHEN faixa_etaria = '25 A 29 anos' THEN 4
                    WHEN faixa_etaria = '30 A 39 anos' THEN 5
                    WHEN faixa_etaria = '40 A 49 anos' THEN 6
                    WHEN faixa_etaria = '50 A 64 anos' THEN 7
                    WHEN faixa_etaria = '65 anos ou mais' THEN 8
                    ELSE 9
                END
            """

            results = client.query(query).result()

            # Converte para lista de dicionários
            data = []
            for row in results:
                if row.faixa_etaria != 'Outras idades':  
                    data.append({
                        'faixa_etaria': row.faixa_etaria,
                        'mediana_salario': row.mediana_salario
                    })

            # Cache por 1 mês e 10 dias (3456000 segundos)
            cache.set('mediana_salario_faixa_etaria', data, 3456000)

        return Response(data)
