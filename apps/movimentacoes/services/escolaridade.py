# # Anual
# curl "http://localhost:8000/api/analises/escolaridade/?ano=2020"

# Mensal
# curl "http://localhost:8000/api/analises/escolaridade/?ano=2020&agregacao=mensal"

# Específico
# curl "http://localhost:8000/api/analises/escolaridade/?ano=2020&mes=1&agregacao=mensal"

from django.db.models import Count
from .base import BaseDistribuicaoService, logger


class DistribuicaoEscolaridadeService(BaseDistribuicaoService):
    """Serviço para distribuição por escolaridade"""
    
    def processar_mensal(self):
        """Processa distribuição mensal"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao',
            'grau_instrucao__codigo',
            'grau_instrucao__descricao'
        ).annotate(total=Count('id'))
        
        registros_por_periodo = {}
        
        for mov in movimentacoes:
            ano, mes = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano and mes:
                codigo = mov['grau_instrucao__codigo']
                descricao = mov['grau_instrucao__descricao']
                
                chave = (ano, mes, codigo, descricao)
                if chave not in registros_por_periodo:
                    registros_por_periodo[chave] = 0
                registros_por_periodo[chave] += mov['total']
        
        # Calcula totais
        periodos = {}
        for (ano, mes, cod, desc), qtd in registros_por_periodo.items():
            periodo = (ano, mes)
            if periodo not in periodos:
                periodos[periodo] = 0
            periodos[periodo] += qtd
        
        # Formata resultado
        data = []
        for (ano, mes, cod, desc), qtd in registros_por_periodo.items():
            total_periodo = periodos[(ano, mes)]
            percentual = (qtd / total_periodo * 100) if total_periodo > 0 else 0
            
            data.append({
                'ano': ano,
                'mes': mes,
                'escolaridade_codigo': cod,
                'escolaridade_descricao': desc,
                'total_movimentacoes': qtd,
                'percentual': round(percentual, 2)
            })
        
        return data
    
    def processar_anual(self):
        """Processa distribuição anual"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao',
            'grau_instrucao__codigo',
            'grau_instrucao__descricao'
        ).annotate(total=Count('id'))
        
        registros_por_ano = {}
        
        for mov in movimentacoes:
            ano, _ = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano:
                codigo = mov['grau_instrucao__codigo']
                descricao = mov['grau_instrucao__descricao']
                
                chave = (ano, codigo, descricao)
                if chave not in registros_por_ano:
                    registros_por_ano[chave] = 0
                registros_por_ano[chave] += mov['total']
        
        # Calcula totais
        anos = {}
        for (ano, cod, desc), qtd in registros_por_ano.items():
            if ano not in anos:
                anos[ano] = 0
            anos[ano] += qtd
        
        # Formata resultado
        data = []
        for (ano, cod, desc), qtd in registros_por_ano.items():
            total_ano = anos[ano]
            percentual = (qtd / total_ano * 100) if total_ano > 0 else 0
            
            data.append({
                'ano': ano,
                'escolaridade_codigo': cod,
                'escolaridade_descricao': desc,
                'total_movimentacoes': qtd,
                'percentual': round(percentual, 2)
            })
        
        return data