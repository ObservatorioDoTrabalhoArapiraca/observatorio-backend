import pandas as pd
from django.core.management.base import BaseCommand
from core.models import SaldoArapiraca
import re

class Command(BaseCommand):
    help = 'Import Arapiraca employment data from all sheets in XLS file'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str, help='Path to XLS file')
        parser.add_argument('--clear', action='store_true', help='Clear existing data')

    def handle(self, *args, **options):
        file_path = options['file']
        clear_data = options['clear']

        if clear_data:
            count = SaldoArapiraca.objects.count()
            SaldoArapiraca.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'🗑️  Deleted {count} existing records'))

        self.stdout.write(self.style.NOTICE(f'📁 Reading: {file_path}'))

        try:
            # Lista todas as sheets
            xls = pd.ExcelFile(file_path)
            self.stdout.write(self.style.SUCCESS(f'📊 Found {len(xls.sheet_names)} sheets'))

            records = []
            found_sheets = 0
            not_found_sheets = []

            for sheet_name in xls.sheet_names:
                self.stdout.write(f'\n🔍 Processing: "{sheet_name}"')
                
                try:
                    # Lê a sheet
                    df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)
                    
                    # Pega o nome da primeira coluna
                    col_municipio = df.columns[0]
                    
                    # Procura por Arapiraca (variações: Al-Arapiraca, AL-Arapiraca, etc)
                    arapiraca_row = None
                    for idx, row in df.iterrows():
                        municipio = str(row[col_municipio]).strip()
                        if 'arapiraca' in municipio.lower():
                            arapiraca_row = row
                            self.stdout.write(self.style.SUCCESS(f'  ✓ Found: {municipio}'))
                            break
                    
                    if arapiraca_row is None:
                        self.stdout.write(self.style.WARNING(f'  ⚠ Arapiraca not found'))
                        not_found_sheets.append(sheet_name)
                        continue
                    
                    found_sheets += 1
                    
                    # Extrai ano de referência do nome da sheet
                    ano_ref = self.extract_year(sheet_name)
                    tipo_periodo = self.classify_period(sheet_name)
                    
                    # Cria dicionário com os valores
                    data_dict = {
                        'periodo': sheet_name,
                        'ano_referencia': ano_ref,
                        'sheet_origem': sheet_name,
                        'tipo_periodo': tipo_periodo
                    }
                    
                    # Mapeia as colunas numéricas para anos
                    anos_esperados = list(range(2002, 2020))
                    col_idx = 1  # Começa da segunda coluna (primeira é município)
                    
                    for ano in anos_esperados:
                        if col_idx < len(arapiraca_row):
                            valor = arapiraca_row.iloc[col_idx]
                            try:
                                if pd.notna(valor):
                                    data_dict[f'ano_{ano}'] = int(float(valor))
                                else:
                                    data_dict[f'ano_{ano}'] = None
                            except (ValueError, TypeError):
                                data_dict[f'ano_{ano}'] = None
                            col_idx += 1
                        else:
                            data_dict[f'ano_{ano}'] = None
                    
                    records.append(SaldoArapiraca(**data_dict))
                    self.stdout.write(f'  ✓ Extracted data for {ano_ref}')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  ✗ Error: {e}'))
                    continue
            
            # Salva todos os registros
            if records:
                SaldoArapiraca.objects.bulk_create(records, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(
                    f'\n🎉 Import completed!\n'
                    f'  Sheets processed: {len(xls.sheet_names)}\n'
                    f'  Arapiraca found in: {found_sheets} sheets\n'
                    f'  Records created: {len(records)}'
                ))
                
                if not_found_sheets:
                    self.stdout.write(self.style.NOTICE(
                        f'\n⚠ Arapiraca not found in {len(not_found_sheets)} sheets:'
                    ))
                    for sheet in not_found_sheets[:5]:
                        self.stdout.write(f'  - {sheet}')
                    if len(not_found_sheets) > 5:
                        self.stdout.write(f'  ... and {len(not_found_sheets) - 5} more')
            else:
                self.stdout.write(self.style.ERROR('❌ No data found for Arapiraca'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

    def extract_year(self, sheet_name):
        """Extrai o ano principal do nome da sheet"""
        # Procura por ano de 4 dígitos
        match = re.search(r'\b(20\d{2})\b', sheet_name)
        if match:
            return int(match.group(1))
        
        # Se não encontrar, tenta extrair de ranges (ex: "2002 A 2019")
        match = re.search(r'\b(20\d{2})\s*[Aa]\s*(20\d{2})\b', sheet_name)
        if match:
            return int(match.group(2))  # Retorna o último ano do range
        
        return 2019  # Default

    def classify_period(self, sheet_name):
        """Classifica o tipo de período"""
        sheet_lower = sheet_name.lower()
        
        if 'série' in sheet_lower or 'serie' in sheet_lower:
            return 'serie_historica'
        elif 'jan a dez' in sheet_lower or 'janeiro a dezembro' in sheet_lower:
            return 'ano_completo'
        elif any(mes in sheet_lower for mes in ['jan', 'fev', 'mar', 'abr', 'mai', 
                                                  'jun', 'jul', 'ago', 'set', 'out', 
                                                  'nov', 'dez']):
            return 'parcial'
        else:
            return 'anual'