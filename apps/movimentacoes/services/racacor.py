# Anual (todos os anos)
# curl "http://localhost:8000/api/analises/raca-cor/"

# Anual filtrado por 2020
# curl "http://localhost:8000/api/analises/raca-cor/?ano=2020"

# Mensal de 2020
# curl "http://localhost:8000/api/analises/raca-cor/?ano=2020&agregacao=mensal"

# Janeiro de 2020
# curl "http://localhost:8000/api/analises/raca-cor/?ano=2020&mes=1&agregacao=mensal"

from django.db.models import Count
from .base import BaseDistribuicaoService, logger
from .utils import carregar_mapeamento_referencia
from apps.referenciais.models import RacaCorReferencia


class DistribuicaoRacaCorService(BaseDistribuicaoService):
    """Serviço para distribuição por raça/cor"""
    
    def __init__(self, queryset):
        super().__init__(queryset)
        self.raca_cor_map = carregar_mapeamento_referencia(RacaCorReferencia)
    
    def processar_mensal(self):
        """Processa distribuição mensal"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao',
            'raca_cor__codigo'
        ).annotate(total=Count('id'))
        
        registros_por_periodo = {}
        
        for mov in movimentacoes:
            ano, mes = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano and mes:
                raca_cor_codigo = mov['raca_cor__codigo']
                chave = (ano, mes)
                
                if chave not in registros_por_periodo:
                    registros_por_periodo[chave] = {}
                
                if raca_cor_codigo:
                    registros_por_periodo[chave][raca_cor_codigo] = mov['total']
        
        data = []
        for (ano, mes), racas in registros_por_periodo.items():
            total_periodo = sum(racas.values())
            
            for raca_cod, qtd in racas.items():
                percentual = (qtd / total_periodo * 100) if total_periodo > 0 else 0
                
                data.append({
                    'ano': ano,
                    'mes': mes,
                    'raca_cor': raca_cod,
                    'raca_cor_descricao': self.raca_cor_map.get(raca_cod, 'Desconhecido'),
                    'total_movimentacoes': qtd,
                    'percentual': round(percentual, 2)
                })
        
        return data
    
    def processar_anual(self):
        """Processa distribuição anual"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao',
            'raca_cor__codigo'
        ).annotate(total=Count('id'))
        
        registros_por_ano = {}
        
        for mov in movimentacoes:
            ano, _ = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano:
                raca_cor_codigo = mov['raca_cor__codigo']
                
                if ano not in registros_por_ano:
                    registros_por_ano[ano] = {}
                
                if raca_cor_codigo:
                    if raca_cor_codigo not in registros_por_ano[ano]:
                        registros_por_ano[ano][raca_cor_codigo] = 0
                    registros_por_ano[ano][raca_cor_codigo] += mov['total']
        
        data = []
        for ano, racas in registros_por_ano.items():
            total_ano = sum(racas.values())
            
            for raca_cod, qtd in racas.items():
                percentual = (qtd / total_ano * 100) if total_ano > 0 else 0
                
                data.append({
                    'ano': ano,
                    'raca_cor': raca_cod,
                    'raca_cor_descricao': self.raca_cor_map.get(raca_cod, 'Desconhecido'),
                    'total_movimentacoes': qtd,
                    'percentual': round(percentual, 2)
                })
        
        return data