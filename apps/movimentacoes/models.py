from django.db import models
from apps.referenciais.models import (
    CategoriaReferencia,
    IndTrabIntermitenteReferencia,
    IndTrabParcialReferencia,
    IndicadorAprendizReferencia,
    IndicadorDeForaDoPrazoReferencia,
    MunicipioReferencia, 
    Cbo2002ocupacaoReferencia, GraudeinstrucaoReferencia,
    OrigemDaInformacaoReferencia,
     RacaCorReferencia,
    RegiaoReferencia,
    SecaoReferencia,
    SexoReferencia,
    SubclasseReferencia,
    TamEstabJanReferencia, TipoDeficienciaReferencia,
    TipoEmpregadorReferencia,
    TipoEstabelecimentoReferencia,
    TipoMovimentacaoReferencia,
    UfReferencia,
    UnidadeSalarioCodigoReferencia,
    IndicadorDeExclusãoReferencia,
)

  

class Movimentacao(models.Model):
    """
    Modelo para armazenar as movimentações do CAGED (CAGEDMOV)
    """
    # Relações com tabelas de referência
    competencia_mov = models.IntegerField(null=True, blank=True)
    competencia_dec = models.IntegerField(null=True, blank=True)
    competencia_exc = models.IntegerField(null=True, blank=True)
    
    # --- Localização (FKs) ---
    regiao = models.ForeignKey(RegiaoReferencia, on_delete=models.PROTECT, null=True, blank=True)
    uf = models.ForeignKey(UfReferencia, on_delete=models.PROTECT, null=True, blank=True)
    municipio = models.ForeignKey(
        MunicipioReferencia,
        on_delete=models.PROTECT,
        # related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='municipio_id'
    )
    
    # --- Atividade Econômica ---
    secao = models.ForeignKey(SecaoReferencia, on_delete=models.PROTECT, null=True, blank=True)
    subclasse = models.ForeignKey(SubclasseReferencia, on_delete=models.PROTECT, null=True, blank=True)
    
   # --- Perfil do Trabalhador (FKs) ---
    cbo2002_ocupacao = models.ForeignKey(
        Cbo2002ocupacaoReferencia,
        on_delete=models.PROTECT,
        # related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='cbo2002_ocupacao_id'
    )
    
    grau_instrucao = models.ForeignKey(
        GraudeinstrucaoReferencia,
        on_delete=models.PROTECT,
        # related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='grau_instrucao_id'
    )
    idade = models.IntegerField(null=True, blank=True, db_column='idade')

    raca_cor = models.ForeignKey(
        RacaCorReferencia,
        on_delete=models.PROTECT,
        # related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='raca_cor_id'
    )
    sexo = models.ForeignKey(
        SexoReferencia,
        on_delete=models.PROTECT,
        # related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='sexo_id'
    )
  
    tipo_deficiencia = models.ForeignKey(
        TipoDeficienciaReferencia,
        on_delete=models.PROTECT,
        # related_name='movimentacoes',
        null=True,
        blank=True,
        db_column='tipo_deficiencia_id'
    )
    categoria = models.ForeignKey(CategoriaReferencia, on_delete=models.PROTECT, null=True, blank=True)
    valor_salario_fixo = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    horas_contratuais = models.IntegerField(null=True, blank=True)
    # --- Detalhes do Contrato (FKs) ---
    tipo_empregador = models.ForeignKey(TipoEmpregadorReferencia, on_delete=models.PROTECT, null=True, blank=True)
    tipo_estabelecimento = models.ForeignKey(TipoEstabelecimentoReferencia, on_delete=models.PROTECT, null=True, blank=True)
    tipo_movimentacao = models.ForeignKey(TipoMovimentacaoReferencia, on_delete=models.PROTECT, null=True, blank=True)
    ind_trab_intermitente = models.ForeignKey(IndTrabIntermitenteReferencia, on_delete=models.PROTECT, null=True, blank=True)
    ind_trab_parcial = models.ForeignKey(IndTrabParcialReferencia, on_delete=models.PROTECT, null=True, blank=True)
    tam_estab_jan = models.ForeignKey(TamEstabJanReferencia, on_delete=models.PROTECT, null=True, blank=True)
    indicador_aprendiz = models.ForeignKey(IndicadorAprendizReferencia, on_delete=models.PROTECT, null=True, blank=True)
    origem_informacao = models.ForeignKey(OrigemDaInformacaoReferencia, on_delete=models.PROTECT, null=True, blank=True)
    indicador_exclusao = models.ForeignKey(IndicadorDeExclusãoReferencia, on_delete=models.PROTECT, null=True, blank=True)
    indicador_fora_prazo = models.ForeignKey(IndicadorDeForaDoPrazoReferencia, on_delete=models.PROTECT, null=True, blank=True)
    unidade_salario_codigo = models.ForeignKey(UnidadeSalarioCodigoReferencia, on_delete=models.PROTECT, null=True, blank=True)
    
    
    # Campos numéricos
    saldo_movimentacao = models.IntegerField(
        null=True,
        blank=True,
        help_text="Saldo da movimentação: 1 (admissão) ou -1 (desligamento)"
    )
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True, db_column='salario')
    
    # Metadata
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'movimentacoes'
        verbose_name = 'Movimentação'
        verbose_name_plural = 'Movimentações'
        indexes = [
            models.Index(fields=['competencia_mov', 'municipio']),
            models.Index(fields=['subclasse'], name='idx_subclasse'),
            models.Index(fields=['cbo2002_ocupacao']),
            models.Index(fields=['saldo_movimentacao']),
        ]
    
    def __str__(self):
        return f"Movimentação {self.competencia_mov} - {self.municipio} - {self.competencia_mov}"