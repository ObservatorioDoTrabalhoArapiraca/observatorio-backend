# PYTHONPATH=. python utils/empresas/pegar_porte_empresa.py

import os
import glob

TIPO_ARQUIVO_EMPRESA = "NAO_ATIVAS"  # Ou "NAO_ATIVAS"
MES = "12"
ANO = 2025

# ==========================================
# CAMINHOS BASE
# ==========================================
# Tabela 1: O seu arquivo unificado, ordenado e com município corrigido
CAMINHO_TABELA_1 = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/{ANO}{MES}/estabelecimentos/Estabelecimentos_Arapiraca_{TIPO_ARQUIVO_EMPRESA}.csv"

# Pasta mãe onde ficam as subpastas empresas0, empresas1, empresas2...
PASTA_PAI_EMPRESAS = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/{ANO}{MES}/empresas/"

# Arquivo de Saída final consolidado
CAMINHO_SAIDA = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/{ANO}{MES}/estabelecimentos/Estabelecimentos_Arapiraca_{TIPO_ARQUIVO_EMPRESA}_FINAL_COMPLETO.csv"
# ==========================================

INDICE_FIXO_RAZAO = 9 
INDICE_FIXO_PORTE = 10
TAMANHO_MINIMO_LINHA = INDICE_FIXO_PORTE + 1
INDICE_MUNICIPIO_TABELA1 = 5 

LEGENDA_PORTE = {
    "00": "NÃO INFORMADO",
    "01": "MICRO EMPRESA",
    "03": "EMPRESA DE PEQUENO PORTE",
    "05": "DEMAIS"
}

INDICE_CHAVE = 0             # 1ª coluna da Tabela 2 (CNPJ Básico)
INDICE_COLUNA2_TABELA2 = 1   # 2ª coluna da Tabela 2 (Razão Social)
INDICE_COLUNA6_TABELA2 = 5   # 6ª coluna da Tabela 2 (Porte)

print("Iniciando o processo de junção MULTI-TABELAS de baixo consumo...")

# Busca automaticamente todos os arquivos .csv dentro de subpastas como empresas0, empresas1, etc.
# O 'case_sensitive=False' garante que ele ache tanto 'empresas0' quanto 'Empresas0'
arquivos_empresas = glob.glob(os.path.join(PASTA_PAI_EMPRESAS, "**", "*.CSV"), recursive=True)

if not arquivos_empresas:
    print(f"Erro: Nenhum arquivo de Empresas encontrado em {PASTA_PAI_EMPRESAS}")
    exit(1)

# Ordena a lista de arquivos para ele processar na ordem: empresas0, empresas1, empresas2...
arquivos_empresas.sort()

print(f"Foram encontrados {len(arquivos_empresas)} arquivos gigantes de Empresas para varrer.")

