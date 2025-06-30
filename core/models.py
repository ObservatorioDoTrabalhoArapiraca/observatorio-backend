from django.db import models

# Create your models here.

class Movimentacao(models.Model):
    competencia_mov = models.CharField(max_length=255, null=True, blank=True)
    municipio = models.CharField(max_length=255, null=True, blank=True)
    secao = models.CharField(max_length=255, null=True, blank=True)
    subclasse = models.CharField(max_length=255, null=True, blank=True)
    saldo_movimentacao = models.BigIntegerField(null=True, blank=True)
    cbo_2002_ocupacao = models.CharField(max_length=255, null=True, blank=True)
    categoria = models.CharField(max_length=255, null=True, blank=True)
    grau_de_instrucao = models.CharField(max_length=255, null=True, blank=True)
    idade = models.FloatField(null=True, blank=True)
    horas_contratuais = models.FloatField(null=True, blank=True)
    raca_cor = models.CharField(max_length=255, null=True, blank=True)
    sexo = models.CharField(max_length=255, null=True, blank=True)
    tipo_empregador = models.CharField(max_length=255, null=True, blank=True)
    tipo_estabelecimento = models.CharField(max_length=255, null=True, blank=True)
    tipo_movimentacao = models.CharField(max_length=255, null=True, blank=True)
    tipo_de_deficiencia = models.CharField(max_length=255, null=True, blank=True)
    ind_trab_intermitente = models.CharField(max_length=255, null=True, blank=True)
    ind_trab_parcial = models.CharField(max_length=255, null=True, blank=True)
    salario = models.FloatField(null=True, blank=True)
    tam_estab_jan = models.CharField(max_length=255, null=True, blank=True)
    indicador_aprendiz = models.CharField(max_length=255, null=True, blank=True)
    origem_da_informacao = models.CharField(max_length=255, null=True, blank=True)
    indicador_de_fora_do_prazo = models.CharField(max_length=255, null=True, blank=True)
    unidade_salario_codigo = models.BigIntegerField(null=True, blank=True)
    faixa_etaria = models.CharField(max_length=255, null=True, blank=True)
    faixa_hora_contrat = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.competencia_mov} - {self.municipio}"
