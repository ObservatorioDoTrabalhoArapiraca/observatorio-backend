import pandas as pd
from django.core.management.base import BaseCommand
from core.models import Movimentacao
import numpy as np

class Command(BaseCommand):
    help = 'Import data from a Parquet file into the Movimentacao model'

    def add_arguments(self, parser):
        parser.add_argument('parquet_file', type=str, help='The path to the Parquet file to import.')
        parser.add_argument('--chunksize', type=int, default=10000, help='The number of rows to process in each chunk.')

    def handle(self, *args, **options):
        file_path = options['parquet_file']
        chunksize = options['chunksize']
        
        try:
            parquet_file = pd.read_parquet(file_path, engine='pyarrow')
            self.stdout.write(self.style.SUCCESS(f'Successfully opened Parquet file from {file_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error opening Parquet file: {e}'))
            return

        total_rows = len(parquet_file)
        start_row = 0
        total_imported = 0
# refatorar usando uma função que mapeia as colunas e tranforma em snake_case e lower case
        column_mapping = {
            'competênciamov': 'competencia_mov', 'município': 'municipio', 'seção': 'secao',
            'subclasse': 'subclasse', 'saldomovimentação': 'saldo_movimentacao', 'cbo2002ocupação': 'cbo_2002_ocupacao',
            'categoria': 'categoria', 'graudeinstrução': 'grau_de_instrucao', 'idade': 'idade',
            'horascontratuais': 'horas_contratuais', 'raçacor': 'raca_cor', 'sexo': 'sexo',
            'tipoempregador': 'tipo_empregador', 'tipoestabelecimento': 'tipo_estabelecimento',
            'tipomovimentação': 'tipo_movimentacao', 'tipodedeficiência': 'tipo_de_deficiencia',
            'indtrabintermitente': 'ind_trab_intermitente', 'indtrabparcial': 'ind_trab_parcial',
            'salário': 'salario', 'tamestabjan': 'tam_estab_jan', 'indicadoraprendiz': 'indicador_aprendiz',
            'origemdainformação': 'origem_da_informacao', 'indicadordeforadoprazo': 'indicador_de_fora_do_prazo',
            'unidadesaláriocódigo': 'unidade_salario_codigo', 'Faixa Etária': 'faixa_etaria',
            'Faixa Hora Contrat': 'faixa_hora_contrat',
        }

        while start_row < total_rows:
            self.stdout.write(f"Processing chunk starting at row {start_row}...")
            end_row = min(start_row + chunksize, total_rows)
            chunk = parquet_file[start_row:end_row]
            
            chunk = chunk.rename(columns=column_mapping)
            chunk = chunk.replace({np.nan: None})

            movimentacoes = [
                Movimentacao(**row)
                for _, row in chunk.iterrows()
            ]
            
            try:
                Movimentacao.objects.bulk_create(movimentacoes, batch_size=500)
                total_imported += len(movimentacoes)
                self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(movimentacoes)} records in this chunk.'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing chunk: {e}'))

            start_row += chunksize

        self.stdout.write(self.style.SUCCESS(f'Finished importing. Total records imported: {total_imported}')) 