try:
    # -------------------------------------------------------------------------
    # PASSO 1: Carregar a Tabela 1 uma única vez na memória
    # -------------------------------------------------------------------------
    print("\nPasso 1: Carregando dados da Tabela 1 de Arapiraca na memória...")
    dados_tabela1 = {}
    ordem_linhas = [] 

    with open(CAMINHO_TABELA_1, 'r', encoding='utf-8') as f_tab1:
        cabecalho = f_tab1.readline()
        
        for linha in f_tab1:
            campos = linha.strip('\n').split(';')
            
            while len(campos) < TAMANHO_MINIMO_LINHA:
                campos.append("")
            
            campos[INDICE_MUNICIPIO_TABELA1] = "Arapiraca"
                
            cnpj_14_digitos = campos[0].strip()
            cnpj_basico_chave = cnpj_14_digitos[:8]
            
            dados_tabela1[cnpj_basico_chave] = campos
            ordem_linhas.append(cnpj_basico_chave)

    print(f"-> {len(dados_tabela1)} registros carregados na memória.")

    # -------------------------------------------------------------------------
    # PASSO 2: Iterar sobre cada arquivo gigante de Empresas sequencialmente
    # -------------------------------------------------------------------------
    total_linhas_atualizadas_geral = 0
    alertas_duplicados_geral = 0

    for idx, caminho_empresa in enumerate(arquivos_empresas, start=1):
        nome_arquivo_resumido = os.path.basename(caminho_empresa)
        nome_pasta_pai = os.path.basename(os.path.dirname(caminho_empresa))
        
        print(f"\n[{idx}/{len(arquivos_empresas)}] Varrendo: {nome_pasta_pai}/{nome_arquivo_resumido}")
        
        linhas_tabela2_processadas = 0
        
        with open(caminho_empresa, 'r', encoding='iso-8859-1') as f_tab2:
            for linha in f_tab2:
                linhas_tabela2_processadas += 1
                
                # Feedback corrigido para evitar erros no terminal
                if linhas_tabela2_processadas % 5000000 == 0:
                    print(f"   ... {nome_arquivo_resumido}: já analisou {linhas_tabela2_processadas} linhas...")

                campos_tab2 = linha.strip('\n').split(';')
                if len(campos_tab2) > 0:
                    cnpj_basico_busca = campos_tab2[INDICE_CHAVE].replace('"', '').strip().zfill(8)
                    
                    if cnpj_basico_busca in dados_tabela1:
                        if len(campos_tab2) > INDICE_COLUNA6_TABELA2:
                            
                            razao_social = campos_tab2[INDICE_COLUNA2_TABELA2].replace('"', '').strip()
                            codigo_porte = campos_tab2[INDICE_COLUNA6_TABELA2].replace('"', '').strip().zfill(2)
                            descricao_porte = LEGENDA_PORTE.get(codigo_porte, codigo_porte)
                            
                            campos_originais = dados_tabela1[cnpj_basico_busca]
                            
                            ja_tem_razao = campos_originais[INDICE_FIXO_RAZAO].strip() != ""
                            ja_tem_porte = campos_originais[INDICE_FIXO_PORTE].strip() != ""
                            
                            if ja_tem_razao or ja_tem_porte:
                                alertas_duplicados_geral += 1
                                print(f"\n[ALERTA DUPLICADO] CNPJ Básico: {cnpj_basico_busca}")
                                print(f"  -> Atual na memória: Razão: '{campos_originais[INDICE_FIXO_RAZAO]}' | Porte: '{campos_originais[INDICE_FIXO_PORTE]}'")
                                print(f"  -> Novo achado ({nome_arquivo_resumido}): Razão: '{razao_social}' | Porte: '{descricao_porte}'")
                            
                            campos_originais[INDICE_FIXO_RAZAO] = razao_social
                            campos_originais[INDICE_FIXO_PORTE] = descricao_porte
                            total_linhas_atualizadas_geral += 1

        print(f"-> Concluído {nome_arquivo_resumido}. Total de linhas lidas: {linhas_tabela2_processadas}")

    # -------------------------------------------------------------------------
    # PASSO 3: Gravar os dados finais consolidados
    # -------------------------------------------------------------------------
    print("\nPasso 3: Escrevendo o arquivo final consolidado...")
    with open(CAMINHO_SAIDA, 'w', encoding='utf-8') as f_out:
        f_out.write(cabecalho)
        for chave in ordem_linhas:
            campos_finais = dados_tabela1[chave]
            f_out.write(';'.join(campos_finais) + '\n')

    print(f"\n==========================================")
    print(f"PROCESSO COMPLETO CONCLUÍDO COM SUCESSO!")
    print(f"Total de atualizações realizadas: {total_linhas_atualizadas_geral}")
    print(f"Total de alertas de duplicados em todas as rodadas: {alertas_duplicados_geral}")
    print(f"Arquivo mestre final salvo em: {CAMINHO_SAIDA}")
    print(f"==========================================")

except Exception as e:
    print(f"Ocorreu um erro durante o processamento: {e}")