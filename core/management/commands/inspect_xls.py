import pandas as pd
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = 'Inspect XLS/XLSX file structure and content'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Path to XLS/XLSX file')
        parser.add_argument('--rows', type=int, default=10, help='Number of rows to display')

    def handle(self, *args, **options):
        file_path = options['file']
        rows = options['rows']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        try:
            # Tenta ler o arquivo
            self.stdout.write(self.style.NOTICE(f'\n📁 Inspecting: {file_path}\n'))

            # Lista todas as sheets
            xls = pd.ExcelFile(file_path)
            self.stdout.write(self.style.SUCCESS(f'📊 Sheets found: {len(xls.sheet_names)}'))

            for i, sheet_name in enumerate(xls.sheet_names, 1):
                self.stdout.write(f'  {i}. {sheet_name}')

            # Lê a primeira sheet
            self.stdout.write(self.style.NOTICE(f'\n🔍 Reading first sheet: "{xls.sheet_names[0]}"'))
            df = pd.read_excel(file_path, sheet_name=0)

            self.stdout.write(self.style.SUCCESS(
                f'\n📈 Data shape: {df.shape[0]:,} rows × {df.shape[1]} columns'
            ))

            # Mostra as colunas
            self.stdout.write(self.style.NOTICE(f'\n📋 Columns ({len(df.columns)}):'))
            for i, col in enumerate(df.columns, 1):
                dtype = df[col].dtype
                non_null = df[col].count()
                self.stdout.write(f'  {i:2d}. {col:<40} | Type: {dtype} | Non-null: {non_null:,}')

            # Mostra as primeiras linhas
            self.stdout.write(self.style.NOTICE(f'\n📄 First {rows} rows:'))
            self.stdout.write(str(df.head(rows)))

            # Estatísticas básicas para colunas numéricas
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                self.stdout.write(self.style.NOTICE(f'\n📊 Numeric columns summary:'))
                self.stdout.write(str(df[numeric_cols].describe()))

            # Informações de memória
            memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            self.stdout.write(self.style.SUCCESS(f'\n💾 Memory usage: {memory_mb:.2f} MB'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc()
