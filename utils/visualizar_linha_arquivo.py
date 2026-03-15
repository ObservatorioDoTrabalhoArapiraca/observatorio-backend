# PYTHONPATH=. python utils/visualizar_linha_arquivo.py --arquivo /home/charlie/Documentos/NOVO\ CAGED/2023/202309/CAGEDMOV202309-Al-Arapiraca_filtrado --id_linha 2562


import argparse
import os
import sys

def visualizar_linha(arquivo, id_linha):
    if not os.path.isfile(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    total_linhas = len(linhas) - 1  # ignora header
    if total_linhas < 1:
        print("❌ Arquivo não possui linhas de dados.")
        return
    if id_linha < 1 or id_linha > total_linhas:
        print(f"❌ ID de linha fora do intervalo. O arquivo tem {total_linhas} linhas de dados.")
        return
    header = linhas[0].strip().split(';')
    campos = linhas[id_linha].strip().split(';')
    print(f"\nLinha {id_linha}:")
    for nome, valor in zip(header, campos):
        print(f"  {nome}: {valor}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visualizar uma linha específica de um arquivo TXT de movimentação")
    parser.add_argument('--arquivo', required=True, type=str, help="Caminho completo do arquivo .txt")
    parser.add_argument('--id_linha', required=True, type=int, help="ID sequencial da linha (igual ao do script de importação)")
    args = parser.parse_args()

    visualizar_linha(args.arquivo, args.id_linha)