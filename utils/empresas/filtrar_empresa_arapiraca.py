# PYTHONPATH=. python utils/empresas/filtrar_empresa_arapiraca.py
  
  # O código de 4 dígitos que você vê na sua planilha é o Código TOM (Tabela de Órgãos e Municípios), utilizado pela Receita Federal, pelo SIAFI e pelo SERPRO --> Cód. Arapiraca: 2705
  
import os

MES = 3
COD_MUNICIPIO = "2705"
NUMERO_ESTABELECIMENTO = 9
CAMINHO_ENTRADA = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/20260{MES}/estabelecimentos/Estabelecimentos{NUMERO_ESTABELECIMENTO}/K3241.K03200Y{NUMERO_ESTABELECIMENTO}.D60314.ESTABELE.csv"
CAMINHO_SAIDA = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/20260{MES}/estabelecimentos/Estabelecimentos{NUMERO_ESTABELECIMENTO}/K3241.K03200Y{NUMERO_ESTABELECIMENTO}.D60314.ESTABELE-Arapiraca_filtrado.csv"
# ==========================================

# Configurações fixas do layout da tabela
INDICE_MUNICIPIO = 20  # Coluna 21 (Python começa no 0)
INDICE_EMPRESA = 0    # Coluna 1

print(f"Iniciando a filtragem...")
print(f"Buscando município: {COD_MUNICIPIO}")

if not os.path.exists(CAMINHO_ENTRADA):
    print(f"Erro: O arquivo de entrada não foi encontrado.")
    exit(1)
    
    
print(f"Arquivo de origem: {CAMINHO_ENTRADA}")
print(f"Arquivo de destino: {CAMINHO_SAIDA}")

# Validação do arquivo de origem
if not os.path.exists(CAMINHO_ENTRADA):
    print(f"Erro: O arquivo de entrada '{CAMINHO_ENTRADA}' não foi encontrado.")
    exit(1)

try:
    linhas_filtradas = 0
    linhas_processadas = 0

    # Abre o arquivo de entrada para leitura e o de saída para escrita
    with open(CAMINHO_ENTRADA, 'r', encoding='iso-8859-1') as f_in, open(CAMINHO_SAIDA, 'w', encoding='utf-8') as f_out:
        
        # Como NÃO há cabeçalho, lemos linha por linha diretamente
        for linha in f_in:
            linhas_processadas += 1
            
            # Remove quebras de linha e separa por ponto e vírgula
            campos = linha.strip('\n').split(';')
            
            # -----------------------------------------------------------------
            # FEEDBACK / DIAGNÓSTICO: Mostra a estrutura das primeiras 5 linhas
            # -----------------------------------------------------------------
            if linhas_processadas <= 5:
                print(f"\n--- DIAGNÓSTICO DA LINHA {linhas_processadas} ---")
                print(f"Total de colunas detectadas nesta linha: {len(campos)}")
                if len(campos) > INDICE_MUNICIPIO:
                    valor_original = campos[INDICE_MUNICIPIO]
                    valor_limpo = valor_original.replace('"', '').strip()
                    print(f"Texto bruto na Coluna 21 (Índice 20): '{valor_original}'")
                    print(f"Texto limpo na Coluna 21 (Índice 20): '{valor_limpo}'")
                else:
                    print(f"AVISO: Esta linha tem apenas {len(campos)} colunas. Não alcança a coluna 21.")
                    if len(campos) > 0:
                        print(f"Conteúdo completo da linha para análise: {campos}")
                print("-" * 35)
            # -----------------------------------------------------------------
            
            # Verifica se a linha tem colunas suficientes para evitar erros de índice
            if len(campos) > INDICE_MUNICIPIO:
                municipio_limpo = campos[INDICE_MUNICIPIO].replace('"', '').strip()
                
                # Se o valor na coluna 21 (índice 20) for igual ao município buscado
                if municipio_limpo == str(COD_MUNICIPIO).strip():
                    cnpj_basico_limpo = campos[INDICE_EMPRESA].replace('"', '').strip()
                    campos[INDICE_EMPRESA] = cnpj_basico_limpo.zfill(8)
                    
                    campos = [campo.replace('"', '').strip() for campo in campos]
                    nova_linha = ';'.join(campos) + '\n'
                    f_out.write(nova_linha)
                    linhas_filtradas += 1

    print(f"\nProcesso concluído com sucesso!")
    print(f"Total de linhas analisadas no arquivo original: {linhas_processadas}")
    print(f"Total de linhas filtradas e salvas: {linhas_filtradas}")

except Exception as e:
    print(f"Ocorreu um erro durante o processamento: {e}")