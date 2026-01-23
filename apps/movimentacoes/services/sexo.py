# Anual (todos os anos)
# curl "http://localhost:8000/api/analises/sexo/"

# Anual filtrado por ano
# curl "http://localhost:8000/api/analises/sexo/?ano=2020"

# Mensal (todos os meses de 2020)
# curl "http://localhost:8000/api/analises/sexo/?ano=2020&agregacao=mensal"

# Mensal específico
# curl "http://localhost:8000/api/analises/sexo/?ano=2020&mes=1&agregacao=mensal"

from django.db.models import Count

from .base import BaseDistribuicaoService, logger


class DistribuicaoSexoService(BaseDistribuicaoService):
    """Serviço para distribuição por sexo"""
    
    SEXO_MAP = {
        1: 'Masculino',
        3: 'Feminino',
        9: 'Não Identificado'
    }
    
    def processar_mensal(self):
        """Processa distribuição mensal"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao', 
            'sexo__codigo'
        ).annotate(total=Count('id'))
        
        logger.info(f"Agregação mensal: {movimentacoes.count()} grupos")
        
        registros_por_periodo = {}
        
        for mov in movimentacoes:
            ano, mes = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano and mes:
                sexo_codigo = mov['sexo__codigo']
                chave = (ano, mes)
                
                if chave not in registros_por_periodo:
                    registros_por_periodo[chave] = {}
                
                if sexo_codigo:
                    registros_por_periodo[chave][sexo_codigo] = mov['total']
        
        # Formata resultado
        data = []
        for (ano, mes), sexos in registros_por_periodo.items():
            total_periodo = sum(sexos.values())
            
            for sexo_cod, qtd in sexos.items():
                percentual = (qtd / total_periodo * 100) if total_periodo > 0 else 0
                
                data.append({
                    'ano': ano,
                    'mes': mes,
                    'sexo': sexo_cod,
                    'sexo_descricao': self.SEXO_MAP.get(sexo_cod, 'Desconhecido'),
                    'total_movimentacoes': qtd,
                    'percentual': round(percentual, 2)
                })
        
        return data
    
    def processar_anual(self):
        """Processa distribuição anual"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao', 
            'sexo__codigo'
        ).annotate(total=Count('id'))
        
        logger.info(f"Agregação anual: {movimentacoes.count()} grupos")
        
        registros_por_ano = {}
        
        for mov in movimentacoes:
            ano, _ = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano:
                sexo_codigo = mov['sexo__codigo']
                
                if ano not in registros_por_ano:
                    registros_por_ano[ano] = {}
                
                if sexo_codigo:
                    if sexo_codigo not in registros_por_ano[ano]:
                        registros_por_ano[ano][sexo_codigo] = 0
                    registros_por_ano[ano][sexo_codigo] += mov['total']
        
        # Formata resultado
        data = []
        for ano, sexos in registros_por_ano.items():
            total_ano = sum(sexos.values())
            
            for sexo_cod, qtd in sexos.items():
                percentual = (qtd / total_ano * 100) if total_ano > 0 else 0
                
                data.append({
                    'ano': ano,
                    'sexo': sexo_cod,
                    'sexo_descricao': self.SEXO_MAP.get(sexo_cod, 'Desconhecido'),
                    'total_movimentacoes': qtd,
                    'percentual': round(percentual, 2)
                })
        
        return data