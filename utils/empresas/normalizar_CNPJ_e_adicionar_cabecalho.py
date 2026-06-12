# PYTHONPATH=. python utils/empresas/normalizar_CNPJ_e_adicionar_cabecalho.py

import os
import glob

MES = "03"
PASTA_ESTABELECIMENTOS = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/2026{MES}/estabelecimentos/"

ARQUIVO_ATIVAS = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/2026{MES}/estabelecimentos/Estabelecimentos_Arapiraca_ATIVAS.csv"
ARQUIVO_NAO_ATIVAS = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/2026{MES}/estabelecimentos/Estabelecimentos_Arapiraca_NAO_ATIVAS.csv"

SITUACAO_CADASTRAL_MAPA = {
    "01": "NULA",
    "02": "ATIVA",
    "03": "SUSPENSA",
    "04": "INAPTA",
    "08": "BAIXADA",
}

print("Iniciando a unificação, ordenação por Bairro e divisão por situação...")

arquivos_alvo = glob.glob(os.path.join(PASTA_ESTABELECIMENTOS, "Estabelecimentos*", "*-Arapiraca_filtrado*.csv"))

if not arquivos_alvo:
    print("Erro: Nenhum arquivo filtrado de Arapiraca foi encontrado.")
    exit(1)

CABECALHO = [
    'CNPJ', 'NOME_FANTASIA', 'SITUAÇÃO CADASTRAL', 'ENDEREÇO', 
    'BAIRRO', 'MUNICÍPIO', 'CNAE PRINCIPAL', 'TELEFONE', 
    'EMAIL', 'RAZAO SOCIAL', 'PORTE DA EMPRESA', 'VISITADA', 'DATA DA VISITA'
]

# Listas temporárias para guardar as linhas processadas antes de ordenar
lista_ativas = []
lista_nao_ativas = []

