from django.http import JsonResponse
from app.services.buscar_dados import BuscarDados
from app.infra.bigquery.salary_per_sex_repo import SalaryPerSexRepository

def get_salary_per_sex(request):
    caso = BuscarDados(SalaryPerSexRepository())
    dados = caso.executar()
    return JsonResponse(dados, safe=False)