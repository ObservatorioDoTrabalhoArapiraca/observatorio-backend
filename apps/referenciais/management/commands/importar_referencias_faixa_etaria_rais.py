import numpy as np
import pandas as pd
import csv
import os
from django.core.management.base import BaseCommand
from apps.referenciais import models

class Command(BaseCommand):
    help = 'Importa tabela de referência de Faixaetária para a Rais a partir de abas do Excel'

    def handle(self, *args, **kwargs):
        caminho = 'apps/referenciais/RAIS_vinculos_layout2020.xlsx'
        aba_nome = 'FAIXAS'

        try:
            # Lemos forçando o código como string para não perder o "0" de "01"
            df = pd.read_excel(caminho, sheet_name=aba_nome, dtype={'FAIXA ETÁRIA': str}, nrows=10)  # Limite de 100 linhas para teste
            
            # Padroniza nomes das colunas (remove espaços e põe minúsculo)
            df.columns = [col.strip().lower() for col in df.columns]

            count = 0
            for _, row in df.iterrows():
                codigo_raw = str(row['faixa etária']).strip() if pd.notna(row['faixa etária']) else None
                descricao_raw = str(row['descricao']).strip() if pd.notna(row['descricao']) else ""

                if not codigo_raw or codigo_raw.lower() in ['nan', 'total', 'None']:
                    continue

                # Upsert: Cria ou atualiza
                obj, created = models.FaixaEtariaRaisReferencia.objects.update_or_create(
                    codigo=codigo_raw,
                    defaults={'descricao': descricao_raw}
                )
                count += 1

            self.stdout.write(self.style.SUCCESS(f'Sucesso! {count} faixas etárias da RAIS importadas.'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao importar: {e}'))