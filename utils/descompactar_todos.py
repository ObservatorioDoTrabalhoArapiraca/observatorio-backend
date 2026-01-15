import os
import py7zr

base_dir = '/home/usuario/Github/NOVO CAGED'
# base_dir = 'D:/NOVO CAGED'

for ano in os.listdir(base_dir):
    ano_path = os.path.join(base_dir, ano)
    if not os.path.isdir(ano_path):
        continue
    for mes in os.listdir(ano_path):
        mes_path = os.path.join(ano_path, mes)
        if not os.path.isdir(mes_path):
            continue
        # Se já existe algum .txt na pasta, ignora a descompactação
        if any(f.endswith('.txt') for f in os.listdir(mes_path)):
            print(f"Pasta {mes_path} já possui .txt, ignorando descompactação.")
            continue
        for arquivo in os.listdir(mes_path):
            if arquivo.endswith('.7z'):
                caminho_arquivo = os.path.join(mes_path, arquivo)
                try:
                    with py7zr.SevenZipFile(caminho_arquivo, mode='r') as z:
                        z.extractall(path=mes_path)
                    print(f"Descompactado: {caminho_arquivo}")
                    os.remove(caminho_arquivo)
                    print(f"Arquivo .7z removido: {caminho_arquivo}")
                except Exception as e:
                    print(f"Erro ao descompactar {caminho_arquivo}: {e}")