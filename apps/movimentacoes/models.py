from django.db import models
from apps.referenciais.models import (
    CompetenciaMovReferencia, RegiaoReferencia, SecaoReferencia, UfReferencia,
    MunicipioReferencia, SubclasseReferencia, CategoriaReferencia,
    Cbo2002ocupacaoReferencia, GraudeinstrucaoReferencia,
     RacaCorReferencia,
    SexoReferencia, TipoEmpregadorReferencia, TipoEstabelecimentoReferencia,
    TipoMovimentacaoReferencia, TipoDeficienciaReferencia,
)


class Movimentacao(models.Model):
    """
    Modelo para armazenar as movimentações do CAGED (CAGEDMOV)
    """
    # Relações com tabelas de referência
    competencia_movimentacao = models.IntegerField(null=True, blank=True, db_column='competencia_mov')
    regiao = models.ForeignKey(
        RegiaoReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='regiao_id'
    )
    uf = models.ForeignKey(
        UfReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='uf_id'
    )
    municipio = models.ForeignKey(
        MunicipioReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='municipio_id'
    )
    secao = models.ForeignKey(
        SecaoReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='secao_id'
    )
    subclasse = models.ForeignKey(
        SubclasseReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='subclasse_id'
    )
    saldo_movimentacao = models.IntegerField(null=True, blank=True, db_column='saldo_movimentacao')
    cbo2002_ocupacao = models.ForeignKey(
        Cbo2002ocupacaoReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='cbo2002_ocupacao_id'
    )
    categoria = models.ForeignKey(
        CategoriaReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='categoria_id'
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
    horas_contratuais = models.IntegerField(null=True, blank=True, db_column='horas_contratuais')
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
    tipo_empregador = models.ForeignKey(
        TipoEmpregadorReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='tipo_empregador_id'
    )
    tipo_estabelecimento = models.ForeignKey(
        TipoEstabelecimentoReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='tipo_estabelecimento_id'
    )
    tipo_movimentacao = models.ForeignKey(
        TipoMovimentacaoReferencia,
        on_delete=models.PROTECT,
        related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='tipo_movimentacao_id'
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
   
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='salario')
    tamanho_estabelecimento = models.IntegerField(null=True, blank=True, db_column='tamanho_estabelecimento')
    
    # Indicadores (texto/código)
    indicador_trabalho_intermitente = models.CharField(max_length=200, null=True, blank=True, db_column='indicador_trabalho_intermitente')
    indicador_trabalho_parcial = models.CharField(max_length=200, null=True, blank=True, db_column='indicador_trabalho_parcial')
    indicador_aprendiz = models.CharField(max_length=200, null=True, blank=True, db_column='indicador_aprendiz')
    origem_informacao = models.CharField(max_length=200, null=True, blank=True, db_column='origem_informacao')
    
    # Metadata
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'movimentacoes'
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        indexes = [
            models.Index(fields=['competencia_movimentacao', 'municipio']),
            models.Index(fields=['subclasse'], name='idx_subclasse'),
            models.Index(fields=['cbo2002_ocupacao']),
        ]
    
    def __str__(self):
        return f"Movimentação {self.competencia_movimentacao} - {self.municipio} - {self.competencia_movimentacao}"