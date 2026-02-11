from rest_framework import serializers
from .models import Movimentacao

class DistribuicaoSexoSerializer(serializers.Serializer):
    """
    Serializer para dados de distribuição por sexo
    """
    ano = serializers.IntegerField()
    mes = serializers.IntegerField(required=False)
    sexo = serializers.CharField()
    sexo_descricao = serializers.CharField()
    total_movimentacoes = serializers.IntegerField()
    percentual = serializers.DecimalField(max_digits=5, decimal_places=2)
    
class DistribuicaoIdadeSerializer(serializers.Serializer):
    """Serializer para dados de distribuição por faixa etária"""
    ano = serializers.IntegerField()
    mes = serializers.IntegerField(required=False)
    faixa_etaria = serializers.CharField()
    total_movimentacoes = serializers.IntegerField()
    percentual = serializers.DecimalField(max_digits=5, decimal_places=2)
    idade_media = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    


class DistribuicaoEscolaridadeSerializer(serializers.Serializer):
    """Serializer para dados de distribuição por escolaridade"""
    ano = serializers.IntegerField()
    mes = serializers.IntegerField(required=False)
    escolaridade_codigo = serializers.IntegerField()
    escolaridade_descricao = serializers.CharField()
    total_movimentacoes = serializers.IntegerField()
    percentual = serializers.DecimalField(max_digits=5, decimal_places=2)
    
class DistribuicaoRacaCorSerializer(serializers.Serializer):
    """Serializer para distribuição por raça/cor"""
    
    ano = serializers.IntegerField(help_text="Ano da competência")
    mes = serializers.IntegerField(required=False, help_text="Mês da competência (apenas em agregação mensal)")
    raca_cor = serializers.IntegerField(help_text="Código da raça/cor")
    raca_cor_descricao = serializers.CharField(help_text="Descrição da raça/cor")
    total_movimentacoes = serializers.IntegerField(help_text="Total de movimentações")
    percentual = serializers.FloatField(help_text="Percentual do total (%)")

class DistribuicaoPcdSerializer(serializers.Serializer):
    """Serializer para distribuição por tipo de deficiência (PCD)"""
    
    ano = serializers.IntegerField(help_text="Ano da competência")
    mes = serializers.IntegerField(required=False, help_text="Mês da competência (apenas em agregação mensal)")
    tipo_deficiencia = serializers.IntegerField(help_text="Código do tipo de deficiência")
    tipo_deficiencia_descricao = serializers.CharField(help_text="Descrição do tipo de deficiência")
    total_movimentacoes = serializers.IntegerField(help_text="Total de movimentações")
    percentual = serializers.FloatField(help_text="Percentual do total (%)")


class SalarioMedioPorOcupacaoSerializer(serializers.Serializer):
    """Serializer para salário médio por ocupação (CBO)"""
    ano = serializers.IntegerField(help_text="Ano da competência")
    mes = serializers.IntegerField(required=False, help_text="Mês da competência (se mensal)")
    cbo_codigo = serializers.CharField(help_text="Código CBO da ocupação")
    cbo_descricao = serializers.CharField(help_text="Descrição da ocupação")
    salario_medio = serializers.FloatField(help_text="Salário médio (R$)")
    total_movimentacoes = serializers.IntegerField(help_text="Total de movimentações")

class DistribuicaoOcupacaoSerializer(serializers.Serializer):
    """Serializer para distribuição por ocupação (CBO)"""
    ano = serializers.IntegerField(help_text="Ano da competência")
    mes = serializers.IntegerField(required=False, help_text="Mês da competência (se mensal)")
    cbo_codigo = serializers.CharField(help_text="Código CBO da ocupação")
    cbo_descricao = serializers.CharField(help_text="Descrição da ocupação")
    total_movimentacoes = serializers.IntegerField(help_text="Total de movimentações")
    percentual = serializers.FloatField(help_text="Percentual do total (%)")
    
