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
    class Meta:
        model = Movimentacao
        fields = '__all__' 