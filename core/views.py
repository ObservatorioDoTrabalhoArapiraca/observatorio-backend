from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
import os
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Avg, Max, Min, Count
from django.db.models.functions import Substr
from .models import Movimentacao

class MedianaSalarioView(APIView):
    def get(self, request):
        data = cache.get('mediana_salario_por_sexo')
        if data is None:
            # Esta é uma aproximação. O Django ORM não tem uma função de mediana direta.
            # Uma alternativa é buscar todos os salários e calcular a mediana em Python,
            # o que pode ser ineficiente. AVG é usado aqui como um substituto.
            results = Movimentacao.objects.values('sexo').annotate(mediana=Avg('salario')).order_by('sexo')
            data = list(results)
            cache.set('mediana_salario_por_sexo', data, 3456000)
        return Response(data)

class AnoTotalMovimentacoesView(APIView):
    def get(self, request):
        data = cache.get('ano_total_movimentacoes')
        if data is None:
            results = Movimentacao.objects.annotate(ano=Substr('competencia_mov', 1, 4)) \
                                          .values('ano') \
                                          .annotate(total=Count('id')) \
                                          .order_by('ano')
            data = { "ano_total_results": list(results) }
            cache.set('ano_total_movimentacoes', data, 3456000)
        return Response(data)

class MedianaSalarioPorEscolaridadeView(APIView): 
    def get(self, request):
        data = cache.get('salario_por_escolaridade')
        if data is None:
            results = Movimentacao.objects.values('grau_de_instrucao') \
                                          .annotate(saldo=Avg('salario'), maior=Max('salario'), menor=Min('salario'))
            
            data = { "salario_por_escolaridade": list(results) }
            cache.set('salario_por_escolaridade', data, 3456000)
        return Response(data)

class MedianaSalarioPorFaixaEtariaView(APIView):
    def get(self, request):
        data = cache.get('mediana_salario_faixa_etaria')
        if data is None:
            # A lógica de faixa etária complexa é melhor tratada no código Python
            # ou com anotações mais complexas se o banco de dados suportar.
            # Esta é uma consulta simplificada.
            results = Movimentacao.objects.values('faixa_etaria') \
                                          .annotate(mediana_salario=Avg('salario')) \
                                          .order_by('faixa_etaria')
            data = list(results)
            cache.set('mediana_salario_faixa_etaria', data, 3456000)
        return Response(data)
    
class SalarioPorProfissaoView(APIView):
    def get(self, request):
        data = cache.get('salario_por_profissao')
        if data is None:
            results = Movimentacao.objects.values('cbo_2002_ocupacao') \
                                          .annotate(maximo=Max('salario'), minimo=Min('salario'), media=Avg('salario'), total=Count('id')) \
                                          .order_by('cbo_2002_ocupacao')
            
            # A lógica de substituição de nome de profissão permanece a mesma
            substituicoes = {
                "Gerente de facility management": "Gerente de facility management",
                "Cientista de dados": "Cientista de dados",
                "Massoterapeuta": "Massoterapeuta",
                "Auxiliar de faturamento": "Auxiliar de faturamento"
            }
            
            processed_data = []
            for row in results:
                profissao = row['cbo_2002_ocupacao']
                row['profissao'] = substituicoes.get(profissao, profissao)
                del row['cbo_2002_ocupacao']
                processed_data.append(row)

            data = processed_data
            cache.set('salario_por_profissao', data, 3456000)
        return Response(data)

class ListarPdfsView(APIView):
    def get(self, request):
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        try:
            files = os.listdir(pdf_dir)
        except FileNotFoundError:
            files = []

        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()

        pdf_files = [
            {
                'name': f,
                'url': f"{protocol}://{host}{settings.MEDIA_URL}pdfs/{f}"
            }
            for f in files if f.lower().endswith('.pdf')
        ]
        return JsonResponse(pdf_files, safe=False)

