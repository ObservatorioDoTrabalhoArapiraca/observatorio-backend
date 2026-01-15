from utils.conversao_utils import txt_para_parquet

# Caminho do seu arquivo .txt
arquivo_txt = "/home/usuario/Github/NOVO CAGED/2020/202002/CAGEDMOV202002.txt"

arquivo_parquet_saida = "/home/usuario/Github/parquet filtrados/NOVO CAGED/2020/202002/CAGEDMOV202002.parquet"
# Converter para Parquet
arquivo_parquet = txt_para_parquet(arquivo_txt)
print(f"Arquivo Parquet gerado: {arquivo_parquet}")

# python3 Utils/converter_em_parquet.py


# Resumo:
# Sempre que for trabalhar no projeto, ative o ambiente virtual com 

# # # source .venv/bin/activate.

# Assim, você pode instalar e usar qualquer pacote Python sem afetar o sistema.