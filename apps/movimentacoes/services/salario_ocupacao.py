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
        
        movimentacoes_com_salario_zero = self.queryset.filter(salario=0.00).count()
        print(f"[DEBUG] movimentacoes_com_salario_zero: {movimentacoes_com_salario_zero}")
         
        movimentacoes_validas = self.queryset.filter(
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
       
        observacao = (
            f"Foram desconsideradas {movimentacoes_com_salario_zero} movimentações com salário 0.00 nos cálculos."
            if movimentacoes_com_salario_zero > 0 else "Não houve movimentações com salário 0.00."
        )
        
        registros_por_periodo = {}
        
        for mov in movimentacoes_validas:
            ano_mov, mes_mov = self.extrair_periodo(mov['competencia_movimentacao'])
            cbo_codigo = mov['cbo2002_ocupacao__codigo']
            chave = (ano_mov, mes_mov, cbo_codigo)
            
            registros_por_periodo[chave] = {
                'ano': ano_mov,
                'mes': mes_mov,
                'cbo_codigo': cbo_codigo,
                'observacao': observacao,
                'mov_zero': movimentacoes_com_salario_zero,
                'cbo_descricao': mov['cbo2002_ocupacao__descricao'],
                'salario_medio': round(float(mov['salario_medio']), 2),
                'total_movimentacoes': mov['total_movimentacoes']
            }
        resultado = list(registros_por_periodo.values())
        
        return resultado
            
    
    def processar_anual(self, ano=None):
        """Calcula média salarial anual por ocupação"""
        movimentacoes_com_salario_zero = self.queryset.filter(salario=0).count()
        
       
        movimentacoes_validas = self.queryset.filter(
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
        
        observacao = (
            f"Foram desconsideradas {movimentacoes_com_salario_zero} movimentações com salário 0.00 nos cálculos."
            if movimentacoes_com_salario_zero > 0 else "Não houve movimentações com salário 0.00."
        )
        
        registros_por_ano = {}
        
        for mov in movimentacoes_validas:
            ano_mov, _ = self.extrair_periodo(mov['competencia_movimentacao'])
           
            cbo_codigo = mov['cbo2002_ocupacao__codigo']
            chave = (ano_mov, cbo_codigo)
                
              
            if chave not in registros_por_ano:
                registros_por_ano[chave] = {
                    'ano': ano_mov,
                    'cbo_codigo': cbo_codigo,
                    'cbo_descricao': mov['cbo2002_ocupacao__descricao'],
                    'salario_total': 0,
                    'total_movimentacoes': 0,
                    'observacao': observacao,
                    'mov_zero': movimentacoes_com_salario_zero
                }
            
                registros_por_ano[chave]['salario_total'] += float(mov['salario_medio']) * mov['total_movimentacoes']
                registros_por_ano[chave]['total_movimentacoes'] += mov['total_movimentacoes']
        
        # Calcula média final
        data = []
        for reg in registros_por_ano.values():
            # salario_medio = (
            #     reg['salario_total'] / reg['total_movimentacoes']
            #     if reg['total_movimentacoes'] > 0 else 0
            # )
            
            reg['salario_medio'] = round(reg['salario_total'] / reg['total_movimentacoes'], 2) if reg['total_movimentacoes'] > 0 else 0
            reg.pop('salario_total')  # Remove o campo 'salario_total', pois não é necessário no retorno
            data.append(reg)
        
        # Ordena por salário médio (maior primeiro)
        # if movimentacoes_com_salario_zero > 0:
        #     for registro in data:
        #         registro['observacao'] = (
        #             f"Foram desconsideradas {movimentacoes_com_salario_zero} movimentações com salário 0.00 nos cálculos."
        #         )

        return sorted(data, key=lambda x: x['salario_medio'], reverse=True)