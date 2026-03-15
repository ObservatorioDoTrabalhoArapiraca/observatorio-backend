import argparse
import os
import sys

def conferir_cbo_na_linha(arquivo, id_linha, cbo_esperado):
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
    try:
        idx_cbo = [i for i, col in enumerate(header) if 'cbo' in col.lower()][0]
    except IndexError:
        print("❌ Coluna CBO não encontrada no header.")
        return
    cbo_linha = campos[idx_cbo] if idx_cbo < len(campos) else ""
    print(f"\nLinha {id_linha}:")
    for nome, valor in zip(header, campos):
        print(f"  {nome}: {valor}")
    if cbo_linha == cbo_esperado:
        print(f"\n✅ CBO {cbo_esperado} encontrado na linha {id_linha}.")
    else:
        print(f"\n❌ CBO nesta linha é '{cbo_linha}', não '{cbo_esperado}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conferir se a linha N tem o CBO desejado")
    parser.add_argument('--arquivo', required=True, type=str, help="Caminho completo do arquivo .txt")
    parser.add_argument('--id_linha', required=True, type=int, help="ID sequencial da linha (igual ao do script de importação)")
    parser.add_argument('--cbo', required=True, type=str, help="Código CBO esperado (ex: 322735)")
    args = parser.parse_args()

    conferir_cbo_na_linha(args.arquivo, args.id_linha, args.cbo)