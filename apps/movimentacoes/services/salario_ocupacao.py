# ✅ Service: apps/movimentacoes/services/salario_ocupacao.py
# ✅ Serializer: Adicionar em serializers.py
# ✅ View: Adicionar em views.py
# ✅ URL: Adicionar em urls.py

# Anual (média salarial por ocupação - todos os anos)
# curl "http://localhost:8000/api/analises/salario-ocupacao/"

# Anual filtrado por 2020
# curl "http://localhost:8000/api/analises/salario-ocupacao/?ano=2020"

# Top 10 ocupações com maior salário médio
# curl "http://localhost:8000/api/analises/salario-ocupacao/?ano=2020&top=10"

# Mensal de 2020
# curl "http://localhost:8000/api/analises/salario-ocupacao/?ano=2020&agregacao=mensal"


from django.db.models import Avg, Count, Q
from .base import BaseDistribuicaoService, logger


class SalarioMedioPorOcupacaoService(BaseDistribuicaoService):
    """Serviço para calcular salário médio por ocupação (CBO)"""
    
    def processar_mensal(self):
        """Calcula média salarial mensal por ocupação"""
        movimentacoes = self.queryset.filter(
            salario__isnull=False,
            salario__gt=0,
            cbo2002_ocupacao__isnull=False
        ).values(
            'competencia_movimentacao',
            'cbo2002_ocupacao__codigo',
            'cbo2002_ocupacao__descricao'
        ).annotate(
            salario_medio=Avg('salario'),
            total_movimentacoes=Count('id')
        )
        
        registros_por_periodo = {}
        
        for mov in movimentacoes:
            ano, mes = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano and mes:
                cbo_codigo = mov['cbo2002_ocupacao__codigo']
                chave = (ano, mes, cbo_codigo)
                
                registros_por_periodo[chave] = {
                    'ano': ano,
                    'mes': mes,
                    'cbo_codigo': cbo_codigo,
                    'cbo_descricao': mov['cbo2002_ocupacao__descricao'],
                    'salario_medio': round(float(mov['salario_medio']), 2),
                    'total_movimentacoes': mov['total_movimentacoes']
                }
        
        return list(registros_por_periodo.values())
    
    def processar_anual(self):
        """Calcula média salarial anual por ocupação"""
        movimentacoes = self.queryset.filter(
            salario__isnull=False,
            salario__gt=0,
            cbo2002_ocupacao__isnull=False
        ).values(
            'competencia_movimentacao',
            'cbo2002_ocupacao__codigo',
            'cbo2002_ocupacao__descricao'
        ).annotate(
            salario_medio=Avg('salario'),
            total_movimentacoes=Count('id')
        )
        
        registros_por_ano = {}
        
        for mov in movimentacoes:
            ano, _ = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano:
                cbo_codigo = mov['cbo2002_ocupacao__codigo']
                chave = (ano, cbo_codigo)
                
                if chave not in registros_por_ano:
                    registros_por_ano[chave] = {
                        'ano': ano,
                        'cbo_codigo': cbo_codigo,
                        'cbo_descricao': mov['cbo2002_ocupacao__descricao'],
                        'salario_total': 0,
                        'total_movimentacoes': 0
                    }
                
                registros_por_ano[chave]['salario_total'] += float(mov['salario_medio']) * mov['total_movimentacoes']
                registros_por_ano[chave]['total_movimentacoes'] += mov['total_movimentacoes']
        
        # Calcula média final
        data = []
        for reg in registros_por_ano.values():
            salario_medio = (
                reg['salario_total'] / reg['total_movimentacoes']
                if reg['total_movimentacoes'] > 0 else 0
            )
            
            data.append({
                'ano': reg['ano'],
                'cbo_codigo': reg['cbo_codigo'],
                'cbo_descricao': reg['cbo_descricao'],
                'salario_medio': round(salario_medio, 2),
                'total_movimentacoes': reg['total_movimentacoes']
            })
        
        # Ordena por salário médio (maior primeiro)
        data.sort(key=lambda x: x['salario_medio'], reverse=True)
        
        return data