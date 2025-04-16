from django.http import JsonResponse
from app.services.buscar_dados import BuscarDados
from app.infra.bigquery.count_by_year_repo import CountByYearRepository

def get_dados(request):
    caso = BuscarDados(CountByYearRepository())
    dados = caso.executar()
    return JsonResponse(dados, safe=False)
