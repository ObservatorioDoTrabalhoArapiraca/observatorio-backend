# Anual (todos os anos)
# curl "http://localhost:8000/api/analises/pcd/"

# Anual filtrado por 2020
# curl "http://localhost:8000/api/analises/pcd/?ano=2020"

# Mensal de 2020
# curl "http://localhost:8000/api/analises/pcd/?ano=2020&agregacao=mensal"

# Janeiro de 2020
# curl "http://localhost:8000/api/analises/pcd/?ano=2020&mes=1&agregacao=mensal"

from django.db.models import Count
from .base import BaseDistribuicaoService, logger
from .utils import carregar_mapeamento_referencia
from apps.referenciais.models import TipoDeficienciaReferencia


class DistribuicaoPcdService(BaseDistribuicaoService):
    """Serviço para distribuição por tipo de deficiência (PCD)"""
    
    def __init__(self, queryset):
        """Inicializa o serviço e carrega o mapeamento do banco"""
        super().__init__(queryset)
        # ✅ Usa 'codigo' (padrão) porque é o nome do campo no modelo
        self.pcd_map = carregar_mapeamento_referencia(TipoDeficienciaReferencia)
    
    def processar_mensal(self):
        """Processa distribuição mensal"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao',
            'tipo_deficiencia__codigo'  # ✅ COM underscore
        ).annotate(total=Count('id'))
        
        registros_por_periodo = {}
        
        for mov in movimentacoes:
            ano, mes = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano and mes:
                pcd_codigo = mov['tipo_deficiencia__codigo']  # ✅ COM underscore
                chave = (ano, mes)
                
                if chave not in registros_por_periodo:
                    registros_por_periodo[chave] = {}
                
                if pcd_codigo is not None:
                    registros_por_periodo[chave][pcd_codigo] = mov['total']
        
        data = []
        for (ano, mes), tipos in registros_por_periodo.items():
            total_periodo = sum(tipos.values())
            
            for pcd_cod, qtd in tipos.items():
                percentual = (qtd / total_periodo * 100) if total_periodo > 0 else 0
                
                data.append({
                    'ano': ano,
                    'mes': mes,
                    'tipo_deficiencia': pcd_cod,
                    'tipo_deficiencia_descricao': self.pcd_map.get(pcd_cod, 'Desconhecido'),
                    'total_movimentacoes': qtd,
                    'percentual': round(percentual, 2)
                })
        
        return data
    
    def processar_anual(self):
        """Processa distribuição anual"""
        movimentacoes = self.queryset.values(
            'competencia_movimentacao',
            'tipo_deficiencia__codigo'  # ✅ COM underscore
        ).annotate(total=Count('id'))
        
        registros_por_ano = {}
        
        for mov in movimentacoes:
            ano, _ = self.extrair_periodo(mov['competencia_movimentacao'])
            if ano:
                pcd_codigo = mov['tipo_deficiencia__codigo']  # ✅ CORRIGIDO: COM underscore
                
                if ano not in registros_por_ano:
                    registros_por_ano[ano] = {}
                
                if pcd_codigo is not None:
                    if pcd_codigo not in registros_por_ano[ano]:
                        registros_por_ano[ano][pcd_codigo] = 0
                    registros_por_ano[ano][pcd_codigo] += mov['total']
        
        data = []
        for ano, tipos in registros_por_ano.items():
            total_ano = sum(tipos.values())
            
            for pcd_cod, qtd in tipos.items():
                percentual = (qtd / total_ano * 100) if total_ano > 0 else 0
                
                data.append({
                    'ano': ano,
                    'tipo_deficiencia': pcd_cod,
                    'tipo_deficiencia_descricao': self.pcd_map.get(pcd_cod, 'Desconhecido'),
                    'total_movimentacoes': qtd,
                    'percentual': round(percentual, 2)
                })
        
        return data