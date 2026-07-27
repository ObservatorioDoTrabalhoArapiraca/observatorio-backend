#  PYTHONPATH=. python utils/obsoletos/ver_parquet.py

import pandas as pd

# arquivo_parquet = "/home/usuario/Github/NOVO CAGED/2020/202001/CAGEDMOV202001/CAGEDMOV202001.parquet"
# arquivo_parquet = "/home/usuario/Github/NOVO CAGED/2020/202001/CAGEDMOV202001/CAGEDMOV202001-Al-Arapiraca_filtrado.parquet"
arquivo_parquet = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/RAIS/RAIS_VINC_PUB_NORDESTE.COMT'


df = pd.read_parquet(arquivo_parquet)

print("Colunas:", df.columns)
print("\nPrimeiras linhas:")
print(df.head())
print("\nAlgumas linhas aleatórias:")
print(df.sample(5))


print(df[["município", "competênciamov"]].head())