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
    
    
    def processar_mensal(self, ano=None, mes=None):
        """Calcula média salarial mensal por ocupação"""

        # movimentacoes_com_salario_zero = self.queryset.filter(salario=0.00).count()
        # print(f"[DEBUG] movimentacoes_com_salario_zero: {movimentacoes_com_salario_zero}")
         
        movimentacoes_validas = self.queryset.values(
            'competencia_movimentacao',
            'cbo2002_ocupacao__codigo',
            'cbo2002_ocupacao__descricao'
        ).annotate(
            salario_medio=Avg('salario', filter=Q(salario__gt=0)),
            total_movimentacoes=Count('id', filter=Q(salario__gt=0)),
            movimentacoes_com_salario_zero=Count('id', filter=Q(salario=0))
        )
       
       
        registros_por_periodo = {}
        
        for mov in movimentacoes_validas:
            if mov['total_movimentacoes'] == 0 and mov['movimentacoes_com_salario_zero'] == 0:
                continue

            ano_mov, mes_mov = self.extrair_periodo(mov['competencia_movimentacao'])
            if (ano is None or ano == ano_mov) and (mes is None or mes == mes_mov):
                cbo_codigo = mov['cbo2002_ocupacao__codigo']
                chave = (ano_mov, mes_mov, cbo_codigo)
                
                movimentacoes_com_salario_zero = mov['movimentacoes_com_salario_zero']
                obs = (
                    f"Foram desconsideradas {movimentacoes_com_salario_zero} movimentações com salário 0.00 nos cálculos."
                    if movimentacoes_com_salario_zero > 0 else "Não houve movimentações com salário 0.00."
                )

                registros_por_periodo[chave] = {
                    'ano': ano_mov,
                    'mes': mes_mov,
                    'cbo_codigo': cbo_codigo,
                    'cbo_descricao': mov['cbo2002_ocupacao__descricao'],
                    'salario_medio': round(float(mov['salario_medio'] or 0), 2),
                    'total_movimentacoes': mov['total_movimentacoes'],
                    'observacao': obs,
                    'mov_zero': movimentacoes_com_salario_zero
                }
        return list(registros_por_periodo.values())
            
    
    def processar_anual(self, ano=None):
        """Calcula média salarial anual por ocupação"""
        # movimentacoes_com_salario_zero = self.queryset.filter(salario=0).count()
        
       
        movimentacoes_validas = self.queryset.values(
            'competencia_movimentacao',
            'cbo2002_ocupacao__codigo',
            'cbo2002_ocupacao__descricao'
        ).annotate(
            salario_medio=Avg('salario', filter=Q(salario__gt=0)),
            total_movimentacoes=Count('id', filter=Q(salario__gt=0)),
            movimentacoes_com_salario_zero=Count('id', filter=Q(salario=0))
        )
        
        registros_por_ano = {}
        
        
        for mov in movimentacoes_validas:
            ano_mov, _ = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano is None or ano == ano_mov:
                cbo_codigo = mov['cbo2002_ocupacao__codigo']
                chave = (ano_mov, cbo_codigo)
                
                if chave not in registros_por_ano:
                    registros_por_ano[chave] = {
                        'ano': ano_mov,
                        'cbo_codigo': cbo_codigo,
                        'cbo_descricao': mov['cbo2002_ocupacao__descricao'],
                        'salario': 0,
                        'total_movimentacoes': 0,
                        'mov_zero': 0
                    }
                
                # Soma os valores para o CBO no ano
                if mov['salario_medio']:
                    registros_por_ano[chave]['salario'] += float(mov['salario_medio']) * mov['total_movimentacoes']
                
                registros_por_ano[chave]['total_movimentacoes'] += mov['total_movimentacoes']
                registros_por_ano[chave]['mov_zero'] += mov['movimentacoes_com_salario_zero']

        data = []
        for reg in registros_por_ano.values():
            m_z = reg['mov_zero']
            reg['salario_medio'] = round(reg['salario'] / reg['total_movimentacoes'], 2) if reg['total_movimentacoes'] > 0 else 0
            reg['observacao'] = (
                f"Foram desconsideradas {m_z} movimentações com salário 0.00 nos cálculos."
                if m_z > 0 else "Não houve movimentações com salário 0.00."
            )
            reg.pop('salario')
            data.append(reg)
        
        return sorted(data, key=lambda x: x['salario_medio'], reverse=True)