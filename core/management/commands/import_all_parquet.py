import os
import glob
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Import all Parquet files from a directory and its subdirectories'

    def add_arguments(self, parser):
        parser.add_argument(
            'directory', 
            type=str, 
            help='Directory containing Parquet files'
        )
        parser.add_argument(
            '--chunksize', 
            type=int, 
            default=10000, 
            help='Chunk size for import'
        )
        parser.add_argument(
            '--recursive',
            action='store_true',
            help='Search subdirectories recursively'
        )

    def handle(self, *args, **options):
        directory = options['directory']
        chunksize = options['chunksize']
        recursive = options['recursive']

        # Padrão de busca
        if recursive:
            pattern = os.path.join(directory, '**', '*.parquet')
            files = glob.glob(pattern, recursive=True)
        else:
            pattern = os.path.join(directory, '*.parquet')
            files = glob.glob(pattern)

        if not files:
            self.stdout.write(self.style.WARNING(f'No Parquet files found in {directory}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Found {len(files)} Parquet file(s)'))
        
        for i, file_path in enumerate(files, 1):
            self.stdout.write(self.style.NOTICE(f'\n[{i}/{len(files)}] Importing: {file_path}'))
            
            try:
                call_command('import_parquet', file_path, chunksize=chunksize)
                self.stdout.write(self.style.SUCCESS(f'✓ Successfully imported {file_path}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error importing {file_path}: {e}'))
                continue

        self.stdout.write(self.style.SUCCESS(f'\n🎉 Finished! Processed {len(files)} files'))


        # Importar apenas da pasta dados
# docker exec -it django_backend python manage.py import_all_parquet dados

# Importar recursivamente (dados + dados/por_ano)
# docker exec -it django_backend python manage.py import_all_parquet dados --recursive

# Com chunk size customizado
# docker exec -it django_backend python manage.py import_all_parquet dados --recursive --chunksize 5000