# PYTHONPATH=. python utils/filtrar_arapiraca.py --ano 2020

import os
import argparse
from filterToColumn import filtrar_parquet_por_coluna

parser = argparse.ArgumentParser(description="Filtrar dados de Arapiraca por ano.")
parser.add_argument('--ano', required=True, help='Ano a ser processado (ex: 2020)')
args = parser.parse_args()

base_dir = f'/home/usuario/Github/NOVO CAGED/{args.ano}/'
coluna = 'município'
valor = 270030 # Al-Arapiraca

# Filtra todos os arquivos Parquet do ano
for root, dirs, files in os.walk(base_dir):
    for arquivo in files:
        if arquivo.endswith('.parquet') and not arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
            caminho_parquet = os.path.join(root, arquivo)
            arquivo_saida = caminho_parquet.replace('.parquet', '-Al-Arapiraca_filtrado.parquet')
            if os.path.exists(arquivo_saida):
                print(f"Já existe: {arquivo_saida}, ignorando.")
                continue
            try:
                filtrar_parquet_por_coluna(caminho_parquet, coluna, valor, arquivo_saida)
                print(f"Arquivo filtrado salvo em: {arquivo_saida}")
            except Exception as e:
                print(f"Erro ao filtrar {caminho_parquet}: {e}")