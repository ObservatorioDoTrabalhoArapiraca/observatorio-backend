import os
import glob

MES = "04"
PASTA_ESTABELECIMENTOS = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/2026{MES}/estabelecimentos/"
ARQUIVO_UNICO_SAIDA = f"/mnt/c/Users/Usuário/Documents/Empresas CNPJ/2026{MES}/estabelecimentos/Estabelecimentos_Unificados_Arapiraca.csv"

print("Iniciando a unificação e normalização estrutural das tabelas...")

# Busca por todos os arquivos que terminam com '-Arapiraca_filtrado.csv' ou '_filtrado_normalizado.csv'
# dentro de todas as subpastas Estabelecimentos0, Estabelecimentos1, etc.
arquivos_alvo = glob.glob(os.path.join(PASTA_ESTABELECIMENTOS, "Estabelecimentos*", "*-Arapiraca_filtrado*.csv"))

if not arquivos_alvo:
    print("Erro: Nenhum arquivo filtrado de Arapiraca foi encontrado nas subpastas.")
    exit(1)

print(f"Foram encontrados {len(arquivos_alvo)} arquivos para unificar.")

# Definição exata do novo cabeçalho ordenado
CABECALHO = [
    'CNPJ', 'NOME_FANTASIA', 'SITUAÇÃO CADASTRAL', 'ENDEREÇO', 
    'BAIRRO', 'MUNICÍPIO', 'CNAE PRINCIPAL', 'TELEFONE', 
    'EMAIL', 'RAZAO SOCIAL', 'PORTE DA EMPRESA', 'VISITADA', 'DATA DA VISITA'
]

try:
    total_linhas_processadas = 0
    
    with open(ARQUIVO_UNICO_SAIDA, 'w', encoding='utf-8') as f_out:
        # 1. Escreve o cabeçalho na primeira linha do arquivo único
        f_out.write(';'.join(CABECALHO) + '\n')
        
        for caminho_arquivo in arquivos_alvo:
            print(f" Processando: {os.path.basename(caminho_arquivo)}")
            
            with open(caminho_arquivo, 'r', encoding='utf-8') as f_in:
                for linha in f_in:
                    # Se por acaso a linha capturada for um cabeçalho antigo, pula ela
                    if "CNPJ" in linha or "município" in linha.lower():
                        continue
                        
                    campos = linha.strip('\n').split(';')
                    
                    # Ignora linhas vazias ou corrompidas que não tenham colunas suficientes
                    if len(campos) < 21:
                        continue
                        
                    total_linhas_processadas += 1
                    
                    # --- PROCESSAMENTO E MONTAGEM DA NOVA LINHA ---
                    nova_linha_dados = []
                    
                    # [0] CNPJ (Unificação das colunas 1, 2 e 3 + Truque de Texto para o Excel)
                    cnpj_basico = campos[0].replace('"', '').strip().zfill(8)
                    cnpj_ordem = campos[1].replace('"', '').strip().zfill(4)
                    cnpj_dv = campos[2].replace('"', '').strip().zfill(2)
                    cnpj_completo = f'="{cnpj_basico}{cnpj_ordem}{cnpj_dv}"'
                    nova_linha_dados.append(cnpj_completo)
                    
                    # [1] NOME_FANTASIA (Índice 4)
                    nova_linha_dados.append(campos[4].replace('"', '').strip())
                    
                    # [2] SITUAÇÃO CADASTRAL (Índice 5)
                    nova_linha_dados.append(campos[5].replace('"', '').strip())
                    
                    # [3] ENDEREÇO (Fusão de Tipo Logradouro [13], Logradouro [14], Número [15], Complemento [16], CEP [18])
                    tipo_logra = campos[13].replace('"', '').strip()
                    logradouro = campos[14].replace('"', '').strip()
                    numero = campos[15].replace('"', '').strip()
                    complem = campos[16].replace('"', '').strip()
                    cep = campos[18].replace('"', '').strip()
                    
                    # Monta o endereço de forma limpa, omitindo campos se estiverem vazios
                    partes_endereco = [f"{tipo_logra} {logradouro}".strip(), f"Nº {numero}" if numero else "", complem, f"CEP: {cep}" if cep else ""]
                    endereco_completo = ", ".join([p for p in partes_endereco if p])
                    nova_linha_dados.append(endereco_completo)
                    
                    # [4] BAIRRO (Índice 17)
                    nova_linha_dados.append(campos[17].replace('"', '').strip())
                    
                    # [5] MUNICÍPIO (Índice 20)
                    nova_linha_dados.append(campos[20].replace('"', '').strip())
                    
                    # [6] CNAE PRINCIPAL (Índice 11)
                    nova_linha_dados.append(campos[11].replace('"', '').strip())
                    
                    # [7] TELEFONE (DDD1[21] + Tel1[22] / DDD2[23] + Tel2[24])
                    ddd1 = campos[21].replace('"', '').strip()
                    tel1 = campos[22].replace('"', '').strip()
                    ddd2 = campos[23].replace('"', '').strip()
                    tel2 = campos[24].replace('"', '').strip()
                    
                    telefones = []
                    if ddd1 or tel1: telefones.append(f"({ddd1}) {tel1}".strip())
                    if ddd2 or tel2: telefones.append(f"({ddd2}) {tel2}".strip())
                    telefone_final = " / ".join(telefones) if telefones else ""
                    nova_linha_dados.append(telefone_final)
                    
                    # [8] EMAIL (Índice 27)
                    nova_linha_dados.append(campos[27].replace('"', '').strip())
                    
                    # [9] RAZAO SOCIAL (Inicia em branco, o próximo script preenche)
                    nova_linha_dados.append("")
                    
                    # [10] PORTE DA EMPRESA (Inicia em branco, o próximo script preenche)
                    nova_linha_dados.append("")
                    
                    # [11] VISITADA (Padrão: Não)
                    nova_linha_dados.append("Não")
                    
                    # [12] DATA DA VISITA (Inicia em branco)
                    nova_linha_dados.append("")
                    
                    # Escreve a linha formatada no arquivo unificado
                    f_out.write(';'.join(nova_linha_dados) + '\n')

    print(f"\n==========================================")
    print(f"Unificação concluída com sucesso!")
    print(f"Total de registros consolidados: {total_linhas_processadas}")
    print(f"Arquivo mestre gerado em: {ARQUIVO_UNICO_SAIDA}")
    print(f"==========================================")

except Exception as e:
    print(f"Ocorreu um erro crítico durante a unificação: {e}")