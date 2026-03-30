#  PYTHONPATH=. python utils/obsoletos/ver_arquivo_comt_ou_txt.py
import sys
import pandas as pd

# arquivo_parquet = "/home/usuario/Github/NOVO CAGED/2020/202001/CAGEDMOV202001/CAGEDMOV202001.parquet"
# arquivo_parquet = "/home/usuario/Github/NOVO CAGED/2020/202001/CAGEDMOV202001/CAGEDMOV202001-Al-Arapiraca_filtrado.parquet"
arquivo = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/RAIS/2021/RAIS_VINC_PUB_NORDESTE.txt'

# linha_desejada = 2091906

if len(sys.argv) > 1:
    linha_alvo = int(sys.argv[1])
else:
    linha_alvo = 2091905
    
print(f"Buscando a linha {linha_alvo}...")

with open(arquivo, "r", encoding="latin1") as f:
    header = f.readline().strip().split(";")
    # print("Header do arquivo:")
    
    linha_encontrada =  None
    # 2. Pula as linhas até chegar na desejada
    # Usamos o enumerate para contar a partir da primeira linha de DADOS
    linha_encontrada = None
    for i, linha_texto in enumerate(f, 1):
        if i == linha_alvo:
            linha_encontrada = linha_texto.strip().split(";")
            break
    
    # 3. Exibe o resultado associando Coluna -> Valor
    if linha_encontrada:
        print(f"\n{'COLUNA':<30} | {'VALOR'}")
        print("-" * 60)
        
        # O zip faz a mágica que você pediu: associa o header à linha_encontrada
        for col, val in zip(header, linha_encontrada):
            # .strip() em ambos para evitar espaços em branco irritantes do TXT
            print(f"{col.strip():<30} | {val.strip()}")
            
        # Dica visual: Se for Arapiraca, avisa no console
        # (270030 costuma ser o código de Arapiraca na RAIS/CAGED)
        if "270030" in linha_encontrada:
            print("\n[!] Esta linha pertence ao município de Arapiraca.")
            
    else:
        print(f"\nErro: O arquivo terminou antes de chegar na linha {linha_alvo}.")

# print("Colunas:", df.columns)
# print("\nPrimeiras linhas:")
# print(df.head())
# print(df)
# print("\nAlgumas linhas aleatórias:")
# print(df["Município"])


# print(df[["município", "competênciamov"]].head())
