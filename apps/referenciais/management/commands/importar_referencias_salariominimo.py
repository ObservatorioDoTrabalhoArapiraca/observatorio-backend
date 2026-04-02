import pandas as pd
import os  # Adicionado para manipulação de caminhos
from django.core.management.base import BaseCommand
from apps.referenciais import models
from decimal import Decimal

class Command(BaseCommand):
    help = 'Importa tabela de referência de alario minimo a partir de abas do Excel'

    def handle(self, *args, **kwargs):
        # Dica: Verifique se o caminho começa da raiz do projeto
        caminho = 'apps/referenciais/Layout Não-identificado Novo Caged Movimentação.xlsx'
        aba_nome = 'salariominimo'
        
        try:
            # Lendo o Excel
            df = pd.read_excel(caminho, sheet_name=aba_nome)
            
            self.stdout.write(self.style.WARNING(f"⏳ Processando {len(df)} registros de salário mínimo..."))
            
            cont_criado = 0
            cont_atualizado = 0

            # CORREÇÃO DE IDENTAÇÃO AQUI:
            for _, row in df.iterrows():
                # Conversão e limpeza dos dados
                desde_val = int(row['desde'])
                valor_val = Decimal(str(row['valor']))
                legislacao_val = str(row['legislacao'])
                
                # Tratamento para reajuste caso venha vazio (NaN)
                reajuste_raw = row['reajuste']
                reajuste_val = Decimal(str(reajuste_raw)) if pd.notna(reajuste_raw) else Decimal('0.00')

                # Uso do models.SalarioBaseReferencia (conforme seu import)
                obj, created = models.SalarioBaseReferencia.objects.update_or_create(
                    desde=desde_val,
                    defaults={
                        'valor': valor_val,
                        'legislacao': legislacao_val,
                        'reajuste': reajuste_val
                    }
                )

                if created:
                    cont_criado += 1
                else:
                    cont_atualizado += 1

            self.stdout.write(self.style.SUCCESS(
                f"✅ Importação finalizada: {cont_criado} novos, {cont_atualizado} atualizados."
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro ao importar: {str(e)}"))