try:
    for caminho_arquivo in arquivos_alvo:
        print(f" Processando: {os.path.basename(caminho_arquivo)}")
        
        with open(caminho_arquivo, 'r', encoding='utf-8') as f_in:
            for linha in f_in:
                if "CNPJ" in linha or "município" in linha.lower():
                    continue
                    
                campos = linha.strip('\n').split(';')
                if len(campos) < 21:
                    continue
                
                # Extração e Tradução da Situação Cadastral
                codigo_situacao = campos[5].replace('"', '').strip().zfill(2)
                situacao_traduzida = SITUACAO_CADASTRAL_MAPA.get(codigo_situacao, codigo_situacao)
                
                # --- MONTAGEM DA NOVA LINHA PADRONIZADA ---
                nova_linha_dados = []
                
                # [0] CNPJ - Corrigido para string pura conforme você pediu
                cnpj_basico = campos[0].replace('"', '').strip().zfill(8)
                cnpj_ordem = campos[1].replace('"', '').strip().zfill(4)
                cnpj_dv = campos[2].replace('"', '').strip().zfill(2)
                cnpj_completo = f"{cnpj_basico}{cnpj_ordem}{cnpj_dv}"
                nova_linha_dados.append(cnpj_completo)
                
                # [1] NOME_FANTASIA
                nova_linha_dados.append(campos[4].replace('"', '').strip())
                
                # [2] SITUAÇÃO CADASTRAL
                nova_linha_dados.append(situacao_traduzida)
                
                # [3] ENDEREÇO
                tipo_logra = campos[13].replace('"', '').strip()
                logradouro = campos[14].replace('"', '').strip()
                numero = campos[15].replace('"', '').strip()
                complem = campos[16].replace('"', '').strip()
                cep = campos[18].replace('"', '').strip()
                
                partes_endereco = [f"{tipo_logra} {logradouro}".strip(), f"Nº {numero}" if numero else "", complem, f"CEP: {cep}" if cep else ""]
                endereco_completo = ", ".join([p for p in partes_endereco if p])
                nova_linha_dados.append(endereco_completo)
                
                # [4] BAIRRO
                nova_linha_dados.append(campos[17].replace('"', '').strip())
                
                # [5] MUNICÍPIO
                nova_linha_dados.append("Arapiraca")
                
                # [6] CNAE PRINCIPAL
                nova_linha_dados.append(campos[11].replace('"', '').strip())
                
                # [7] TELEFONE
                ddd1 = campos[21].replace('"', '').strip()
                tel1 = campos[22].replace('"', '').strip()
                ddd2 = campos[23].replace('"', '').strip()
                tel2 = campos[24].replace('"', '').strip()
                
                telefones = []
                if ddd1 or tel1: telefones.append(f"({ddd1}) {tel1}".strip())
                if ddd2 or tel2: telefones.append(f"({ddd2}) {tel2}".strip())
                telefone_final = " / ".join(telefones) if telefones else ""
                nova_linha_dados.append(telefone_final)
                
                # [8] EMAIL
                nova_linha_dados.append(campos[27].replace('"', '').strip())
                
                # [9] RAZAO SOCIAL
                nova_linha_dados.append("")
                
                # [10] PORTE DA EMPRESA
                nova_linha_dados.append("")
                
                # [11] VISITADA
                nova_linha_dados.append("Não")
                
                # [12] DATA DA VISITA
                nova_linha_dados.append("")
                
                # Separa nas listas da memória em vez de salvar direto no arquivo
                if situacao_traduzida == "ATIVA":
                    lista_ativas.append(nova_linha_dados)
                else:
                    lista_nao_ativas.append(nova_linha_dados)

    # -------------------------------------------------------------------------
    # PASSO DE ORDENAÇÃO: Ordena alfabeticamente pelo campo Bairro (Índice 4)
    # -------------------------------------------------------------------------
    print("\nOrdenando os dados por ordem alfabética de Bairro...")
    
    # O lambda diz ao Python para olhar para o elemento x[4] (Bairro) para fazer a ordenação
    lista_ativas.sort(key=lambda x: x[4])
    lista_nao_ativas.sort(key=lambda x: x[4])

    # -------------------------------------------------------------------------
    # SALVANDO OS ARQUIVOS FINAIS
    # -------------------------------------------------------------------------
    print("Gravando arquivos ordenados de saída...")
    
    with open(ARQUIVO_ATIVAS, 'w', encoding='utf-8') as f_ativas:
        f_ativas.write(';'.join(CABECALHO) + '\n')
        for linha in lista_ativas:
            f_ativas.write(';'.join(linha) + '\n')
            
    with open(ARQUIVO_NAO_ATIVAS, 'w', encoding='utf-8') as f_nao_ativas:
        f_nao_ativas.write(';'.join(CABECALHO) + '\n')
        for linha in lista_nao_ativas:
            f_nao_ativas.write(';'.join(linha) + '\n')

    print(f"\n==========================================")
    print(f"Processo concluído com sucesso!")
    print(f"Total de empresas ATIVAS ordenadas: {len(lista_ativas)}")
    print(f"Total de empresas NÃO ATIVAS ordenadas: {len(lista_nao_ativas)}")
    print(f"==========================================")

except Exception as e:
    print(f"Ocorreu um erro crítico durante o processamento: {e}")

# COLUNAS = {
#     'CNPJ': 0,
#     'NOME_FANTASIA': 1,
#     'SITUAÇÃO CADASTRAL': 5,
#     'ENDEREÇO': [13, 14, 15, 16, 18],  # tipo logradouro, logradouro, Número, Complemento, cep
#     'BAIRRO': 17,
#     'MUNICÍPIO': 20,
#     'CNAE PRINCIPAL': 11,
#     'TELEFONE': [{tel1: [21, 22], tel2: [23, 24]},],  # DDD + Telefone
#     'EMAIL': 27,
#     'RAZAO SOCIAL': 28,
#     'PORTE DA EMPRESA': 29,
#     'VISITADA': 30,
#     'DATA DA VISITA': 31,
#     }