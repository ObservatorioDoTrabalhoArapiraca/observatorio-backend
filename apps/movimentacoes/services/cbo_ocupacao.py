# Anual (todas as ocupações - todos os anos)
# curl "http://localhost:8000/api/analises/ocupacao/"

# Anual filtrado por 2020
# curl "http://localhost:8000/api/analises/ocupacao/?ano=2020"

# Top 10 ocupações mais frequentes
# curl "http://localhost:8000/api/analises/ocupacao/?ano=2020&top=10"

# Mensal de 2020
# curl "http://localhost:8000/api/analises/ocupacao/?ano=2020&agregacao=mensal"

# Janeiro de 2020
# curl "http://localhost:8000/api/analises/ocupacao/?ano=2020&mes=1&agregacao=mensal"

from django.db.models import Count
from .base import BaseDistribuicaoService, logger


class DistribuicaoOcupacaoService(BaseDistribuicaoService):
    """Serviço para distribuição por ocupação (CBO 2002)"""
    
    def processar_mensal(self):
        movimentacoes = self.queryset.values(
            'competencia_movimentacao',           # Ex: 202001
            'cbo2002_ocupacao__codigo',           # Ex: "414105"
            'cbo2002_ocupacao__descricao'         # Ex: "Vendedor"
        ).annotate(
            total=Count('id') 
        )
        
        registros_por_periodo = {}
        
        for mov in movimentacoes:
            
            ano, mes = self.extrair_periodo(mov['competencia_movimentacao'])
            
            if ano and mes:
                cbo_codigo = mov['cbo2002_ocupacao__codigo']
                chave = (ano, mes)
                
                if chave not in registros_por_periodo:
                    registros_por_periodo[chave] = {}
                
                # Armazena a quantidade para aquela ocupação
                if cbo_codigo is not None:
                    registros_por_periodo[chave][cbo_codigo] = {
                        'descricao': mov['cbo2002_ocupacao__descricao'],
                        'total': mov['total']
                    }
        
        data = []
        for (ano, mes), ocupacoes in registros_por_periodo.items():
            # Total de movimentações no período
            total_periodo = sum(ocp['total'] for ocp in ocupacoes.values())
            
            # Para cada ocupação, calcula percentual
            for cbo_cod, info in ocupacoes.items():
                percentual = (
                    (info['total'] / total_periodo * 100) 
                    if total_periodo > 0 else 0
                )
                
                data.append({
                    'ano': ano,
                    'mes': mes,
                    'cbo_codigo': cbo_cod,
                    'cbo_descricao': info['descricao'],
                    'total_movimentacoes': info['total'],
                    'percentual': round(percentual, 2)
                })
        
        
        data.sort(key=lambda x: (x['ano'], x['mes'], -x['total_movimentacoes']))
        
        return data
    
    def processar_anual(self):
        movimentacoes = self.queryset.values(
            'competencia_movimentacao',
            'cbo2002_ocupacao__codigo',
            'cbo2002_ocupacao__descricao'
        ).annotate(
            total=Count('id')
        )
        
        registros_por_ano = {}
        
        for mov in movimentacoes:
            ano, _ = self.extrair_periodo(mov['competencia_movimentacao'])
            
            if ano:
                cbo_codigo = mov['cbo2002_ocupacao__codigo']
                
                # Cria dicionário do ano se não existir
                if ano not in registros_por_ano:
                    registros_por_ano[ano] = {}
                
                # Acumula totais (pode ter múltiplos meses)
                if cbo_codigo is not None:
                    if cbo_codigo not in registros_por_ano[ano]:
                        registros_por_ano[ano][cbo_codigo] = {
                            'descricao': mov['cbo2002_ocupacao__descricao'],
                            'total': 0
                        }
                    
                    registros_por_ano[ano][cbo_codigo]['total'] += mov['total']
        
        data = []
        for ano, ocupacoes in registros_por_ano.items():
            total_ano = sum(ocp['total'] for ocp in ocupacoes.values())
            
            for cbo_cod, info in ocupacoes.items():
                percentual = (
                    (info['total'] / total_ano * 100) 
                    if total_ano > 0 else 0
                )
                
                data.append({
                    'ano': ano,
                    'cbo_codigo': cbo_cod,
                    'cbo_descricao': info['descricao'],
                    'total_movimentacoes': info['total'],
                    'percentual': round(percentual, 2)
                })
        
        data.sort(key=lambda x: (x['ano'], -x['total_movimentacoes']))
        
        return data