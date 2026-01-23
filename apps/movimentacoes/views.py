from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Movimentacao

from .serializers import (
    DistribuicaoSexoSerializer,
    DistribuicaoIdadeSerializer,
    DistribuicaoEscolaridadeSerializer,
    DistribuicaoRacaCorSerializer,
    DistribuicaoPcdSerializer,
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