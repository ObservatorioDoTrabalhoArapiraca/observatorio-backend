import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path

class Command(BaseCommand):
    help = 'Import XLS/XLSX file, convert to CSV and load into database'

    def add_arguments(self, parser):
        parser.add_argument('xls_file', type=str, help='Path to XLS/XLSX file')
        parser.add_argument('--sheet', type=str, default=0, help='Sheet name or index')
        parser.add_argument('--keep-csv', action='store_true', help='Keep CSV after import')

    def handle(self, *args, **options):
        xls_file = options['xls_file']
        sheet = options['sheet']
        keep_csv = options['keep_csv']

        if not os.path.exists(xls_file):
            self.stdout.write(self.style.ERROR(f'File not found: {xls_file}'))
            return

        # Criar diretório temp
        os.makedirs('temp_csv', exist_ok=True)
        
        csv_filename = Path(xls_file).stem + '.csv'
        csv_file = os.path.join('temp_csv', csv_filename)

        self.stdout.write(self.style.NOTICE(f'📁 Reading XLS file: {xls_file}'))

        try:
            # Lê XLS/XLSX
            df = pd.read_excel(xls_file, sheet_name=sheet)
            
            self.stdout.write(self.style.SUCCESS(f'✓ XLS loaded: {len(df):,} rows, {len(df.columns)} columns'))

            # Converte para CSV
            self.stdout.write(self.style.NOTICE(f'🔄 Converting to CSV: {csv_file}'))
            df.to_csv(csv_file, index=False, encoding='utf-8')
            
            csv_size = os.path.getsize(csv_file) / (1024 * 1024)
            self.stdout.write(self.style.SUCCESS(f'✓ CSV created: {csv_size:.2f} MB'))

            # Importa usando o comando import_csv
            self.stdout.write(self.style.NOTICE(f'📥 Importing to database...'))
            call_command('import_csv', csv_file)

            # Remove CSV se não for para manter
            if not keep_csv:
                os.remove(csv_file)
                if not os.listdir('temp_csv'):
                    os.rmdir('temp_csv')
                self.stdout.write(self.style.NOTICE(f'🗑️  Temporary CSV removed'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            if os.path.exists(csv_file):
                os.remove(csv_file)