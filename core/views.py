# Lógica

from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
import os
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Avg, Max, Min, Count, Sum
from django.db.models.functions import Substr
from .models import Movimentacao, CagedEst, SaldoArapiraca



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




class CagedEstListView(APIView):
    """
    Lista todos os estabelecimentos com filtros opcionais
    """
    def get(self, request):
        # Pega parâmetros da URL (ex: ?municipio=Arapiraca&ano=2023)
        municipio = request.query_params.get('municipio', None)
        ano = request.query_params.get('ano', None)
        uf = request.query_params.get('uf', None)
        
        # Chave de cache dinâmica baseada nos filtros
        cache_key = f'cagedest_list_{municipio}_{ano}_{uf}'
        data = cache.get(cache_key)
        
        if data is None:
            queryset = CagedEst.objects.all()
            
            # Aplica filtros se fornecidos
            if municipio:
                queryset = queryset.filter(municipio__icontains=municipio)
            if ano:
                queryset = queryset.filter(ano=ano)
            if uf:
                queryset = queryset.filter(uf=uf)
            
            # Limita resultado e converte para dicionário
            results = queryset.values(
                'id', 'cnpj', 'razao_social', 'nome_fantasia', 
                'municipio', 'uf', 'secao', 'porte', 
                'ano', 'admissoes', 'desligamentos', 'saldo'
            )[:100]  # Limite de 100 registros
            
            data = list(results)
            cache.set(cache_key, data, 3600)  # Cache de 1 hora
        
        return Response({
            'total': len(data),
            'estabelecimentos': data
        })


class CagedEstStatsByMunicipioView(APIView):
    """
    Estatísticas de estabelecimentos por município
    """
    def get(self, request):
        data = cache.get('cagedest_stats_municipio')
        
        if data is None:
            results = CagedEst.objects.values('municipio', 'ano') \
                .annotate(
                    total_estabelecimentos=Count('id'),
                    total_admissoes=Sum('admissoes'),
                    total_desligamentos=Sum('desligamentos'),
                    saldo_total=Sum('saldo')
                ) \
                .order_by('-ano', 'municipio')
            
            data = list(results)
            cache.set('cagedest_stats_municipio', data, 3456000)
        
        return Response(data)


class CagedEstStatsBySetorView(APIView):
    """
    Estatísticas de estabelecimentos por setor (seção CNAE)
    """
    def get(self, request):
        municipio = request.query_params.get('municipio', None)
        cache_key = f'cagedest_stats_setor_{municipio}'
        
        data = cache.get(cache_key)
        
        if data is None:
            queryset = CagedEst.objects.all()
            
            if municipio:
                queryset = queryset.filter(municipio__icontains=municipio)
            
            results = queryset.values('secao', 'ano') \
                .annotate(
                    total_estabelecimentos=Count('id'),
                    total_admissoes=Sum('admissoes'),
                    total_desligamentos=Sum('desligamentos')
                ) \
                .order_by('-ano', 'secao')
            
            data = list(results)
            cache.set(cache_key, data, 3456000)
        
        return Response(data)


class CagedEstDetailView(APIView):
    """
    Detalhes de um estabelecimento específico por ID
    """
    def get(self, request, pk):
        try:
            estabelecimento = CagedEst.objects.get(pk=pk)
            data = {
                'id': estabelecimento.id,
                'cnpj': estabelecimento.cnpj,
                'razao_social': estabelecimento.razao_social,
                'nome_fantasia': estabelecimento.nome_fantasia,
                'municipio': estabelecimento.municipio,
                'uf': estabelecimento.uf,
                'cep': estabelecimento.cep,
                'endereco': f"{estabelecimento.logradouro}, {estabelecimento.numero}",
                'bairro': estabelecimento.bairro,
                'secao': estabelecimento.secao,
                'cnae_classe': estabelecimento.cnae_2_0_classe,
                'cnae_subclasse': estabelecimento.cnae_2_0_subclasse,
                'porte': estabelecimento.porte,
                'natureza_juridica': estabelecimento.natureza_juridica,
                'ano': estabelecimento.ano,
                'competencia': estabelecimento.competencia,
                'admissoes': estabelecimento.admissoes,
                'desligamentos': estabelecimento.desligamentos,
                'saldo': estabelecimento.saldo,
            }
            return Response(data)
        except CagedEst.DoesNotExist:
            return Response(
                {'error': 'Estabelecimento não encontrado'},
                status=404
            )


