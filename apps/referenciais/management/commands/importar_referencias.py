import pandas as pd
import csv
from django.core.management.base import BaseCommand
from apps.referenciais import models
# Adicione outros modelos conforme necessário

class Command(BaseCommand):
    help = 'Importa dados das tabelas de referência a partir de abas do Excel'

    def handle(self, *args, **kwargs):
        # Exemplo para RegiaoReferencia
        caminho = 'apps/referenciais/Layout Não-identificado Novo Caged Movimentação.xlsx'

        # print(pd.ExcelFile(caminho).sheet_names)


        aba_para_modelo = {
            'região': models.RegiaoReferencia,
            'uf': models.UfReferencia,
            'município': models.MunicipioReferencia,
            'seção': models.SecaoReferencia,
            'subclasse': models.SubclasseReferencia,
            'categoria': models.CategoriaReferencia,
            'cbo2002ocupação': models.Cbo2002ocupacaoReferencia,
            'graudeinstrução': models.GraudeinstrucaoReferencia,
            'raçacor': models.RacaCorReferencia,
            'sexo': models.SexoReferencia,
            'tipoempregador': models.TipoEmpregadorReferencia,
            'tipoestabelecimento': models.TipoEstabelecimentoReferencia,
            'tipomovimentação': models.TipoMovimentacaoReferencia,
            'tipodedeficiência': models.TipoDeficienciaReferencia,
            'indtrabintermitente': models.IndTrabIntermitenteReferencia,
            'indtrabparcial': models.IndTrabParcialReferencia,
            'tamestabjan': models.TamEstabJanReferencia,
            'indicadoraprendiz': models.IndicadorAprendizReferencia,
            'origemdainformação': models.OrigemDaInformacaoReferencia,
            'indicadordeexclusão': models.IndicadorDeExclusãoReferencia,
            'indicadordeforadoprazo': models.IndicadorDeForaDoPrazoReferencia,
            'unidadesaláriocódigo': models.UnidadeSalarioCodigoReferencia,


# Não precisam de referência pois o valor já é o cnúmero exato
            # 'saldo movimentação': models.SaldoMovimentacaoReferencia,
            # 'idade': models.IdadeReferencia,
            # 'horas contratuais': models.HorasContratuaisReferencia,
            # 'salário': models.SalarioReferencia,
            # 'competência dec': models.CompetênciaDecReferencia,
            # 'competência exc': models.CompetênciaExcReferencia,
            # 'valor salário fixo': models.ValorSalarioFixoReferencia,
            # 'competência mov': models.CompetenciaMovReferencia,
        }

        abas = pd.read_excel(caminho, sheet_name=None)

        abas_importadas = list(abas.keys())[1:]  # Ignora a primeira aba

        for aba in abas_importadas:
            modelo = aba_para_modelo.get(aba.strip().lower())
            if not modelo:
                self.stdout.write(self.style.WARNING(f'Aba "{aba}" não mapeada para nenhum modelo. Ignorando.'))
                continue

            df = abas[aba]
            df.columns = [col.strip().lower() for col in df.columns]
            if "código" not in df.columns or "descrição" not in df.columns:
                self.stdout.write(self.style.WARNING(f'Aba "{aba}" não contém as colunas esperadas "Código" e "Descrição". Ignorando.'))
                continue

            count = 0

            for _, row in df.iterrows():
              if pd.isna(row['código']):
                  continue  # Ignora linhas com código ou descrição nulos
                
              if aba.strip().lower() == "município":
                # modelo.objects.all().delete()
                if not str(row['código']).startswith("27"):
                  continue
              modelo.objects.update_or_create(
                    codigo=row['código'],
                    defaults={'descricao': row['descrição']}
                )
              count += 1


            self.stdout.write(self.style.SUCCESS(f'Aba "{aba}": {count} registros importados.'))

        self.stdout.write(self.style.SUCCESS(' importações concluídas com sucesso.'))
        