from django.db import models
from apps.referenciais.models import (
    MunicipioReferencia, 
    Cbo2002ocupacaoReferencia, GraudeinstrucaoReferencia,
     RacaCorReferencia,
    SexoReferencia, TipoDeficienciaReferencia,
)


class Movimentacao(models.Model):
    """
    Modelo para armazenar as movimentações do CAGED (CAGEDMOV)
    """
    # Relações com tabelas de referência
    competencia_movimentacao = models.IntegerField(null=True, blank=True, db_column='competencia_mov')
  
    municipio = models.ForeignKey(
        MunicipioReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='municipio_id'
    )
 
   
    cbo2002_ocupacao = models.ForeignKey(
        Cbo2002ocupacaoReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='cbo2002_ocupacao_id'
    )
    
    grau_instrucao = models.ForeignKey(
        GraudeinstrucaoReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='grau_instrucao_id'
    )
    idade = models.IntegerField(null=True, blank=True, db_column='idade')

    raca_cor = models.ForeignKey(
        RacaCorReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='raca_cor_id'
    )
    sexo = models.ForeignKey(
        SexoReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='sexo_id'
    )
  
    tipo_deficiencia = models.ForeignKey(
        TipoDeficienciaReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='tipo_deficiencia_id'
    )
    # Campos numéricos
    saldo_movimentacao = models.IntegerField(
        null=True,
        blank=True,
        help_text="Saldo da movimentação: 1 (admissão) ou -1 (desligamento)"
    )
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='salario')
    
    # Metadata
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'movimentacoes'
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        indexes = [
            models.Index(fields=['competencia_movimentacao', 'municipio']),
            # models.Index(fields=['subclasse'], name='idx_subclasse'),
            models.Index(fields=['cbo2002_ocupacao']),
            models.Index(fields=['saldo_movimentacao']),
        ]
    
    def __str__(self):
        return f"Movimentação {self.competencia_movimentacao} - {self.municipio} - {self.competencia_movimentacao}"