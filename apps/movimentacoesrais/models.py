from django.db import models

class MovimentacaoRais(models.Model):
    bairros_sp = models.CharField(max_length=50, null=True, blank=True)
    bairros_fortaleza = models.CharField(max_length=50, null=True, blank=True)
    bairros_rj = models.CharField(max_length=50, null=True, blank=True)
    distritos_sp = models.CharField(max_length=50, null=True, blank=True)
    regioes_adm_df = models.IntegerField(null=True)
    mun_trab = models.CharField(max_length=10, db_index=True, null=True, blank=True)
    municipio = models.CharField(max_length=10, db_index=True, null=True, blank=True)
    
    # --- IDENTIFICAÇÃO DE ATIVIDADE (CBO / CNAE) ---
    cbo_ocupacao_2002 = models.CharField(max_length=15, null=True, blank=True, db_index=True)
    cnae_2_0_classe = models.CharField(max_length=15, null=True)
    cnae_95_classe = models.CharField(max_length=15, null=True)
    cnae_2_0_subclasse = models.CharField(max_length=15, null=True)
    ibge_subsetor = models.IntegerField(null=True)
    natureza_juridica = models.CharField(max_length=10, null=True)

    # --- CARACTERÍSTICAS DO TRABALHADOR ---
    idade = models.IntegerField(null=True)
    faixa_etaria = models.IntegerField(null=True)
    sexo_trabalhador = models.IntegerField(null=True)
    raca_cor = models.IntegerField(null=True)
    escolaridade_apos_2005 = models.IntegerField(null=True)
    nacionalidade = models.IntegerField(null=True)
    ind_portador_defic = models.IntegerField(null=True)
    tipo_defic = models.IntegerField(null=True)
    ano_chegada_brasil = models.IntegerField(null=True)

    # --- VÍNCULO E CONTRATO ---
    vinculo_ativo_31_12 = models.IntegerField(null=True)
    faixa_hora_contrat = models.IntegerField(null=True)
    qtd_hora_contr = models.IntegerField(null=True)
    faixa_tempo_emprego = models.IntegerField(null=True)
    tempo_emprego = models.DecimalField(max_digits=10, decimal_places=1, null=True)
    tipo_admissao = models.IntegerField(null=True)
    tipo_estab = models.IntegerField(null=True)
    tipo_estab_1 = models.CharField(max_length=20, null=True)
    tipo_vinculo = models.IntegerField(null=True)
    tamanho_estabelecimento = models.IntegerField(null=True)
    ind_cei_vinculado = models.IntegerField(null=True)
    ind_simples = models.IntegerField(null=True)
    ind_trab_intermitente = models.IntegerField(null=True)
    ind_trab_parcial = models.IntegerField(null=True)

    # --- MOVIMENTAÇÃO (ADMISSÃO E DESLIGAMENTO) ---
    causa_afastamento_1 = models.IntegerField(null=True)
    causa_afastamento_2 = models.IntegerField(null=True)
    causa_afastamento_3 = models.IntegerField(null=True)
    motivo_desligamento = models.IntegerField(null=True)
    mes_admissao = models.IntegerField(null=True)
    mes_desligamento = models.CharField(max_length=10, null=True) # Mantido como string devido ao '{ñ'
    qtd_dias_afastamento = models.IntegerField(null=True)

    # --- REMUNERAÇÕES (ANUAIS E MÉDIAS) ---
    vl_remun_dezembro_nom = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_remun_dezembro_sm = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_remun_media_nom = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_remun_media_sm = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    faixa_remun_dezem_sm = models.IntegerField(null=True)
    faixa_remun_media_sm = models.IntegerField(null=True)

    # --- REMUNERAÇÕES MENSAIS ---
    vl_rem_janeiro_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_fevereiro_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_marco_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_abril_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_maio_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_junho_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_julho_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_agosto_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_setembro_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_outubro_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    vl_rem_novembro_sc = models.DecimalField(max_digits=15, decimal_places=2, null=True)

    ano_base = models.IntegerField(db_index=True)

    class Meta:
        db_table = 'movimentacoes_rais'

    def __str__(self):
        return f"RAIS {self.ano_base} - Mun: {self.mun_trab}"