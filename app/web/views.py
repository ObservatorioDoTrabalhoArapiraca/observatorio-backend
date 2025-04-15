from django.http import JsonResponse
from app.use_cases.buscar_dados import buscar_dados

def get_bigquery_data(request):
    try:
        dados = buscar_dados()
        return JsonResponse(dados, safe=False)
    except Exception as e:
        return JsonResponse({'error': 'Erro ao buscar dados', 'details': str(e)}, status=500)