class MovimentacaoSerializer(serializers.ModelSerializer):
    regiao_codigo = serializers.IntegerField(source='regiao.codigo', read_only=True)
    regiao_descricao = serializers.CharField(source='regiao.descricao', read_only=True)
    
    uf_codigo = serializers.IntegerField(source='uf.codigo', read_only=True)
    uf_descricao = serializers.CharField(source='uf.descricao', read_only=True)
    
    municipio_codigo = serializers.IntegerField(source='municipio.codigo', read_only=True)
    municipio_descricao = serializers.CharField(source='municipio.descricao', read_only=True)
    
    secao_codigo = serializers.CharField(source='secao.codigo', read_only=True)
    secao_descricao = serializers.CharField(source='secao.descricao', read_only=True)
    
    subclasse_codigo = serializers.IntegerField(source='subclasse.codigo', read_only=True)
    subclasse_descricao = serializers.CharField(source='subclasse.descricao', read_only=True)
    
    cbo2002_ocupacao_codigo = serializers.IntegerField(source='cbo2002_ocupacao.codigo', read_only=True)
    cbo2002_ocupacao_descricao = serializers.CharField(source='cbo2002_ocupacao.descricao', read_only=True)
    
    categoria_codigo = serializers.IntegerField(source='categoria.codigo', read_only=True)
    categoria_descricao = serializers.CharField(source='categoria.descricao', read_only=True)
    
    grau_instrucao_codigo = serializers.IntegerField(source='grau_instrucao.codigo', read_only=True)
    grau_instrucao_descricao = serializers.CharField(source='grau_instrucao.descricao', read_only=True)
    
    raca_cor_codigo = serializers.IntegerField(source='raca_cor.codigo', read_only=True)
    raca_cor_descricao = serializers.CharField(source='raca_cor.descricao', read_only=True)
    
    sexo_codigo = serializers.IntegerField(source='sexo.codigo', read_only=True)
    sexo_descricao = serializers.CharField(source='sexo.descricao', read_only=True)
    
    tipo_empregador_codigo = serializers.IntegerField(source='tipo_empregador.codigo', read_only=True)
    tipo_empregador_descricao = serializers.CharField(source='tipo_empregador.descricao', read_only=True)
    
    tipo_estabelecimento_codigo = serializers.IntegerField(source='tipo_estabelecimento.codigo', read_only=True)
    tipo_estabelecimento_descricao = serializers.CharField(source='tipo_estabelecimento.descricao', read_only=True)
    
    tipo_movimentacao_codigo = serializers.IntegerField(source='tipo_movimentacao.codigo', read_only=True)
    tipo_movimentacao_descricao = serializers.CharField(source='tipo_movimentacao.descricao', read_only=True)
    
    tipo_deficiencia_codigo = serializers.IntegerField(source='tipo_deficiencia.codigo', read_only=True)
    tipo_deficiencia_descricao = serializers.CharField(source='tipo_deficiencia.descricao', read_only=True)
    
    class Meta:
        model = Movimentacao
        fields = [
            'id',
            'competencia_movimentacao',
            
            # Região (código + descrição)
            'regiao_codigo',
            'regiao_descricao',
            
            # UF
            'uf_codigo',
            'uf_descricao',
            
            # Município
            'municipio_codigo',
            'municipio_descricao',
            
            # Seção
            'secao_codigo',
            'secao_descricao',
            
            # Subclasse
            'subclasse_codigo',
            'subclasse_descricao',
            
            # CBO Ocupação
            'cbo2002_ocupacao_codigo',
            'cbo2002_ocupacao_descricao',
            
            # Categoria
            'categoria_codigo',
            'categoria_descricao',
            
            # Grau de Instrução
            'grau_instrucao_codigo',
            'grau_instrucao_descricao',
            
            # Raça/Cor
            'raca_cor_codigo',
            'raca_cor_descricao',
            
            # Sexo
            'sexo_codigo',
            'sexo_descricao',
            
            # Tipo Empregador
            'tipo_empregador_codigo',
            'tipo_empregador_descricao',
            
            # Tipo Estabelecimento
            'tipo_estabelecimento_codigo',
            'tipo_estabelecimento_descricao',
            
            # Tipo Movimentação
            'tipo_movimentacao_codigo',
            'tipo_movimentacao_descricao',
            
            # Tipo Deficiência
            'tipo_deficiencia_codigo',
            'tipo_deficiencia_descricao',
            
            # Campos numéricos
            'saldo_movimentacao',
            'idade',
            'horas_contratuais',
            'salario',
            'tamanho_estabelecimento',
            
            # Indicadores
            'indicador_trabalho_intermitente',
            'indicador_trabalho_parcial',
            'indicador_aprendiz',
            'origem_informacao',
            
            # Metadata
            'criado_em',
            'atualizado_em',
        ]
