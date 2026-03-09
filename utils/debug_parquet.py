import pandas as pd
import os
from pathlib import Path

# Procura o arquivo
base_dir = '/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/2025/'
arquivo_encontrado = None

print("🔍 Procurando arquivo Parquet filtrado...\n")

for root, dirs, files in os.walk(base_dir):
    for arquivo in files:
        if 'CAGEDMOV202501' in arquivo and 'Arapiraca' in arquivo and arquivo.endswith('.parquet'):
            arquivo_encontrado = os.path.join(root, arquivo)
            print(f"✅ Arquivo encontrado: {arquivo_encontrado}\n")
            break
    if arquivo_encontrado:
        break

if not arquivo_encontrado:
    print("❌ Arquivo não encontrado!")
    print(f"📂 Procurei em: {base_dir}")
    print("\n📋 Arquivos disponíveis:")
    for root, dirs, files in os.walk(base_dir):
        for arquivo in files:
            if arquivo.endswith('.parquet'):
                print(f"   - {os.path.join(root, arquivo)}")
    exit(1)

# Carrega o arquivo
df = pd.read_parquet(arquivo_encontrado)

print("=" * 80)
print("TODAS AS COLUNAS DO PARQUET:")
print("=" * 80)
for i, col in enumerate(df.columns, 1):
    print(f"{i:2d}. {repr(col):50s} | Tipo: {str(df[col].dtype):15s} | Não-nulos: {df[col].count()}")

print("\n" + "=" * 80)
print("PRIMEIRA LINHA COMPLETA:")
print("=" * 80)
primeira_linha = df.iloc[0]
for col, valor in primeira_linha.items():
    print(f"{col:40s} = {valor}")

print("\n" + "=" * 80)
print("COLUNAS QUE CONTÊM 'GRAU' OU 'INSTRUC':")
print("=" * 80)
colunas_grau = [col for col in df.columns if 'grau' in col.lower() or 'instruc' in col.lower()]
if colunas_grau:
    for col in colunas_grau:
        print(f"\n📋 Coluna: {repr(col)}")
        print(f"   Valores únicos: {sorted(df[col].dropna().unique())}")
        print(f"   Total de NULLs: {df[col].isna().sum()}")
        print(f"   Exemplo de valores:")
        print(df[col].value_counts().head())
else:
    print("⚠️  NENHUMA COLUNA ENCONTRADA COM 'GRAU' OU 'INSTRUC'!")
    print("\n🔍 Todas as colunas disponíveis:")
    for col in df.columns:
        print(f"   - {col}")