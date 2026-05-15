import pandas as pd

# 1. Carrega o arquivo TXT
# Se o separador for TAB, use sep='\t'. Se for espaço, use sep=' '
arquivo_txt = "/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/RAIS/RAIS_DOM_PUB_2024/RAIS_DOM_PUB_2024_ARAPIRACA.txt"
arquivo_csv = "/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/RAIS/RAIS_DOM_PUB_2024/RAIS_DOM_PUB_2024_ARAPIRACA.csv"

df = pd.read_csv(
    arquivo_txt,
    sep=';',
    encoding='latin-1',
    low_memory=False
)

df.to_csv(
    arquivo_csv,
    sep=';',
    index=False,
    encoding='latin-1'
)

print("Arquivo convertido com sucesso:", arquivo_csv)