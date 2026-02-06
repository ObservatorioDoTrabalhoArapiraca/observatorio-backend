from django.db import models
# Banco
# Create your models here.

# class Movimentacao(models.Model):
#     ano = models.IntegerField(null=True, blank=True)
#     competencia_mov = models.CharField(max_length=255, null=True, blank=True)
#     municipio = models.CharField(max_length=255, null=True, blank=True)
#     secao = models.CharField(max_length=255, null=True, blank=True)
#     subclasse = models.CharField(max_length=255, null=True, blank=True)
#     saldo_movimentacao = models.BigIntegerField(null=True, blank=True)
#     cbo_2002_ocupacao = models.CharField(max_length=255, null=True, blank=True)
#     categoria = models.CharField(max_length=255, null=True, blank=True)
#     grau_de_instrucao = models.CharField(max_length=255, null=True, blank=True)
#     idade = models.FloatField(null=True, blank=True)
#     horas_contratuais = models.FloatField(null=True, blank=True)
#     raca_cor = models.CharField(max_length=255, null=True, blank=True)
#     sexo = models.CharField(max_length=255, null=True, blank=True)
#     tipo_empregador = models.CharField(max_length=255, null=True, blank=True)
#     tipo_estabelecimento = models.CharField(max_length=255, null=True, blank=True)
#     tipo_movimentacao = models.CharField(max_length=255, null=True, blank=True)
#     tipo_de_deficiencia = models.CharField(max_length=255, null=True, blank=True)
#     ind_trab_intermitente = models.CharField(max_length=255, null=True, blank=True)
#     ind_trab_parcial = models.CharField(max_length=255, null=True, blank=True)
#     salario = models.FloatField(null=True, blank=True)
#     tam_estab_jan = models.CharField(max_length=255, null=True, blank=True)
#     indicador_aprendiz = models.CharField(max_length=255, null=True, blank=True)
#     origem_da_informacao = models.CharField(max_length=255, null=True, blank=True)
#     indicador_de_fora_do_prazo = models.CharField(max_length=255, null=True, blank=True)
#     unidade_salario_codigo = models.BigIntegerField(null=True, blank=True)
#     faixa_etaria = models.CharField(max_length=255, null=True, blank=True)
#     faixa_hora_contrat = models.CharField(max_length=255, null=True, blank=True)

#     def __str__(self):
#         return f"{self.competencia_mov} - {self.municipio}"



class CagedEst(models.Model):
    """
    Modelo para dados de estabelecimentos do CAGED
    """
    # Identificação do estabelecimento
    cnpj = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    razao_social = models.CharField(max_length=500, null=True, blank=True)
    nome_fantasia = models.CharField(max_length=500, null=True, blank=True)
    
    # Localização
    municipio = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    uf = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=10, null=True, blank=True)
    logradouro = models.CharField(max_length=500, null=True, blank=True)
    bairro = models.CharField(max_length=255, null=True, blank=True)
    numero = models.CharField(max_length=50, null=True, blank=True)
    complemento = models.CharField(max_length=255, null=True, blank=True)
    
    # Classificação econômica
    cnae_2_0_classe = models.CharField(max_length=10, null=True, blank=True)
    cnae_2_0_subclasse = models.CharField(max_length=10, null=True, blank=True)
    secao = models.CharField(max_length=255, null=True, blank=True)
    
    # Dados do estabelecimento
    porte = models.CharField(max_length=100, null=True, blank=True)
    natureza_juridica = models.CharField(max_length=255, null=True, blank=True)
    tipo_estabelecimento = models.CharField(max_length=100, null=True, blank=True)
    
    # Dados de movimentação
    competencia = models.CharField(max_length=10, null=True, blank=True)
    ano = models.IntegerField(null=True, blank=True, db_index=True)
    admissoes = models.IntegerField(null=True, blank=True, default=0)
    desligamentos = models.IntegerField(null=True, blank=True, default=0)
    saldo = models.IntegerField(null=True, blank=True)
    
    # Timestamps
    data_importacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_cagedest'
        verbose_name = 'CAGED Estabelecimento'
        verbose_name_plural = 'CAGED Estabelecimentos'
        ordering = ['-ano', 'municipio']
        indexes = [
            models.Index(fields=['cnpj', 'ano']),
            models.Index(fields=['municipio', 'ano']),
        ]
    def __str__(self):
        return f"{self.razao_social or self.cnpj} - {self.municipio} ({self.ano})"




# saldomunicio ajustado

class SaldoArapiraca(models.Model):
    """
    Saldo do emprego formal de Arapiraca por período
    """
    periodo = models.CharField(max_length=100, unique=True, db_index=True,
                              help_text='Ex: jan a dez 2018, 2017, série 2002 A 2019')
    ano_referencia = models.IntegerField(db_index=True,
                                        help_text='Ano principal do período')
    
    # Saldos por ano (colunas dinâmicas)
    ano_2002 = models.IntegerField(null=True, blank=True)
    ano_2003 = models.IntegerField(null=True, blank=True)
    ano_2004 = models.IntegerField(null=True, blank=True)
    ano_2005 = models.IntegerField(null=True, blank=True)
    ano_2006 = models.IntegerField(null=True, blank=True)
    ano_2007 = models.IntegerField(null=True, blank=True)
    ano_2008 = models.IntegerField(null=True, blank=True)
    ano_2009 = models.IntegerField(null=True, blank=True)
    ano_2010 = models.IntegerField(null=True, blank=True)
    ano_2011 = models.IntegerField(null=True, blank=True)
    ano_2012 = models.IntegerField(null=True, blank=True)
    ano_2013 = models.IntegerField(null=True, blank=True)
    ano_2014 = models.IntegerField(null=True, blank=True)
    ano_2015 = models.IntegerField(null=True, blank=True)
    ano_2016 = models.IntegerField(null=True, blank=True)
    ano_2017 = models.IntegerField(null=True, blank=True)
    ano_2018 = models.IntegerField(null=True, blank=True)
    ano_2019 = models.IntegerField(null=True, blank=True)
    
    # Metadados
    sheet_origem = models.CharField(max_length=100)
    tipo_periodo = models.CharField(max_length=50, 
                                   help_text='serie_historica, mensal, anual')
    data_importacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'core_saldo_arapiraca'
        verbose_name = 'Saldo de Emprego - Arapiraca'
        verbose_name_plural = 'Saldos de Emprego - Arapiraca'
        ordering = ['-ano_referencia', 'periodo']
    
    def __str__(self):
        return f"Arapiraca - {self.periodo}"