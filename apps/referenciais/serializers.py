from rest_framework import serializers
from .models import (
    CompetenciaMovReferencia, RegiaoReferencia, UfReferencia,
    MunicipioReferencia, SecaoReferencia, SubclasseReferencia,
    SaldoMovimentacaoReferencia, CategoriaReferencia,
    Cbo2002ocupacaoReferencia, GraudeinstrucaoReferencia,
    IdadeReferencia, HorasContratuaisReferencia, RacaCorReferencia,
    SexoReferencia, TipoEmpregadorReferencia, TipoEstabelecimentoReferencia,
    TipoMovimentacaoReferencia, TipoDeficienciaReferencia,
    IndTrabIntermitenteReferencia, IndTrabParcialReferencia,
    SalarioReferencia, TamEstabJanReferencia, IndicadorAprendizReferencia,
    OrigemDaInformacaoReferencia, CompetênciaDecReferencia,
    CompetênciaExcReferencia, IndicadorDeExclusãoReferencia,
    IndicadorDeForaDoPrazoReferencia, UnidadeSalarioCodigoReferencia,
    ValorSalarioFixoReferencia
)

class ReferenciaBaseSerializer(serializers.ModelSerializer):
    """Serializer base para tabelas de referência"""
    class Meta:
        fields = ['codigo', 'descricao']

class CompetenciaMovReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = CompetenciaMovReferencia

class RegiaoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = RegiaoReferencia

class UfReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = UfReferencia

class MunicipioReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = MunicipioReferencia

class SecaoReferenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecaoReferencia
        fields = ['codigo', 'descricao']

class SubclasseReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = SubclasseReferencia

class SaldoMovimentacaoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = SaldoMovimentacaoReferencia

class CategoriaReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = CategoriaReferencia

class Cbo2002ocupacaoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = Cbo2002ocupacaoReferencia

class GraudeinstrucaoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = GraudeinstrucaoReferencia

class IdadeReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = IdadeReferencia

class HorasContratuaisReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = HorasContratuaisReferencia

class RacaCorReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = RacaCorReferencia

class SexoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = SexoReferencia

class TipoEmpregadorReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = TipoEmpregadorReferencia

class TipoEstabelecimentoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = TipoEstabelecimentoReferencia

class TipoMovimentacaoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = TipoMovimentacaoReferencia

class TipoDeficienciaReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = TipoDeficienciaReferencia

class IndTrabIntermitenteReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = IndTrabIntermitenteReferencia

class IndTrabParcialReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = IndTrabParcialReferencia

class SalarioReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = SalarioReferencia

class TamEstabJanReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = TamEstabJanReferencia

class IndicadorAprendizReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = IndicadorAprendizReferencia

class OrigemDaInformacaoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = OrigemDaInformacaoReferencia

class CompetênciaDecReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = CompetênciaDecReferencia

class CompetênciaExcReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = CompetênciaExcReferencia

class IndicadorDeExclusãoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = IndicadorDeExclusãoReferencia

class IndicadorDeForaDoPrazoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = IndicadorDeForaDoPrazoReferencia

class UnidadeSalarioCodigoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = UnidadeSalarioCodigoReferencia

class ValorSalarioFixoReferenciaSerializer(ReferenciaBaseSerializer):
    class Meta(ReferenciaBaseSerializer.Meta):
        model = ValorSalarioFixoReferencia