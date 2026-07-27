import argparse
import os
import sys

def encontrar_linha_por_cbo(arquivo, cbo_busca):
    if not os.path.isfile(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        sys.exit(1)
    with open(arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    if len(linhas) < 2:
        print("❌ Arquivo não possui linhas de dados.")
        return
    header = linhas[0].strip().split(';')
    try:
        idx_cbo = [i for i, col in enumerate(header) if 'cbo' in col.lower()][0]
    except IndexError:
        print("❌ Coluna CBO não encontrada no header.")
        return
    encontrou = False
    for i, linha in enumerate(linhas[1:], start=1):
        campos = linha.strip().split(';')
        if len(campos) <= idx_cbo:
            continue
        if campos[idx_cbo] == cbo_busca:
            print(f"Encontrado CBO {cbo_busca} na linha sequencial {i}:")
            for nome, valor in zip(header, campos):
                print(f"  {nome}: {valor}")
            encontrou = True
    if not encontrou:
        print(f"Nenhuma linha encontrada com CBO {cbo_busca}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procurar linha por CBO e mostrar o id sequencial")
    parser.add_argument('--arquivo', required=True, type=str, help="Caminho completo do arquivo .txt")
    parser.add_argument('--cbo', required=True, type=str, help="Código CBO a buscar (ex: 322735)")
    args = parser.parse_args()

    encontrar_linha_por_cbo(args.arquivo, args.cbo)