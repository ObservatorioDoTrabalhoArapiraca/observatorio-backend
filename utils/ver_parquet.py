import pandas as pd

# arquivo_parquet = "/home/usuario/Github/NOVO CAGED/2020/202001/CAGEDMOV202001/CAGEDMOV202001.parquet"
arquivo_parquet = "/home/usuario/Github/NOVO CAGED/2020/202001/CAGEDMOV202001/CAGEDMOV202001-Al-Arapiraca_filtrado.parquet"
df = pd.read_parquet(arquivo_parquet)

print("Colunas:", df.columns)
print("\nPrimeiras linhas:")
print(df.head())
print("\nAlgumas linhas aleatórias:")
print(df.sample(5))


print(df[["município", "competênciamov"]].head())