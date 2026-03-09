# ✅ Service: apps/movimentacoes/services/saldomov_ocupacao.py
# ✅ Serializer: Adicionar em serializers.py
# ✅ View: Adicionar em views.py
# ✅ URL: Adicionar em urls.py

# Exemplos de uso:
# Anual (saldo de movimentações por ocupação - todos os anos)
# curl "http://localhost:8000/api/analises/saldomov-ocupacao/"

# Anual filtrado por 2020
# curl "http://localhost:8000/api/analises/saldomov-ocupacao/?ano=2020"

# Top 10 ocupações com maior saldo positivo
# curl "http://localhost:8000/api/analises/saldomov-ocupacao/?ano=2020&top=10"

# Mensal de 2020
# curl "http://localhost:8000/api/analises/saldomov-ocupacao/?ano=2020&agregacao=mensal"

from django.db.models import Count, Sum, Q, Case, When, IntegerField
from .base import BaseDistribuicaoService, logger


class SaldoMovimentacaoPorOcupacaoService(BaseDistribuicaoService):
    """Serviço para calcular saldo de movimentações (admissões - demissões) por ocupação (CBO)"""
    
    def processar_mensal(self):
        """Calcula saldo mensal de movimentações por ocupação"""
        movimentacoes = self.queryset.filter(
            saldo_movimentacao__isnull=False,
            cbo2002_ocupacao__isnull=False
        ).values(
            'competencia_movimentacao',
            'cbo2002_ocupacao__codigo',
            'cbo2002_ocupacao__descricao'
        ).annotate(
            total_admissoes=Count('id', filter=Q(saldo_movimentacao=1)),
            total_demissoes=Count('id', filter=Q(saldo_movimentacao=-1)),
            total_movimentacoes=Count('id'),
            saldo=Sum('saldo_movimentacao')
        )
        
        registros_por_periodo = {}
        
        for mov in movimentacoes:
            ano, mes = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano and mes:
                cbo_codigo = mov['cbo2002_ocupacao__codigo']
                chave = (ano, mes, cbo_codigo)
                
                total_mov = mov['total_movimentacoes']
                saldo = mov['saldo'] or 0
                total_admissoes = mov['total_admissoes']
                total_demissoes = mov['total_demissoes']
                
                # Calcula percentual (saldo / total * 100)
                percentual = (saldo / total_mov * 100) if total_mov > 0 else 0
                
                registros_por_periodo[chave] = {
                    'ano': ano,
                    'mes': mes,
                    'cbo_codigo': cbo_codigo,
                    'cbo_descricao': mov['cbo2002_ocupacao__descricao'],
                    'saldo_movimentacoes': saldo,
                    'total_movimentacoes': total_mov,
                    'total_admissoes': total_admissoes,
                    'total_demissoes': total_demissoes,
                    'percentual': round(percentual, 2)
                }
        
        return list(registros_por_periodo.values())
    
    def processar_anual(self):
        """Calcula saldo anual de movimentações por ocupação"""
        movimentacoes = self.queryset.filter(
            saldo_movimentacao__isnull=False,
            cbo2002_ocupacao__isnull=False
        ).values(
            'competencia_movimentacao',
            'cbo2002_ocupacao__codigo',
            'cbo2002_ocupacao__descricao'
        ).annotate(
            total_admissoes=Count('id', filter=Q(saldo_movimentacao=1)),
            total_demissoes=Count('id', filter=Q(saldo_movimentacao=-1)),
            total_movimentacoes=Count('id'),
            saldo=Sum('saldo_movimentacao')
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
                        'saldo_movimentacoes': 0,
                        'total_movimentacoes': 0,
                        'total_admissoes': 0,
                        'total_demissoes': 0
                    }
                
                registros_por_ano[chave]['saldo_movimentacoes'] += mov['saldo'] or 0
                registros_por_ano[chave]['total_movimentacoes'] += mov['total_movimentacoes']
                registros_por_ano[chave]['total_admissoes'] += mov['total_admissoes']
                registros_por_ano[chave]['total_demissoes'] += mov['total_demissoes']
        
        # Calcula percentual final e formata dados
        data = []
        for reg in registros_por_ano.values():
            total_mov = reg['total_movimentacoes']
            saldo = reg['saldo_movimentacoes']
            percentual = (saldo / total_mov * 100) if total_mov > 0 else 0
            
            data.append({
                'ano': reg['ano'],
                'cbo_codigo': reg['cbo_codigo'],
                'cbo_descricao': reg['cbo_descricao'],
                'saldo_movimentacoes': saldo,
                'total_movimentacoes': total_mov,
                'total_admissoes': reg['total_admissoes'],
                'total_demissoes': reg['total_demissoes'],
                'percentual': round(percentual, 2)
            })
        
        # Ordena por saldo (maior primeiro - mais admissões)
        data.sort(key=lambda x: x['saldo_movimentacoes'], reverse=True)
        
        return data