class CagedEstTopEmpregadoresView(APIView):
    """
    Top estabelecimentos que mais contrataram
    """
    def get(self, request):
        ano = request.query_params.get('ano', None)
        limite = int(request.query_params.get('limite', 10))
        
        cache_key = f'cagedest_top_empregadores_{ano}_{limite}'
        data = cache.get(cache_key)
        
        if data is None:
            queryset = CagedEst.objects.all()
            
            if ano:
                queryset = queryset.filter(ano=ano)
            
            results = queryset.order_by('-admissoes').values(
                'razao_social', 'nome_fantasia', 'municipio', 
                'secao', 'admissoes', 'desligamentos', 'saldo', 'ano'
            )[:limite]
            
            data = list(results)
            cache.set(cache_key, data, 3600)
        
        return Response(data),


# ============ ENDPOINTS ESPECÍFICOS PARA ARAPIRACA ============
class SaldoArapiracaListView(APIView):
    """
    Lista todos os períodos de Arapiraca
    """
    def get(self, request):
        data = cache.get('saldo_arapiraca_list')
        
        if data is None:
            results = SaldoArapiraca.objects.all().values()
            data = list(results)
            cache.set('saldo_arapiraca_list', data, 7200)
        
        return Response({
            'total': len(data),
            'periodos': data
        })

class SaldoArapiracaSerieView(APIView):
    """
    Série histórica consolidada de Arapiraca (2002-2019)
    """
    def get(self, request):
        data = cache.get('saldo_arapiraca_serie')
        
        if data is None:
            # Pega o registro da série histórica completa
            try:
                serie = SaldoArapiraca.objects.get(tipo_periodo='serie_historica')
                
                # Monta array com anos e valores
                anos_valores = []
                for ano in range(2002, 2020):
                    valor = getattr(serie, f'ano_{ano}', None)
                    if valor is not None:
                        anos_valores.append({
                            'ano': ano,
                            'saldo': valor
                        })
                
                data = {
                    'municipio': 'Arapiraca',
                    'uf': 'AL',
                    'periodo': serie.periodo,
                    'serie': anos_valores
                }
            except SaldoArapiraca.DoesNotExist:
                data = {'error': 'Série histórica não encontrada'}
            
            cache.set('saldo_arapiraca_serie', data, 7200)
        
        return Response(data)


class SaldoArapiracaByYearView(APIView):
    """
    Dados de Arapiraca para um ano específico
    """
    def get(self, request, ano):
        if ano < 2002 or ano > 2019:
            return Response({'error': 'Ano deve estar entre 2002 e 2019'}, status=400)
        
        cache_key = f'saldo_arapiraca_ano_{ano}'
        data = cache.get(cache_key)
        
        if data is None:
            # Busca todos os períodos que têm dados para esse ano
            periodos = SaldoArapiraca.objects.all()
            
            dados_ano = []
            for periodo in periodos:
                valor = getattr(periodo, f'ano_{ano}', None)
                if valor is not None:
                    dados_ano.append({
                        'periodo': periodo.periodo,
                        'tipo': periodo.tipo_periodo,
                        'saldo': valor
                    })
            
            data = {
                'ano': ano,
                'municipio': 'Arapiraca',
                'dados': dados_ano
            }
            cache.set(cache_key, data, 7200)
        
        return Response(data)

class SaldoArapiracaComparisonView(APIView):
    """
    Comparação entre anos
    """
    def get(self, request):
        data = cache.get('saldo_arapiraca_comparison')
        
        if data is None:
            try:
                serie = SaldoArapiraca.objects.get(tipo_periodo='serie_historica')
                
                # Calcula variações ano a ano
                comparacoes = []
                for ano in range(2003, 2020):
                    valor_atual = getattr(serie, f'ano_{ano}', None)
                    valor_anterior = getattr(serie, f'ano_{ano-1}', None)
                    
                    if valor_atual is not None and valor_anterior is not None:
                        variacao = valor_atual - valor_anterior
                        try:
                            percentual = (variacao / abs(valor_anterior)) * 100 if valor_anterior != 0 else 0
                        except:
                            percentual = 0
                        
                        comparacoes.append({
                            'ano': ano,
                            'saldo': valor_atual,
                            'saldo_anterior': valor_anterior,
                            'variacao_absoluta': variacao,
                            'variacao_percentual': round(percentual, 2)
                        })
                
                data = {
                    'municipio': 'Arapiraca',
                    'comparacoes': comparacoes
                }
            except SaldoArapiraca.DoesNotExist:
                data = {'error': 'Dados não encontrados'}
            
            cache.set('saldo_arapiraca_comparison', data, 7200)
        
        return Response(data)