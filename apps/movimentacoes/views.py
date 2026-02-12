from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db import models 
from rest_framework import status
from .models import Movimentacao
from django.db.models import Count, Avg, Sum, Q, FloatField, F, Case, When, IntegerField
from django.db.models.functions import Cast

from .serializers import (
    DistribuicaoSexoSerializer,
    DistribuicaoIdadeSerializer,
    DistribuicaoEscolaridadeSerializer,
    DistribuicaoRacaCorSerializer,
    DistribuicaoPcdSerializer,
    MovimentacaoSerializer,
    SalarioMedioPorOcupacaoSerializer,
    DistribuicaoOcupacaoSerializer,
)
from .services import (
    DistribuicaoSexoService,
    DistribuicaoIdadeService,
    DistribuicaoEscolaridadeService,
    DistribuicaoRacaCorService,
    DistribuicaoPcdService,
    SalarioMedioPorOcupacaoService,
    DistribuicaoOcupacaoService
)
import logging

logger = logging.getLogger(__name__)
from rest_framework.pagination import PageNumberPagination

class MovimentacaoPagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class DistribuicaoSexoView(APIView):
    """Distribuição de movimentações por sexo"""
    
    def get(self, request):
        ano = request.query_params.get('ano')
        mes = request.query_params.get('mes')
        agregacao = request.query_params.get('agregacao', 'anual')
        
        # Queryset base
        queryset = Movimentacao.objects.filter(sexo_id__isnull=False)
        
        if queryset.count() == 0:
            return Response(
                {'error': 'Nenhum registro encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Aplica filtros via service
        try:
            service = DistribuicaoSexoService(queryset)
            service.aplicar_filtro_ano(ano).aplicar_filtro_mes(mes)
            
            # Processa
            if agregacao == 'mensal':
                data = service.processar_mensal()
            else:
                data = service.processar_anual()
            
            serializer = DistribuicaoSexoSerializer(data, many=True)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DistribuicaoIdadeView(APIView):
    """Distribuição de movimentações por faixa etária"""
    
    def get(self, request):
        ano = request.query_params.get('ano')
        mes = request.query_params.get('mes')
        agregacao = request.query_params.get('agregacao', 'anual')
        
        queryset = Movimentacao.objects.filter(idade__isnull=False)
        
        if queryset.count() == 0:
            return Response(
                {'error': 'Nenhum registro encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            service = DistribuicaoIdadeService(queryset)
            service.aplicar_filtro_ano(ano).aplicar_filtro_mes(mes)
            
            if agregacao == 'mensal':
                data = service.processar_mensal()
            else:
                data = service.processar_anual()
            
            serializer = DistribuicaoIdadeSerializer(data, many=True)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DistribuicaoEscolaridadeView(APIView):
    """Distribuição de movimentações por escolaridade"""
    
    def get(self, request):
        ano = request.query_params.get('ano')
        mes = request.query_params.get('mes')
        agregacao = request.query_params.get('agregacao', 'anual')
        
        queryset = Movimentacao.objects.filter(grau_instrucao_id__isnull=False)
        
        if queryset.count() == 0:
            return Response(
                {'error': 'Nenhum registro encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            service = DistribuicaoEscolaridadeService(queryset)
            service.aplicar_filtro_ano(ano).aplicar_filtro_mes(mes)
            
            if agregacao == 'mensal':
                data = service.processar_mensal()
            else:
                data = service.processar_anual()
            
            serializer = DistribuicaoEscolaridadeSerializer(data, many=True)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class DistribuicaoRacaCorView(APIView):
    def get(self, request):
        ano = request.query_params.get('ano')
        mes = request.query_params.get('mes')
        agregacao = request.query_params.get('agregacao', 'anual')
        
        # 2️⃣ Queryset base (apenas registros com raça/cor)
        queryset = Movimentacao.objects.filter(raca_cor_id__isnull=False)
        
        # 3️⃣ Valida se há dados
        if queryset.count() == 0:
            return Response(
                {'error': 'Nenhum registro encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 4️⃣ Aplica filtros e processa
        try:
            # Cria instância do service
            service = DistribuicaoRacaCorService(queryset)
            
            # Aplica filtros de ano e mês
            service.aplicar_filtro_ano(ano).aplicar_filtro_mes(mes)
            
            # Processa de acordo com a agregação
            if agregacao == 'mensal':
                data = service.processar_mensal()
            else:
                data = service.processar_anual()
            
            # 5️⃣ Serializa e retorna
            serializer = DistribuicaoRacaCorSerializer(data, many=True)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
class DistribuicaoPcdView(APIView):
    """Distribuição de movimentações por tipo de deficiência (PCD)"""
    
    def get(self, request):
        """
        Retorna distribuição por tipo de deficiência.
        
        Query Parameters:
            - ano (int, opcional): Filtrar por ano
            - mes (int, opcional): Filtrar por mês (1-12)
            - agregacao (str, opcional): 'mensal' ou 'anual' (padrão: 'anual')
        
        Exemplos:
            - /api/analises/pcd/?ano=2020
            - /api/analises/pcd/?ano=2020&mes=1
            - /api/analises/pcd/?ano=2020&agregacao=mensal
        """
        # Pega os parâmetros da URL
        ano = request.query_params.get('ano')
        mes = request.query_params.get('mes')
        agregacao = request.query_params.get('agregacao', 'anual')
        
        # Queryset base (apenas registros com tipo de deficiência)
        queryset = Movimentacao.objects.filter(tipo_deficiencia_id__isnull=False)
        
        # Valida se há dados
        if queryset.count() == 0:
            return Response(
                {'error': 'Nenhum registro encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Aplica filtros e processa
        try:
            service = DistribuicaoPcdService(queryset)
            service.aplicar_filtro_ano(ano).aplicar_filtro_mes(mes)
            
            if agregacao == 'mensal':
                data = service.processar_mensal()
            else:
                data = service.processar_anual()
            
            serializer = DistribuicaoPcdSerializer(data, many=True)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            

class SalarioMedioPorOcupacaoView(APIView):
    """Calcula salário médio por ocupação (CBO)"""
    
    def get(self, request):
        ano = request.query_params.get('ano')
        mes = request.query_params.get('mes')
        agregacao = request.query_params.get('agregacao', 'anual')
        top = request.query_params.get('top')  # Top N ocupações
        
        queryset = Movimentacao.objects.filter(
            salario__isnull=False,
            salario__gt=0,
            cbo2002_ocupacao__isnull=False
        )
        
        if queryset.count() == 0:
            return Response(
                {'error': 'Nenhum registro encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            service = SalarioMedioPorOcupacaoService(queryset)
            service.aplicar_filtro_ano(ano).aplicar_filtro_mes(mes)
            
            if agregacao == 'mensal':
                data = service.processar_mensal()
            else:
                data = service.processar_anual()
            
            # Filtra top N se solicitado
            if top:
                try:
                    top_n = int(top)
                    data = data[:top_n]
                except ValueError:
                    pass
            
            serializer = SalarioMedioPorOcupacaoSerializer(data, many=True)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DistribuicaoOcupacaoView(APIView):
    """Distribuição de movimentações por ocupação (CBO)"""
    
    def get(self, request):
        ano = request.query_params.get('ano')
        mes = request.query_params.get('mes')
        agregacao = request.query_params.get('agregacao', 'anual')
        top = request.query_params.get('top')
        
        queryset = Movimentacao.objects.filter(cbo2002_ocupacao__isnull=False)
        
        if queryset.count() == 0:
            return Response(
                {'error': 'Nenhum registro encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            service = DistribuicaoOcupacaoService(queryset)
            service.aplicar_filtro_ano(ano).aplicar_filtro_mes(mes)
            
            if agregacao == 'mensal':
                data = service.processar_mensal()
            else:
                data = service.processar_anual()
            
            # Filtra top N se solicitado
            if top:
                try:
                    top_n = int(top)
                    data = data[:top_n]
                except ValueError:
                    pass
            
            serializer = DistribuicaoOcupacaoSerializer(data, many=True)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class MovimentacoesListView(APIView):
    """
    View para listar todas as movimentações com contagem total
    """
    
    def get(self, request):
        # === PARÂMETROS ===
        ano = request.query_params.get('ano')
        mes = request.query_params.get('mes')
        agregacao = request.query_params.get('agregacao', 'mensal')
        detalhes = request.query_params.get('detalhes', 'true').lower() == 'true'
        
        # Filtros opcionais
        municipio = request.query_params.get('municipio')
        tipo_movimentacao = request.query_params.get('tipo_movimentacao')
        sexo = request.query_params.get('sexo')
        raca_cor = request.query_params.get('raca_cor')
        grau_instrucao = request.query_params.get('grau_instrucao')
        
        # === VALIDAÇÃO ===
        if ano:
            try:
                ano = int(ano)
            except ValueError:
                return Response(
                    {'error': 'O parâmetro "ano" deve ser um número inteiro'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        queryset = Movimentacao.objects.all()
        if ano:
            if agregacao == 'anual':
                queryset = queryset.filter(
                    competencia_movimentacao__gte=ano * 100,
                    competencia_movimentacao__lt=(ano + 1) * 100
                )
            else:  # mensal
                if mes:
                    try:
                        mes = int(mes)
                        if mes < 1 or mes > 12:
                            return Response(
                                {'error': 'O parâmetro "mes" deve estar entre 1 e 12'},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        competencia = ano * 100 + mes
                        queryset = queryset.filter(competencia_movimentacao=competencia)
                    except ValueError:
                        return Response(
                            {'error': 'O parâmetro "mes" deve ser um número inteiro'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                else:
                    queryset = queryset.filter(
                        competencia_movimentacao__gte=ano * 100,
                        competencia_movimentacao__lt=(ano + 1) * 100
                    )
        
        # === FILTROS OPCIONAIS ===
        if municipio:
            queryset = queryset.filter(municipio_id=municipio)
        if tipo_movimentacao:
            queryset = queryset.filter(tipo_movimentacao_id=tipo_movimentacao)
        if sexo:
            queryset = queryset.filter(sexo_id=sexo)
        if raca_cor:
            queryset = queryset.filter(raca_cor_id=raca_cor)
        if grau_instrucao:
            queryset = queryset.filter(grau_instrucao_id=grau_instrucao)
        
        # === CALCULAR TOTAL ===
        total_movimentacoes = queryset.count()
        
        # === METADADOS ===
        filtros_aplicados = {
            'agregacao': agregacao,
            'ano': ano,
        }
        if ano: filtros_aplicados['ano'] = ano
        if mes:
            filtros_aplicados['mes'] = mes
        if municipio:
            filtros_aplicados['municipio'] = municipio
        if tipo_movimentacao:
            filtros_aplicados['tipo_movimentacao'] = tipo_movimentacao
        if sexo:
            filtros_aplicados['sexo'] = sexo
        if raca_cor:
            filtros_aplicados['raca_cor'] = raca_cor
        if grau_instrucao:
            filtros_aplicados['grau_instrucao'] = grau_instrucao
        
        # === RESPOSTA BASE ===
        response_data = {
            'total_movimentacoes': total_movimentacoes,
            'filtros_aplicados': filtros_aplicados,
        }
        
        # === SE DETALHES=TRUE, ADICIONA DADOS PAGINADOS ===
        if detalhes:
            # Otimizar queries com select_related
            queryset = queryset.select_related(
                'regiao', 'uf', 'municipio', 'secao', 'subclasse',
                'cbo2002_ocupacao', 'categoria', 'grau_instrucao',
                'raca_cor', 'sexo', 'tipo_empregador',
                'tipo_estabelecimento', 'tipo_movimentacao', 'tipo_deficiencia'
            ).order_by('-competencia_movimentacao', 'id')
            
            # Paginação
            paginator = MovimentacaoPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            
            # Serializar
            serializer = MovimentacaoSerializer(paginated_queryset, many=True)
            
            # Adicionar dados paginados
            response_data['paginacao'] = {
                'page': paginator.page.number,
                'page_size': paginator.page_size,
                'total_pages': paginator.page.paginator.num_pages,
                'links': {
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                }
            }
            response_data['resultados'] = serializer.data
        
        return Response(response_data, status=status.HTTP_200_OK)