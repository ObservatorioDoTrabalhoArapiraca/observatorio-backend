from django.db import models

# Create your models here.
# class MunicipioReferencia(models.Model):
#     codigo = models.IntegerField(primary_key=True)
#     nome = models.CharField(max_length=100)
#     uf = models.CharField(max_length=2)

class ReferenciaBase(models.Model):
    codigo = codigo = models.IntegerField(primary_key=True)
    descricao = models.CharField(max_length=255)
    class Meta: 
        abstract = True

class ReferenciaBaseInterger(models.Model):
    codigo = models.IntegerField(primary_key=True)
    descricao = models.IntegerField()


class CompetenciaMovReferencia(ReferenciaBaseInterger):
    pass

class RegiaoReferencia(ReferenciaBase):
    pass

class UfReferencia(ReferenciaBase):
    pass

class MunicipioReferencia(ReferenciaBase):
    pass

class SecaoReferencia(models.Model):
    codigo = models.CharField(max_length=10, primary_key=True)
    descricao = models.CharField(max_length=255)

class SubclasseReferencia(ReferenciaBase):
    pass

class SaldoMovimentacaoReferencia(ReferenciaBaseInterger):
    pass

class CategoriaReferencia(ReferenciaBase):
    pass

class Cbo2002ocupacaoReferencia(ReferenciaBase):
    pass

class GraudeinstrucaoReferencia(ReferenciaBase):
    pass

class IdadeReferencia(ReferenciaBaseInterger):
    pass

class HorasContratuaisReferencia(ReferenciaBaseInterger):
    pass
    
class RacaCorReferencia(ReferenciaBase):
    pass

class SexoReferencia(ReferenciaBase):
    pass
class TipoEmpregadorReferencia(ReferenciaBase):
    pass

class TipoEstabelecimentoReferencia(ReferenciaBase):
    pass

class TipoMovimentacaoReferencia(ReferenciaBase):
    pass

class TipoDeficienciaReferencia(ReferenciaBase):
    pass

class IndTrabIntermitenteReferencia(ReferenciaBase):
    pass

class IndTrabParcialReferencia(ReferenciaBase):
    pass

class SalarioReferencia(ReferenciaBaseInterger):
    pass

class TamEstabJanReferencia(ReferenciaBase):
    pass
class IndicadorAprendizReferencia(ReferenciaBase):
    pass
class OrigemDaInformacaoReferencia(ReferenciaBase):
    pass

class CompetênciaDecReferencia(ReferenciaBaseInterger):
    pass

class CompetênciaExcReferencia(ReferenciaBaseInterger):
    pass

class IndicadorDeExclusãoReferencia(ReferenciaBase):
    pass
class IndicadorDeForaDoPrazoReferencia(ReferenciaBase):
    pass
class UnidadeSalarioCodigoReferencia(ReferenciaBase):
    pass
class ValorSalarioFixoReferencia(ReferenciaBaseInterger):
    pass
