# PYTHONPATH=. python utils/filtrar_arapiraca_rais.py --ano 2021

import os
import argparse

parser = argparse.ArgumentParser(description="Filtrar todos os arquivos .txt da RAIS por Arapiraca e criar arquivos filtrados.")
parser.add_argument('--ano', required=True, help='Ano a ser processado (ex: 2020)')
args = parser.parse_args()

base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/RAIS/{args.ano}'
coluna = 'Município'
valor = 270030  # Código de Arapiraca como string

for root, dirs, files in os.walk(base_dir):
    for arquivo in files:
        if arquivo.endswith('.txt'):
            print(f"Arquivo alvo encontrado: {arquivo}")
            caminho_txt = os.path.join(root, arquivo)
            arquivo_saida = caminho_txt.replace('.txt', '-Arapiraca_filtrado.txt')
            if os.path.exists(arquivo_saida):
                print(f"Já existe: {arquivo_saida}, ignorando.")
                continue
            try:
                with open(caminho_txt, 'r', encoding='latin1') as f_in, open(arquivo_saida, 'w', encoding='latin1') as f_out:
                    header = f_in.readline()
                    f_out.write(header)
                    municipio_idx = None
                    colunas = header.strip().split(';')
                    for idx, nome in enumerate(colunas):
                        if nome.strip().lower() == coluna.lower():
                            municipio_idx = idx
                            break
                    if municipio_idx is None:
                        print(f"Coluna '{coluna}' não encontrada em {arquivo}")
                        continue
                    linhas_filtradas = 0
                    for linha in f_in:
                        campos = linha.strip().split(';')
                        if len(campos) > municipio_idx and campos[municipio_idx].strip() == valor:
                            f_out.write(linha)
                            linhas_filtradas += 1
                print(f"Arquivo filtrado salvo em: {arquivo_saida} ({linhas_filtradas} linhas)")
            except Exception as e:
                print(f"Erro ao filtrar {caminho_txt}: {e}")