from django.db import models


class ReferenciaBase(models.Model):
    codigo = models.IntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    class Meta: 
        abstract = True

class ReferenciaBaseInterger(models.Model):
    codigo = models.IntegerField(primary_key=True)
    descricao = models.IntegerField()
    class Meta: 
        abstract = True

    # desde: int
    # volor: int
    # legislacao: str
    # rejuste: int
    
class SalarioBaseReferencia(models.Model):
    desde = models.IntegerField(primary_key=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    legislacao = models.CharField(max_length=255)
    reajuste = models.DecimalField(max_digits=10, decimal_places=2)


class CompetenciaMovReferencia(ReferenciaBaseInterger): pass
class RegiaoReferencia(ReferenciaBase): pass
class UfReferencia(ReferenciaBase): pass
class MunicipioReferencia(ReferenciaBase): pass

class SecaoReferencia(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    descricao = models.CharField(max_length=255)

class SubclasseReferencia(ReferenciaBase): pass
class CategoriaReferencia(ReferenciaBase): pass
class Cbo2002ocupacaoReferencia(ReferenciaBase): pass
class GraudeinstrucaoReferencia(ReferenciaBase): pass
class RacaCorReferencia(ReferenciaBase): pass
class SexoReferencia(ReferenciaBase): pass
class TipoEmpregadorReferencia(ReferenciaBase): pass
class TipoEstabelecimentoReferencia(ReferenciaBase): pass
class TipoMovimentacaoReferencia(ReferenciaBase): pass
class TipoDeficienciaReferencia(ReferenciaBase): pass
class IndTrabIntermitenteReferencia(ReferenciaBase): pass
class IndTrabParcialReferencia(ReferenciaBase): pass
class TamEstabJanReferencia(ReferenciaBase): pass
class IndicadorAprendizReferencia(ReferenciaBase): pass
class OrigemDaInformacaoReferencia(ReferenciaBase): pass
class CompetênciaDecReferencia(ReferenciaBaseInterger): pass
class CompetênciaExcReferencia(ReferenciaBaseInterger): pass
class IndicadorDeExclusãoReferencia(ReferenciaBase): pass
class IndicadorDeForaDoPrazoReferencia(ReferenciaBase): pass
class UnidadeSalarioCodigoReferencia(ReferenciaBase): pass


class SetorAgregadoReferencia(models.Model):
    secao_inicio = models.CharField(
        max_length=10,
        null=True,
        verbose_name="Seção Início (CNAE/CAGED)",
        help_text="Ex: A, B-E, G, Z"
    )
    secao_fim = models.CharField(
        max_length=10, 
        null=True,
        blank=True,
        verbose_name="Seção Fim (CNAE/CAGED)",
        help_text="Deixe vazio se for apenas uma seção",
    )
    
    divisao_inicio = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="Divisão Início"
    )
    divisao_fim = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="Divisão Fim"
    )
    denominacao = models.CharField(
        max_length=100, 
        verbose_name="Nome do Setor"
    )

    def __str__(self):
        intervalo = f"{self.secao_inicio}-{self.secao_fim}" if self.secao_fim else self.secao_inicio
        return f"{intervalo} - {self.denominacao}"

    class Meta:
        db_table = 'ref_setores_agregados'
        verbose_name = "Setor Agregado"
        ordering = ['secao_inicio']