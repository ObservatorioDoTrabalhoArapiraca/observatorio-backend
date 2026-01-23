# from utils.conversao_utils import txt_para_parquet

# ls "/home/usuario/Github/NOVO CAGED/2025/202502/"

# ano = 2025
# mes = '202504'
# tipo_arquivo = 'CAGEDMOV'
# tipo_arquivo = 'CAGEDEXC'
# tipo_arquivo = 'CAGEDFOR'
# Caminho do seu arquivo .txt
# arquivo_txt = "/home/usuario/Github/NOVO CAGED/2025/202502/CAGEDEXEC202502.txt"
# arquivo_txt = f"/home/usuario/Github/NOVO CAGED/{ano}/{mes}/{tipo_arquivo}{mes}.txt"

# arquivo_parquet_saida = f"/home/usuario/Github/NOVO CAGED/{ano}/{mes}/{tipo_arquivo}{mes}.parquet"
# Converter para Parquet
# arquivo_parquet = txt_para_parquet(arquivo_txt)
# print(f"Arquivo Parquet gerado: {arquivo_parquet}")

# python3 Utils/converter_em_parquet.py


# Resumo:
# Sempre que for trabalhar no projeto, ative o ambiente virtual com 

# # # source .venv/bin/activate.

# Assim, você pode instalar e usar qualquer pacote Python sem afetar o sistema.


import gc
import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa

# Limpa memória antes de iniciar
gc.collect()

# ls "/home/usuario/Github/NOVO CAGED/2025/202502/"

ano = 2025
mes = '202501'
tipo_arquivo = 'CAGEDMOV'
# tipo_arquivo = 'CAGEDEXC'
# tipo_arquivo = 'CAGEDFOR'

# Caminho do seu arquivo .txt
arquivo_txt = f"/home/usuario/Github/NOVO CAGED/{ano}/{mes}/{tipo_arquivo}{mes}.txt"
arquivo_parquet_saida = f"/home/usuario/Github/NOVO CAGED/{ano}/{mes}/{tipo_arquivo}{mes}.parquet"

print(f"Iniciando conversão de {arquivo_txt}")
print(f"Destino: {arquivo_parquet_saida}")

# Configuração do chunk
chunksize = 100000

try:
    # Cria um iterador para ler o TXT em pedaços
    reader = pd.read_csv(
        arquivo_txt, 
        sep=';', 
        chunksize=chunksize, 
        low_memory=False, 
        encoding='utf-8'
    )
    
    writer = None
    total_linhas = 0
    
    for i, chunk in enumerate(reader):
        # Converte o chunk para Tabela PyArrow
        table = pa.Table.from_pandas(chunk)
        
        # Na primeira iteração, cria o ParquetWriter
        if writer is None:
            writer = pq.ParquetWriter(arquivo_parquet_saida, table.schema)
        
        # Escreve o chunk no arquivo
        writer.write_table(table)
        
        total_linhas += len(chunk)
        print(f"Chunk {i+1} processado: {len(chunk)} linhas | Total: {total_linhas}")
        
        # Limpa memória a cada chunk
        del chunk
        del table
        gc.collect()
    
    # Fecha o arquivo após processar todos os chunks
    if writer:
        writer.close()
        print(f"\nArquivo Parquet gerado com sucesso: {arquivo_parquet_saida}")
        print(f"Total de linhas processadas: {total_linhas}")
    else:
        print("Nenhum dado foi processado.")

except Exception as e:
    print(f"Erro durante a conversão: {e}")
    raise

finally:
    # Limpa memória após finalizar
    gc.collect()
    print("Memória limpa.")

# python3 utils/converter_em_parquet.py

# Resumo:
# Sempre que for trabalhar no projeto, ative o ambiente virtual com 
# source .venv/bin/activate.
# Assim, você pode instalar e usar qualquer pacote Python sem afetar o sistema.