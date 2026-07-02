# python utils/empresas/buscar_bairros_por_cep.py 
import pandas as pd
import re
import unicodedata
import requests
import time
import shutil

# --- FUNÇÕES DE AUXÍLIO ---
caminho_planilha_dicionario = "/mnt/c/Users/Usuário/Documents/Empresas CNPJ/CNPJ_Nao_Ativos_2025.xlsx"
caminho_planilha_analisada = "/mnt/c/Users/Usuário/Documents/Empresas CNPJ/CNPJ_Nao_Ativos_2025.xlsx"
arquivo_de_saida = "/mnt/c/Users/Usuário/Documents/Empresas CNPJ/CNPJ_Nao_Ativos_2025_Atualizado.xlsx"

CACHE_CEP = {}

def normalizar_texto(texto):
    """Remove acentos, caracteres especiais e deixa em caixa alta"""
    if pd.isna(texto) or not isinstance(texto, str):
        return ""
    # Remove acentos
    nfkd_form = unicodedata.normalize('NFKD', texto)
    texto_sem_acento = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    # Deixa em caixa alta e remove caracteres especiais mantendo apenas letras, números e espaços
    texto_limpo = re.sub(r'[^A-Z0-9\s]', '', texto_sem_acento.upper())
    return " ".join(texto_limpo.split()) # limpa espaços extras

def extrair_cep(endereco):
    """Tenta encontrar um padrão de CEP (00000-000 ou 00000000) no endereço"""
    if pd.isna(endereco):
        return None
    match = re.search(r'\b\d{5}-?\d{3}\b', str(endereco))
 
    return match.group(0).replace('-', '')
  

def buscar_bairro_por_cep(cep):
    """Consulta a API gratuita ViaCEP para descobrir o bairro e a cidade"""
    if cep in CACHE_CEP:
        return CACHE_CEP[cep]
    try:
        url = f"https://viacep.com.br/ws/{cep}/json/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            dados = response.json()
            if "erro" not in dados:
                bairro, cidade = dados.get("bairro"), dados.get("localidade")
                CACHE_CEP[cep] = (bairro, cidade)
                return bairro, cidade
            else:
                print(f"   [API INFO] CEP {cep} pesquisado, mas não existe na base dos Correios.")
        else:
            print(f"   [API ERRO] Servidor retornou código: {response.status_code}")
            
    except Exception as e:
        print(f"   [API ERRO] Falha de conexão/rede para o CEP {cep}: {e}")
    CACHE_CEP[cep] = (None, None)    
    return None, None

def carregar_dicionario(caminho_arquivo):
    """Lê a primeira aba do arquivo para estruturar o Dicionário"""
    print(f"Carregando dicionário da primeira aba de: {caminho_arquivo}")
    
    # Abrimos o arquivo Excel especificando o motor 'openpyxl' (evita erros de codec comuns em CSVs)
    # sheet_name=0 garante que estamos pegando a PRIMEIRA aba, não importa o nome dela
    df_dic = pd.read_excel(caminho_arquivo, sheet_name=0, engine='openpyxl')
    
    # Criar mapa de tradução (De: Coluna A -> Para: Coluna B)
    mapa_traducao = {}
    for _, row in df_dic.dropna(subset=[df_dic.columns[0], df_dic.columns[1]]).iterrows():
        de = normalizar_texto(row.iloc[0])
        para = normalizar_texto(row.iloc[1])
        mapa_traducao[de] = para

    # Criar lista de bairros oficiais de Arapiraca (Coluna C)
    bairros_oficiais = set(
        df_dic.iloc[:, 2].dropna().apply(normalizar_texto).unique()
    )
    
    return mapa_traducao, bairros_oficiais

