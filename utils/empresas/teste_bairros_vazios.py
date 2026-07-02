# python utils/empresas/teste_bairros_vazios.py
import pandas as pd
import re
import unicodedata
import requests
import time
import shutil


# DIGITE AQUI A ABA EXATA QUE VOCÊ QUER TESTAR AGORA:
caminho_planilha_dicionario = "/mnt/c/Users/Usuário/Documents/Empresas CNPJ/CNPJ_Nao_Ativos_2025.xlsx"
caminho_planilha_analisada  = "/mnt/c/Users/Usuário/Documents/Empresas CNPJ/CNPJ_Ativos_2025_e_2026.xlsx"
# arquivo_de_saida            = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/CNPJ_Nao_Ativos_2025_Atualizado-{ABA_TESTE}.xlsx"

ABA_TESTE = "Dezembro 2025"

# Cache na memória para evitar requisições repetidas
CACHE_CEP = {}

# --- FUNÇÕES DE AUXÍLIO ---

def normalizar_texto(texto):
    if pd.isna(texto) or not isinstance(texto, str):
        return ""
    nfkd_form = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    texto_limpo = re.sub(r'[^A-Z0-9\s]', '', texto_sem_acento.upper())
    return " ".join(texto_limpo.split())

def extrair_cep(endereco):
    if pd.isna(endereco):
        return None
    match = re.search(r'\b\d{5}-?\d{3}\b', str(endereco))
    return match.group(0).replace('-', '') if match else None

def buscar_bairro_por_cep(cep):
    if cep in CACHE_CEP:
        return CACHE_CEP[cep]
        
    try:
        url = f"https://brasilapi.com.br/api/cep/v1/{cep}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=4)
        
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                bairro, cidade = dados.get("neighborhood"), dados.get("city")
                CACHE_CEP[cep] = (bairro, cidade)
                return bairro, cidade
            else:
                print(f"   [API INFO] CEP {cep} inexistente na base dos Correios.")
        else:
            print(f"   [API ERRO] Servidor retornou código: {response.status_code}")
            
    except Exception as e:
        print(f"   [API ERRO] Falha de conexão/rede para o CEP {cep}: {e}")
    
    CACHE_CEP[cep] = (None, None)
    return None, None

def carregar_dicionario(caminho_arquivo):
    print(f"Carregando dicionário da primeira aba de: {caminho_arquivo}")
    df_dic = pd.read_excel(caminho_arquivo, sheet_name=0, engine='openpyxl')
    bairros_oficiais = set(df_dic.iloc[:, 2].dropna().apply(normalizar_texto).unique())
    return bairros_oficiais

# --- SCRIPT DE EXECUÇÃO FOCADA ---

def rodar_teste_bairros_vazios():
    # 1. Carrega apenas os bairros válidos da coluna C
    bairros_oficiais = carregar_dicionario(caminho_planilha_dicionario)
    
    # 3. Carrega apenas a aba escolhida para o teste
    print(f"\nLendo dados da Aba: {ABA_TESTE}...")
    df = pd.read_excel(caminho_planilha_analisada, sheet_name=ABA_TESTE, engine='openpyxl')
    
    
    contador_invalidos_processados = 0
    
    # 4. Varre a planilha linha por linha
    for idx, row in df.iterrows():
        bairro_orig = row.get('BAIRRO', '')
        endereco_orig = row.get('ENDEREÇO', row.get('endereco', ''))
        
        # Verifica se o bairro original está REALMENTE em branco/nulo
        bairro_limpo = str(bairro_orig).strip().lower()
        bairro_limpo = re.sub(r'[^a-z0-9]', '', bairro_limpo) # Remove traços, barras, aspas, etc.
        
        # Considera INVÁLIDO se: for nulo do pandas, estiver na lista de nulos ou tiver menos de 4 caracteres
        is_invalido = (
            pd.isna(bairro_orig) or 
            bairro_limpo in ['nan', 'null', ''] or 
            len(bairro_limpo) <= 3
        )
        
        if is_invalido:
            contador_invalidos_processados += 1
            cep = extrair_cep(endereco_orig)
            
            if cep:
                # Se já estiver no cache, puxa da memória direto
                if cep in CACHE_CEP:
                    bairro_api, cidade_api = CACHE_CEP[cep]
                else:
                    print(f"   [LINHA {idx}] Bairro vazio. CEP {cep} encontrado. Buscando na API...")
                    bairro_api, cidade_api = buscar_bairro_por_cep(cep)
                    time.sleep(0.4) # Delay para proteger a API pública
                
                if bairro_api:
                    bairro_api_norm = normalizar_texto(bairro_api)
                    cidade_api_norm = normalizar_texto(cidade_api)
                    
                    if "ARAPIRACA" not in cidade_api_norm:
                        df.at[idx, 'BAIRRO'] = "NAO IDENTIFICADO"
                    elif bairro_api_norm in bairros_oficiais:
                        df.at[idx, 'BAIRRO'] = bairro_api_norm
                    else:
                        df.at[idx, 'BAIRRO'] = "NAO IDENTIFICADO"
                else:
                    df.at[idx, 'BAIRRO'] = "" # API falhou ou rede caiu, deixa em branco
                    print(f"   [LINHA {idx}] CEP {cep} não retornou bairro válido. Mantendo em branco para revisão humana.")
            else:
                df.at[idx, 'BAIRRO'] = "NAO IDENTIFICADO" # Sem CEP e sem Bairro
                print(f"   [LINHA {idx}] Sem CEP válido no endereço e sem bairro original. Resultado: NAO IDENTIFICADO.")
        else:
            pass

    print(f"\n[FIM DO PROCESSAMENTO] Total de {contador_invalidos_processados} linhas inválidas analisadas.")

        
    # 6. Grava apenas esta aba modificada no arquivo final
    print(f"Salvando alterações da aba '{ABA_TESTE}' no arquivo de saída...")
    with pd.ExcelWriter(caminho_planilha_analisada, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=ABA_TESTE, index=False)
        
    print("Teste concluído com sucesso!")

# Executar o script de teste
rodar_teste_bairros_vazios()