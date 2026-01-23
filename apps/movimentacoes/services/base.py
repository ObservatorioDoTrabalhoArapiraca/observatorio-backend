from django.db.models import Count
import logging

logger = logging.getLogger(__name__)


class BaseDistribuicaoService:
    """Classe base para serviços de distribuição"""
    
    def __init__(self, queryset):
        self.queryset = queryset
    
    def aplicar_filtro_ano(self, ano):
        """Filtra por ano"""
        if ano:
            try:
                ano_int = int(ano)
                self.queryset = self.queryset.filter(
                    competencia_movimentacao__startswith=str(ano_int)
                )
                logger.info(f"Após filtro ano {ano}: {self.queryset.count()} registros")
            except ValueError:
                raise ValueError('Ano inválido')
        return self
    
    def aplicar_filtro_mes(self, mes):
        """Filtra por mês"""
        if mes:
            try:
                mes_int = int(mes)
                if mes_int < 1 or mes_int > 12:
                    raise ValueError
                mes_str = str(mes_int).zfill(2)
                self.queryset = self.queryset.filter(
                    competencia_movimentacao__endswith=mes_str
                )
                logger.info(f"Após filtro mês {mes}: {self.queryset.count()} registros")
            except ValueError:
                raise ValueError('Mês inválido (1-12)')
        return self
    
    def extrair_periodo(self, competencia):
        """Extrai ano e mês de uma competência (YYYYMM)"""
        if competencia and len(str(competencia)) >= 6:
            ano = int(str(competencia)[:4])
            mes = int(str(competencia)[4:6])
            return ano, mes
        return None, None
    
    def calcular_percentuais(self, registros_por_periodo, periodos_totais):
        """Calcula percentuais baseado nos totais"""
        resultado = []
        for chave, qtd in registros_por_periodo.items():
            periodo_key = chave[:-1] if len(chave) > 2 else chave[:1]
            total_periodo = periodos_totais.get(periodo_key, 0)
            percentual = (qtd / total_periodo * 100) if total_periodo > 0 else 0
            resultado.append((chave, qtd, round(percentual, 2)))
        return resultado