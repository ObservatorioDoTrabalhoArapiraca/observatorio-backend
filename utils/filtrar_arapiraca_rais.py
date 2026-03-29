import pandas as pd

# Configurações
arquivo_origem = "/home/charlie/Documentos/RAIS/2024/RAIS_VINC_PUB_NORDESTE.COMT"
arquivo_destino = "/home/charlie/Documentos/RAIS/2024/RAIS_VINC_PUB_ARAPIRACA.COMT"
codigo_arapiraca = 270030
tamanho_bloco = 100000  # Processa 100 mil linhas por vez

def filtrar_arapiraca():
    primeiro_bloco = True
    encontrados = 0
    
    print(f"Iniciando filtragem de Arapiraca ({codigo_arapiraca})...")
    
    # Usamos o chunksize para não carregar o arquivo inteiro na RAM
    chunks = pd.read_csv(
        arquivo_origem, 
        # sep=';', 
        sep=',', 
        encoding='latin-1', 
        chunksize=tamanho_bloco, 
        low_memory=False,
        # dtype={'Mun Trab': int}
        dtype={'Município Trab - Código': int}
    )
    
    for i, bloco in enumerate(chunks):
        # Filtra onde Mun Trab OU Município é Arapiraca
        # (Uso ambos para garantir, já que seu log mostrou os dois)
        # filtro = (bloco['Mun Trab'] == codigo_arapiraca)
        filtro = (bloco['Município Trab - Código'] == codigo_arapiraca)
        dados_filtrados = bloco[filtro]
        
        if not dados_filtrados.empty:
            encontrados += len(dados_filtrados)
            # Salva no arquivo de destino
            # 'a' (append) adiciona ao final do arquivo; 'w' (write) cria o arquivo
            modo = 'w' if primeiro_bloco else 'a'
            header = True if primeiro_bloco else False
            
            dados_filtrados.to_csv(
                arquivo_destino, 
                sep=';', 
                index=False, 
                encoding='latin-1', 
                mode=modo, 
                header=header
            )
            primeiro_bloco = False
            
        print(f"Bloco {i+1} processado... Encontrados até agora: {encontrados}", end='\r')

    print(f"\nConcluído! Total de registros de Arapiraca: {encontrados}")
    print(f"Arquivo salvo em: {arquivo_destino}")

if __name__ == "__main__":
    filtrar_arapiraca()