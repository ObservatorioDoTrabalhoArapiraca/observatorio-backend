import os
import zipfile
from utils.conversao_utils import txt_para_parquet
from filterToColumn import filtrar_parquet_por_coluna

# Caminho do arquivo Parquet original (ajuste para o caminho real no seu PC)
base_dir = '/home/usuario/Github/NOVO CAGED'
# base_dir = 'D:/NOVO CAGED'
# ano = 2020
# mes = "01"
# arquivo_entrada = f'{base_dir}/{ano}/{ano}{mes}/CAGEDMOV{ano}{mes}/CAGEDMOV{ano}{mes}.parquet'

# Nome da coluna e valor para filtrar
coluna = 'município'
valor = 270030 # Al-Arapiraca

# Caminho do arquivo de saída (opcional)
# arquivo_saida = f'/home/usuario/Github/NOVO CAGED/{ano}/{ano}{mes}/CAGEDMOV{ano}{mes}/CAGEDMOV{ano}{mes}-Al-Arapiraca_filtrado.parquet'

# Executa a filtragem
# filtrar_parquet_por_coluna(arquivo_entrada, coluna, valor, arquivo_saida)
# print(f"Arquivo filtrado salvo em: {arquivo_saida}")

# txt_para_parquet(caminho_do_txt, caminho_do_parquet)

# 1. Descompacta todos os arquivos zip
for root, dirs, files in os.walk(base_dir):
    for arquivo in files:
        if arquivo.endswith('.zip'):
            zip_path = os.path.join(root, arquivo)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(root)
            print(f"Arquivo zip descompactado: {zip_path}")


# 2. Converte e filtra todos os arquivos txt
for root, dirs, files in os.walk(base_dir):
    for arquivo in files:
        if arquivo.endswith('.txt'):
            caminho_txt = os.path.join(root, arquivo)
            caminho_parquet = caminho_txt.replace('.txt', '.parquet')
            txt_para_parquet(caminho_txt, caminho_parquet)
            print(f"Arquivo Txt convertido para Parquet: {caminho_parquet}")
            arquivo_saida = caminho_parquet.replace('.parquet', '-Al-Arapiraca_filtrado.parquet')
            filtrar_parquet_por_coluna(caminho_parquet, coluna, valor, arquivo_saida)
            print(f"Arquivo filtrado salvo em: {arquivo_saida}")


# for ano in os.listdir(base_dir):
#     ano_path = os.path.join(base_dir, ano)
#     if not os.path.isdir(ano_path):
#         continue
#     for mes in os.listdir(ano_path):
#         mes_path = os.path.join(ano_path, mes)
#         if not os.path.isdir(mes_path):
#             continue
#         # Procura o arquivo Parquet dentro da pasta do mês
#         for pasta_caged in os.listdir(mes_path):
#             pasta_caged_path = os.path.join(mes_path, pasta_caged)
#             if not os.path.isdir(pasta_caged_path):
#                 continue
#             for arquivo in os.listdir(pasta_caged_path):
#                 if arquivo.endswith('.zip'):
#                   zip_path = os.path.join(pasta_caged_path, arquivo)
#                   with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                     zip_ref.extractall(pasta_caged_path)
#                   print(f"Arquivo zip Descompactado: {zip_path}")
                  
                  
#                   for arquivo in os.listdir(pasta_caged_path):
                    
#                     if arquivo.endswith('.txt'):
#                       caminho_txt = os.path.join(pasta_caged_path, arquivo)
#                       caminho_parquet = caminho_txt.replace('.txt', '.parquet')
#                       txt_para_parquet(caminho_txt, caminho_parquet)
#                       print(f"Arquivo Txt convertido para Parquet: {caminho_parquet}")
#                       # arquivo_entrada = os.path.join(pasta_caged_path, arquivo)
#                       arquivo_saida = caminho_parquet.replace('.parquet', '-Al-Arapiraca_filtrado.parquet')
#                       filtrar_parquet_por_coluna(caminho_parquet, coluna, valor, arquivo_saida)
#                       print(f"Arquivo filtrado salvo em: {arquivo_saida}")

