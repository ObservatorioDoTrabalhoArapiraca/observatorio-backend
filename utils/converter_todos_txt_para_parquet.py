# PYTHONPATH=. python utils/converter_todos_txt_para_parquet.py --ano 2020


# Padrão (chunks de 100.000 linhas)
# PYTHONPATH=. python utils/converter_todos_txt_para_parquet.py --ano 2020

# # Chunks menores (se tiver pouca memória)
# PYTHONPATH=. python utils/converter_todos_txt_para_parquet.py --ano 2020 --chunksize 50000

# PYTHONPATH=. python utils/converter_todos_txt_para_parquet.py --ano 2020

# Padrão (chunks de 100.000 linhas)
# PYTHONPATH=. python utils/converter_todos_txt_para_parquet.py --ano 2020

# Chunks menores (se tiver pouca memória)
# PYTHONPATH=. python utils/converter_todos_txt_para_parquet.py --ano 2020 --chunksize 50000

import os
import argparse
import sys
import gc
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa

def txt_para_parquet_chunked(caminho_txt, caminho_parquet, chunksize=100000):
    """
    Converte arquivo TXT para Parquet processando em chunks
    """
    try:
        reader = pd.read_csv(
            caminho_txt,
            sep=';',
            chunksize=chunksize,
            low_memory=False,
            encoding='utf-8'
        )
        
        writer = None
        total_linhas = 0
        
        for i, chunk in enumerate(reader):
            table = pa.Table.from_pandas(chunk)
            
            if writer is None:
                writer = pq.ParquetWriter(caminho_parquet, table.schema)
            
            writer.write_table(table)
            total_linhas += len(chunk)
            
            # Limpa memória a cada chunk
            del chunk
            del table
            gc.collect()
        
        if writer:
            writer.close()
            return True
        return False
        
    except Exception as e:
        raise e
    finally:
        gc.collect()


parser = argparse.ArgumentParser(description="Converter arquivos TXT para Parquet por ano.")
parser.add_argument('--ano', required=True, help='Ano a ser processado (ex: 2020)')
parser.add_argument('--chunksize', type=int, default=100000, help='Tamanho do chunk (padrão: 100000)')
args = parser.parse_args()

base_dir = f'/home/usuario/Github/NOVO CAGED/{args.ano}/'

if not os.path.isdir(base_dir):
    print(f"Diretório não encontrado: {base_dir}")
    exit(1)
    
total_convertidos = 0
total_ignorados = 0
total_pastas = 0
total_arquivos_encontrados = 0

for mes in sorted(os.listdir(base_dir)):
    mes_path = os.path.join(base_dir, mes)
    if not os.path.isdir(mes_path):
        continue
    
    total_pastas += 1
    print(f"\n--- Processando pasta: {mes} ---")
    
    arquivos_na_pasta = os.listdir(mes_path)
    total_arquivos_encontrados += len(arquivos_na_pasta)
    
    # Debug: mostra todos os arquivos encontrados
    print(f"  Arquivos encontrados: {len(arquivos_na_pasta)}")
    for arq in arquivos_na_pasta:
        print(f"    - {arq}")
    
    for arquivo in arquivos_na_pasta:
        if arquivo.endswith('.txt'):
            caminho_txt = os.path.join(mes_path, arquivo)
            caminho_parquet = caminho_txt.replace('.txt', '.parquet')
            
            # Verifica se o arquivo Parquet já existe
            if os.path.exists(caminho_parquet):
                print(f"  ✓ Já existe: {arquivo}")
                total_ignorados += 1
                continue
            
            try:
                print(f"  → Convertendo: {arquivo}...")
                txt_para_parquet_chunked(caminho_txt, caminho_parquet, args.chunksize)
                print(f"  ✓ Convertido: {arquivo}")
                total_convertidos += 1
            except MemoryError:
                print(f"  ✗ Erro de memória ao converter {arquivo}. Encerrando o script.")
                sys.exit(1)
            except Exception as e:
                print(f"  ✗ Erro ao converter {arquivo}: {e}")
                
print(f"\n{'='*60}")
print(f"Resumo da conversão:")
print(f"  Pastas processadas: {total_pastas}")
print(f"  Total de arquivos encontrados: {total_arquivos_encontrados}")
print(f"  Arquivos .txt convertidos: {total_convertidos}")
print(f"  Arquivos .txt ignorados: {total_ignorados}")
print(f"{'='*60}")