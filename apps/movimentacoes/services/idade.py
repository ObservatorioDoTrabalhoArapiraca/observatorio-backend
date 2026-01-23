# Anual
# curl "http://localhost:8000/api/analises/idade/?ano=2020"

# Mensal
# curl "http://localhost:8000/api/analises/idade/?ano=2020&agregacao=mensal"

# Específico
# curl "http://localhost:8000/api/analises/idade/?ano=2020&mes=1&agregacao=mensal"

from django.db.models import Count

from .base import BaseDistribuicaoService, logger


class DistribuicaoIdadeService(BaseDistribuicaoService):
    """Serviço para distribuição por faixa etária"""
    
    FAIXAS_ETARIAS = [
        (0, 17, 'Até 17 anos'),
        (18, 24, '18-24 anos'),
        (25, 29, '25-29 anos'),
        (30, 39, '30-39 anos'),
        (40, 49, '40-49 anos'),
        (50, 64, '50-64 anos'),
        (65, 999, '65 anos ou mais'),
    ]
    
    def get_faixa_etaria(self, idade):
        """Retorna a faixa etária de uma idade"""
        if idade is None:
            return None
        
        for min_idade, max_idade, descricao in self.FAIXAS_ETARIAS:
            if min_idade <= idade <= max_idade:
                return descricao
        return None
    
    def processar_mensal(self):
        """Processa distribuição mensal"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao', 
            'idade'
        ).annotate(total=Count('id'))
        
        registros_por_periodo = {}
        
        for mov in movimentacoes:
            ano, mes = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano and mes:
                faixa = self.get_faixa_etaria(mov['idade'])
                if faixa:
                    chave = (ano, mes, faixa)
                    if chave not in registros_por_periodo:
                        registros_por_periodo[chave] = 0
                    registros_por_periodo[chave] += mov['total']
        
        # Calcula totais por período
        periodos = {}
        for (ano, mes, faixa), qtd in registros_por_periodo.items():
            periodo = (ano, mes)
            if periodo not in periodos:
                periodos[periodo] = 0
            periodos[periodo] += qtd
        
        # Formata resultado
        data = []
        for (ano, mes, faixa), qtd in registros_por_periodo.items():
            total_periodo = periodos[(ano, mes)]
            percentual = (qtd / total_periodo * 100) if total_periodo > 0 else 0
            
            data.append({
                'ano': ano,
                'mes': mes,
                'faixa_etaria': faixa,
                'total_movimentacoes': qtd,
                'percentual': round(percentual, 2)
            })
        
        return data
    
    def processar_anual(self):
        """Processa distribuição anual"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao', 
            'idade'
        ).annotate(total=Count('id'))
        
        registros_por_ano = {}
        
        for mov in movimentacoes:
            ano, _ = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano:
                faixa = self.get_faixa_etaria(mov['idade'])
                if faixa:
                    chave = (ano, faixa)
                    if chave not in registros_por_ano:
                        registros_por_ano[chave] = 0
                    registros_por_ano[chave] += mov['total']
        
        # Calcula totais por ano
        anos = {}
        for (ano, faixa), qtd in registros_por_ano.items():
            if ano not in anos:
                anos[ano] = 0
            anos[ano] += qtd
        
        # Formata resultado
        data = []
        for (ano, faixa), qtd in registros_por_ano.items():
            total_ano = anos[ano]
            percentual = (qtd / total_ano * 100) if total_ano > 0 else 0
            
            data.append({
                'ano': ano,
                'faixa_etaria': faixa,
                'total_movimentacoes': qtd,
                'percentual': round(percentual, 2)
            })
        
        return data