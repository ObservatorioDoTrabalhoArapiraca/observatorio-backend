# python utils/ver_arquivo_rais.py 

import pandas as pd

# Defina o caminho do arquivo aqui
caminho_arquivo = "/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/RAIS/2021/RAIS_VINC_PUB_ARAPIRACA.txt"

def analisar_estrutura_rais(caminho):
    try:
        # Carrega apenas as primeiras 5 linhas para economizar memória
        # A RAIS geralmente usa ';' como separador e encoding 'latin-1' ou 'cp1252'
        df = pd.read_csv(caminho, sep=';', nrows=5, encoding='latin-1', low_memory=False)
        
        print(f"{'Índice':<8} | {'Coluna':<30} | {'Tipo':<12} | {'Exemplos (Primeiras 5 linhas)'}")
        print("-" * 90)
        
        for i, coluna in enumerate(df.columns):
            # Obtém os valores da coluna para as 5 linhas
            valores = df[coluna].tolist()
            tipo = str(df[coluna].dtype)
            
            # Formata a exibição
            print(f"{i:<8} | {coluna[:30]:<30} | {tipo:<12} | {valores}")

    except FileNotFoundError:
        print("Erro: O arquivo não foi encontrado no caminho especificado.")
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    analisar_estrutura_rais(caminho_arquivo)