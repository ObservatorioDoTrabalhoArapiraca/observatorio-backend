import os
from utils.conversao_utils import txt_para_parquet

base_dir = '/home/usuario/Github/NOVO CAGED'


for ano in os.listdir(base_dir):
    ano_path = os.path.join(base_dir, ano)
    if not os.path.isdir(ano_path):
        continue
    for mes in os.listdir(ano_path):
        mes_path = os.path.join(ano_path, mes)
        if not os.path.isdir(mes_path):
            continue
        # Remove arquivos .7z restantes
        for arquivo in os.listdir(mes_path):
            if arquivo.endswith('.7z'):
                caminho_7z = os.path.join(mes_path, arquivo)
                try:
                    os.remove(caminho_7z)
                    print(f"Removido: {caminho_7z}")
                except Exception as e:
                    print(f"Erro ao remover {caminho_7z}: {e}")
        # Converte e remove .txt
        for arquivo in os.listdir(mes_path):
            if arquivo.endswith('.txt'):
                caminho_txt = os.path.join(mes_path, arquivo)
                caminho_parquet = caminho_txt.replace('.txt', '.parquet')
                try:
                    txt_para_parquet(caminho_txt, caminho_parquet)
                    print(f"Convertido: {caminho_txt} -> {caminho_parquet}")
                    os.remove(caminho_txt)
                    print(f"Removido: {caminho_txt}")
                except Exception as e:
                    print(f"Erro ao converter/remover {caminho_txt}: {e}")