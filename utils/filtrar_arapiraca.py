# PYTHONPATH=. python utils/filtrar_arapiraca.py --ano 2020 --type MOV --mes 01

  # 3263


import os
import argparse

parser = argparse.ArgumentParser(description="Filtrar dados de Arapiraca por ano e tipo.")
parser.add_argument('--ano', required=True, help='Ano a ser processado (ex: 2026)')
parser.add_argument('--mes', required=True, help='Mês a ser processado (ex: 01)')
parser.add_argument('--type', required=False, help='Tipo de arquivo (MOV, FOR, EXC)')
args = parser.parse_args()

base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{args.ano}/{args.ano}{args.mes}'
coluna = 'município'
valor = 270030 # Al-Arapiraca

# Filtra todos os arquivos Parquet do ano
for root, dirs, files in os.walk(base_dir):
    for arquivo in files:
        print(f"Verificando arquivo: {arquivo}") 
        if (args.type and arquivo.startswith(f'CAGED{args.type}{args.ano}{args.mes}') and arquivo.endswith('.txt')) or (not args.type and arquivo.endswith('.txt')):
            print(f"Arquivo alvo encontrado: {arquivo}")  
            
            caminho_txt = os.path.join(root, arquivo)
            arquivo_saida = caminho_txt.replace('.txt', '-Al-Arapiraca_filtrado.txt')
            if os.path.exists(arquivo_saida):
                print(f"Já existe: {arquivo_saida}, ignorando.")
                continue
            try:
                with open(caminho_txt, 'r', encoding='utf-8') as f_in, open(arquivo_saida, 'w', encoding='utf-8') as f_out:
                    header = f_in.readline()
                    f_out.write(header)
                    municipio_idx = None
                    colunas = header.strip().split(';')
                    for idx, nome in enumerate(colunas):
                        if nome.lower() == 'município':
                            municipio_idx = idx
                            break
                    if municipio_idx is None:
                        print(f"Coluna 'município' não encontrada em {arquivo}")
                        continue
                    linhas_filtradas = 0
                    for linha in f_in:
                        campos = linha.strip().split(';')
                        if len(campos) > municipio_idx and campos[municipio_idx] == (str(valor)):
                            f_out.write(linha)
                            linhas_filtradas += 1
                print(f"Arquivo filtrado salvo em: {arquivo_saida} ({linhas_filtradas} linhas)")
            except Exception as e:
                print(f"Erro ao filtrar {caminho_txt}: {e}")
                