def determinar_bairro_certo(bairro_original, endereco_completo, mapa_traducao, bairros_oficiais):
    """Lógica linear simplificada utilizando early returns (retornos rápidos)"""
    if pd.isna(bairro_original) or str(bairro_original).strip().lower() in ['nan', 'null', '']:
        bairro_norm = ""
    else:
        bairro_norm = normalizar_texto(str(bairro_original))
    
    # REGRA 1: Bairro preenchido e válido
    if bairro_norm and bairro_norm != "NAO IDENTIFICADO":
        bairro_corrigido = mapa_traducao.get(bairro_norm, bairro_norm)
        return bairro_corrigido if bairro_corrigido in bairros_oficiais else "NAO IDENTIFICADO"
        
    # REGRA 2: Vazio ou "NAO IDENTIFICADO" -> Tenta resolver pelo CEP
    # Vamos colocar um print aqui para auditar quando ele decidir buscar pelo CEP
    print(f"   [DEBUG] Bairro original vazio/nulo. Varrendo endereço: '{endereco_completo}'")
    
    cep = extrair_cep(endereco_completo)
    if cep:
        if cep in CACHE_CEP:
            bairro_api, cidade_api = CACHE_CEP[cep]
        else:
            print(f"   [DEBUG] Bairro original vazio. Varrendo endereço: '{endereco_completo}'")
            print(f"   [DEBUG] CEP {cep} inédito. Chamando internet...")
            bairro_api, cidade_api = buscar_bairro_por_cep(cep)
            time.sleep(0.3)  # Delay seguro para requisições inéditas
        
        if bairro_api:
            bairro_api_norm = normalizar_texto(bairro_api)
            cidade_api_norm = normalizar_texto(cidade_api)
            
            if "ARAPIRACA" not in cidade_api_norm:
                return "NAO IDENTIFICADO"
            return bairro_api_norm if bairro_api_norm in bairros_oficiais else "NAO IDENTIFICADO"
        
        return ""  # Se a API falhou (e agora está em cache), mantém em branco para o humano
        
    # REGRA 3: Sem CEP válido no endereço e sem Bairro Original válido
    print("   [DEBUG] Resultado: NAO IDENTIFICADO (Sem CEP no endereço e sem bairro na planilha)")
    return "NAO IDENTIFICADO"

# --- PROCESSAR AS ABAS DE DADOS ---

def processar_planilha_completa(path_dic, path_analise, path_saida, abas_para_analisar):
    """Carrega o dicionário da aba 1 e analisa as demais abas indicadas"""
    
    # 1. Obtém o dicionário da primeira aba do arquivo
    mapa_traducao, bairros_oficiais = carregar_dicionario(path_dic)
    
    print(f"Criando arquivo de saída em: {path_saida}")
    shutil.copyfile(path_analise, path_saida)
    
    abas_processadas = {}
    
    # 2. Loop para processar cada aba de dados fornecida
    for nome_aba in abas_para_analisar:
        print(f"\nAnalisando Aba: {nome_aba}...")
        try: 
            
            df = pd.read_excel(path_analise, sheet_name=nome_aba, engine='openpyxl')
        except Exception as e:
            print(f"Aba '{nome_aba}' não encontrada no arquivo analisado. Pulando... Erro: {e}")
            continue
        
        bairro_certo_lista = []
        for _, row in df.iterrows():
            bairro_orig = row.get('BAIRRO', '')
            endereco_orig = row.get('ENDEREÇO', row.get('endereco', ''))
            
            resultado = determinar_bairro_certo(bairro_orig, endereco_orig, mapa_traducao, bairros_oficiais)
            bairro_certo_lista.append(resultado)
        
        try:
            df.insert(5, 'Bairro Certo', bairro_certo_lista)
        except Exception:
            # Caso de segurança: se a planilha tiver menos de 5 colunas por algum erro, joga no final
            df['Bairro Certo'] = bairro_certo_lista
            
        abas_processadas[nome_aba] = df
        
        
       # 3. Escrita Única em Disco (Salva tudo de uma vez só)
    print("\nGravando todas as alterações no arquivo final... Aguarde.")
    with pd.ExcelWriter(path_saida, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        for nome_aba, df_processado in abas_processadas.items():
            df_processado.to_excel(writer, sheet_name=nome_aba, index=False)
            
    print(f"\nMissão Concluída com Sucesso! Arquivo gravado em: {path_saida}")
# --- COMO EXECUTAR O CÓDIGO ---

# Digamos que seu arquivo se chama "dados_arapiraca.xlsx"
# O dicionário está na aba 1 (ele lê sozinho), e você quer analisar as abas "Janeiro" e "Fevereiro"

abas_dados = ["Janeiro 2025", "Fevereiro 2025", "Março 2025", "Abril 2025", "Maio 2025", "Junho 2025", "Julho 2025", "Agosto 2025", "Setembro 2025", "Outubro 2025", "Novembro 2025", "Dezembro 2025"] 

processar_planilha_completa(
    caminho_planilha_dicionario, 
    caminho_planilha_analisada, 
    arquivo_de_saida, 
    abas_dados)