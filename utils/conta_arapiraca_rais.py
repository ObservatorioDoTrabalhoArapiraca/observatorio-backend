import pandas as pd

# Configurações
arquivo_origem = "/home/charlie/Documentos/RAIS/2024/RAIS_VINC_PUB_NORDESTE.COMT"
codigo_arapiraca_int = 270030
codigo_arapiraca_str = "270030"

def validar_contagem_exata():
    total_encontrado = 0
    linhas_processadas = 0
    
    print(f"Iniciando auditoria rigorosa no arquivo: {arquivo_origem}")
    print("-" * 50)

    # Lemos apenas a coluna 'Mun Trab' para ser ultra rápido e leve
    # Forçamos a leitura como string para evitar problemas de interpretação do pandas
    chunks = pd.read_csv(
        arquivo_origem, 
        # sep=';', 
        sep=',', 
        encoding='latin-1', 
        # usecols=['Mun Trab'], 
        usecols=['Município Trab - Código'], 
        chunksize=200000, 
        # dtype={'Mun Trab': str}
        dtype={'Município Trab - Código': str}
    )

    for i, bloco in enumerate(chunks):
        # Remove espaços em branco que podem vir nos arquivos da RAIS
        # bloco['Mun Trab'] = bloco['Mun Trab'].str.strip()
        bloco['Município Trab - Código'] = bloco['Município Trab - Código'].str.strip()
        
        # Conta ocorrências exatas do código de Arapiraca
        # filtro = bloco['Mun Trab'] == codigo_arapiraca_str
        filtro = bloco['Município Trab - Código'] == codigo_arapiraca_str
        contagem_bloco = filtro.sum()
        
        total_encontrado += contagem_bloco
        linhas_processadas += len(bloco)
        
        print(f"Processando: {linhas_processadas} linhas analisadas...", end='\r')

    print(f"\n\n--- RESULTADO DA AUDITORIA ---")
    print(f"Total de linhas analisadas no arquivo original: {linhas_processadas}")
    print(f"Total REAL de ocorrências de Arapiraca (270030): {total_encontrado}")
    print("-" * 50)
    
    return total_encontrado

if __name__ == "__main__":
    validar_contagem_exata()