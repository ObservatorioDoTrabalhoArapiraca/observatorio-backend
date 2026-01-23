# PYTHONPATH=. python utils/excluir_txt_por_ano.py --ano 2020

import os
import argparse

parser = argparse.ArgumentParser(description="Excluir arquivos TXT por ano.")
parser.add_argument('--ano', required=True, help='Ano a ser processado (ex: 2020)')
args = parser.parse_args()

base_dir = f'/home/usuario/Github/NOVO CAGED/{args.ano}/'

removidos = 0
for root, dirs, files in os.walk(base_dir):
    for arquivo in files:
        if arquivo.endswith('.txt'):
            caminho_txt = os.path.join(root, arquivo)
            try:
                os.remove(caminho_txt)
                print(f"Removido: {caminho_txt}")
                removidos += 1
            except Exception as e:
                print(f"Erro ao remover {caminho_txt}: {e}")

print(f"Total de arquivos TXT removidos: {removidos}")