import pandas as pd
from django.core.management.base import BaseCommand
from apps.referenciais import models

class Command(BaseCommand):
    help = 'Importa tabela de referência de Grau de Instrução para a Rais'

    def handle(self, *args, **kwargs):
        caminho = 'apps/referenciais/RAIS_vinculos_layout2020.xlsx'
        aba_nome = 'escolaridade ou g instruçao'

        try:
            # 1. Lemos a planilha. nrows=11 (1 cabeçalho + 10 dados)
            # Usamos dtype=str para evitar que o pandas converta códigos para float (ex: 1.0)
            df = pd.read_excel(caminho, sheet_name=aba_nome, dtype=str)

            count = 0
            for _, row in df.iterrows():
                # Baseado na sua descrição:
                # Primeira coluna (índice 0) -> Descrição ("grau de instruçao")
                # Segunda coluna (índice 1)  -> Código ("escolaridade após 2005")
                
                descricao_raw = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
                codigo_raw = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else None

                # Tratamento para o valor -1 ou vazios conforme sua regra
                if not codigo_raw or codigo_raw in ['nan', 'None', 'total']:
                    continue

                # 2. No banco de dados: GrauDeInstrucaoRaisReferencia
                # Ajuste o nome do modelo se for diferente no seu models.py
                obj, created = models.GrauDeInstrucaoRaisReferencia.objects.update_or_create(
                    codigo=codigo_raw,
                    defaults={'descricao': descricao_raw}
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} graus de instrução da RAIS importados.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar: {e}'))