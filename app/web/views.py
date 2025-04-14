from django.http import JsonResponse
from app.infrastructure.bigquery_repo import BigQueryRepositoryImpl
from app.use_cases.buscar_dados import BuscarDadosUseCase

def dados_view(request):
    repo = BigQueryRepositoryImpl()
    use_case = BuscarDadosUseCase(repo)
    dados = use_case.execute("SELECT 'teste' AS exemplo")
    return JsonResponse(dados, safe=False)
