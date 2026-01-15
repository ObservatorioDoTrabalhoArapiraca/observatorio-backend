import os
import py7zr

# Caminho da pasta onde estão os arquivos .7z
pasta = '/home/usuario/Github/NOVO CAGED/2020/202002'
# Caminho da pasta onde estão os arquivos .7z
# pasta = r'D:\NOVO CAGED\2020\202002'

for arquivo in os.listdir(pasta):
    if arquivo.endswith('.7z'):
        caminho_arquivo = os.path.join(pasta, arquivo)
        try:
            with py7zr.SevenZipFile(caminho_arquivo, mode='r') as z:
                z.extractall(path=pasta)
            print(f"Descompactado: {caminho_arquivo}")
        except Exception as e:
            print(f"Erro ao descompactar {caminho_arquivo}: {e}")