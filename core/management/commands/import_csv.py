import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.core.management import call_command
from pathlib import Path

class Command(BaseCommand):
    help = 'Import CSV file, convert to Parquet and load into database'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file', 
            type=str, 
            help='Path to the CSV file to import'
        )
        parser.add_argument(
            '--chunksize', 
            type=int, 
            default=10000, 
            help='Chunk size for import'
        )
        parser.add_argument(
            '--separator',
            type=str,
            default=',',
            help='CSV separator/delimiter (default: comma)'
        )
        parser.add_argument(
            '--encoding',
            type=str,
            default='utf-8',
            help='CSV encoding (default: utf-8)'
        )
        parser.add_argument(
            '--keep-parquet',
            action='store_true',
            help='Keep the converted Parquet file after import'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            default='temp_parquet',
            help='Directory to save temporary Parquet file (default: temp_parquet)'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        chunksize = options['chunksize']
        separator = options['separator']
        encoding = options['encoding']
        keep_parquet = options['keep_parquet']
        output_dir = options['output_dir']

        # Verifica se o arquivo CSV existe
        if not os.path.exists(csv_file):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_file}'))
            return

        # Cria diretório de saída se não existir
        os.makedirs(output_dir, exist_ok=True)

        # Define nome do arquivo Parquet
        csv_filename = Path(csv_file).stem
        parquet_file = os.path.join(output_dir, f'{csv_filename}.parquet')

        self.stdout.write(self.style.NOTICE(f'📁 Reading CSV file: {csv_file}'))

        try:
            # Lê o CSV
            df = pd.read_csv(
                csv_file,
                sep=separator,
                encoding=encoding,
                low_memory=False
            )
            
            total_rows = len(df)
            self.stdout.write(self.style.SUCCESS(f'✓ CSV loaded successfully: {total_rows:,} rows'))

            # Exibe informações sobre as colunas
            self.stdout.write(self.style.NOTICE(f'\n📊 Columns found ({len(df.columns)}):'))
            for col in df.columns:
                self.stdout.write(f'  - {col}')

            # Converte para Parquet
            self.stdout.write(self.style.NOTICE(f'\n🔄 Converting to Parquet: {parquet_file}'))
            df.to_parquet(
                parquet_file,
                engine='pyarrow',
                compression='snappy',
                index=False
            )
            
            # Verifica tamanho dos arquivos
            csv_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
            parquet_size = os.path.getsize(parquet_file) / (1024 * 1024)  # MB
            compression_ratio = (1 - parquet_size / csv_size) * 100
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ Parquet created successfully\n'
                f'  CSV size: {csv_size:.2f} MB\n'
                f'  Parquet size: {parquet_size:.2f} MB\n'
                f'  Compression: {compression_ratio:.1f}%'
            ))

            # Importa o Parquet para o banco
            self.stdout.write(self.style.NOTICE(f'\n📥 Importing to database...'))
            call_command('import_parquet', parquet_file, chunksize=chunksize)
            
            self.stdout.write(self.style.SUCCESS(f'✓ Data imported successfully!'))

            # Remove arquivo Parquet temporário se não for para manter
            if not keep_parquet:
                os.remove(parquet_file)
                self.stdout.write(self.style.NOTICE(f'🗑️  Temporary Parquet file removed'))
            else:
                self.stdout.write(self.style.SUCCESS(f'💾 Parquet file saved at: {parquet_file}'))

            # Remove diretório vazio
            if not keep_parquet and not os.listdir(output_dir):
                os.rmdir(output_dir)

        except pd.errors.EmptyDataError:
            self.stdout.write(self.style.ERROR('Error: CSV file is empty'))
        except pd.errors.ParserError as e:
            self.stdout.write(self.style.ERROR(f'Error parsing CSV: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during conversion/import: {e}'))
            # Limpa arquivo parquet se houver erro
            if os.path.exists(parquet_file):
                os.remove(parquet_file)

             #   importação básica
             #docker exec -it django_backend python manage.py import_csv dados.csv

              #   importação com separador ponto e vírgula
              # docker exec -it django_backend python manage.py import_csv dados.csv --separator ";"
              
# manter arquivo parquet depois de importar
              # docker exec -it django_backend python manage.py import_csv dados.csv --keep-parquet