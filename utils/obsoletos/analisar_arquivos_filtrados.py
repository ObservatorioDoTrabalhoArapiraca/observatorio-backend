# PYTHONPATH=. python utils/analisar_arquivos_filtrados.py --ano 2020

import os
import argparse
import pyarrow.parquet as pq

parser = argparse.ArgumentParser(description="Analisar arquivos filtrados de Arapiraca.")
parser.add_argument('--ano', required=True, help='Ano a ser analisado (ex: 2020)')
args = parser.parse_args()

base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{args.ano}/'

total_linhas = 0
total_tamanho_mb = 0
arquivos_encontrados = []

print(f"\n{'='*80}")
print(f"Analisando arquivos filtrados de Arapiraca - Ano {args.ano}")
print(f"{'='*80}\n")

# Percorre todos os arquivos
for root, dirs, files in os.walk(base_dir):
    for arquivo in files:
        if arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
            caminho_completo = os.path.join(root, arquivo)
            
            try:
                # Lê o arquivo parquet
                tabela = pq.read_table(caminho_completo)
                num_linhas = len(tabela)
                
                # Calcula tamanho em MB
                tamanho_bytes = os.path.getsize(caminho_completo)
                tamanho_mb = tamanho_bytes / (1024 * 1024)
                
                # Acumula totais
                total_linhas += num_linhas
                total_tamanho_mb += tamanho_mb
                
                # Armazena info do arquivo
                arquivos_encontrados.append({
                    'arquivo': arquivo,
                    'linhas': num_linhas,
                    'tamanho_mb': tamanho_mb
                })
                
                print(f"✓ {arquivo}")
                print(f"  Linhas: {num_linhas:,} | Tamanho: {tamanho_mb:.2f} MB\n")
                
            except Exception as e:
                print(f"✗ Erro ao processar {arquivo}: {e}\n")

# Exibe resumo final
print(f"{'='*80}")
print(f"RESUMO FINAL {args.ano}")
print(f"{'='*80}")
print(f"Total de arquivos encontrados: {len(arquivos_encontrados)}")
print(f"Total de linhas: {total_linhas:,}")
print(f"Tamanho total: {total_tamanho_mb:.2f} MB ({total_tamanho_mb/1024:.2f} GB)")
print(f"{'='*80}\n")

# Análise de viabilidade
if total_tamanho_mb < 512:
    print("✓ VIÁVEL: Tamanho total menor que 512 MB")
elif total_tamanho_mb < 1024:
    print("⚠ ATENÇÃO: Tamanho próximo ao limite (512 MB - 1 GB)")
else:
    print("✗ INVIÁVEL: Tamanho maior que 1 GB, considere outra estratégia")
    
# ================================================================================
# RESUMO FINAL 2020
# ================================================================================
# Total de arquivos encontrados: 32
# Total de linhas: 6,219
# Tamanho total: 0.65 MB (0.00 GB)
# ================================================================================

# ✓ VIÁVEL: Tamanho total menor que 512 MB

# ================================================================================
# RESUMO FINAL 2021
# ================================================================================
# Total de arquivos encontrados: 36
# Total de linhas: 5,482
# Tamanho total: 0.72 MB (0.00 GB)
# ================================================================================

# ✓ VIÁVEL: Tamanho total menor que 512 MB

# ================================================================================
# RESUMO FINAL 2022
# ================================================================================
# Total de arquivos encontrados: 36
# Total de linhas: 17,856
# Tamanho total: 0.85 MB (0.00 GB)
# ================================================================================

# ✓ VIÁVEL: Tamanho total menor que 512 MB


# ================================================================================
# RESUMO FINAL 2023
# ================================================================================
# Total de arquivos encontrados: 36
# Total de linhas: 11,270
# Tamanho total: 0.78 MB (0.00 GB)
# ================================================================================

# ✓ VIÁVEL: Tamanho total menor que 512 MB

# ================================================================================
# RESUMO FINAL 2024
# ================================================================================
# Total de arquivos encontrados: 36
# Total de linhas: 3,109
# Tamanho total: 0.69 MB (0.00 GB)
# ================================================================================

# ✓ VIÁVEL: Tamanho total menor que 512 MB

# ================================================================================
# RESUMO FINAL 2025
# ================================================================================
# Total de arquivos encontrados: 30
# Total de linhas: 2,084
# Tamanho total: 0.57 MB (0.00 GB)
# ================================================================================

# ✓ VIÁVEL: Tamanho total menor que 512 MB


# =================================
# RESUMO FINAL 2026
# ================================================================================
# Total de arquivos encontrados: 3
# Total de linhas: 125
# Tamanho total: 0.06 MB (0.00 GB)
# ================================================================================

# ✓ VIÁVEL: Tamanho total menor que 512 MB