#  PYTHONPATH=. python utils/importar_por_pasta.py --pasta '/home/charlie/Documentos/NOVO CAGED/2025/202502'

import os
import sys
import django
import argparse
from pathlib import Path
from django import db

# Setup do Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Importamos a função mestre que já tem os prints de erro por linha
from utils.importar_desde_linha import importar_desde

def processar_pasta(caminho_pasta):
    if not os.path.exists(caminho_pasta):
        print(f"❌ Erro: A pasta '{caminho_pasta}' não foi encontrada.")
        return

    arquivos = [f for f in os.listdir(caminho_pasta) if f.endswith('.txt')]
    arquivos.sort()

    if not arquivos:
        print(f"⚠️ Nenhum arquivo .txt encontrado em {caminho_pasta}")
        return

    total_arquivos = len(arquivos)
    print(f"📂 [DIRETÓRIO] {caminho_pasta}")
    print(f"📊 [TOTAL] {total_arquivos} arquivos encontrados.")
    print("=" * 60)

    for idx, arquivo in enumerate(arquivos, 1):
        caminho_completo = os.path.join(caminho_pasta, arquivo)
        
        # Feedback de progresso de arquivos
        print(f"\n🚀 Arquivo [{idx}/{total_arquivos}]: {arquivo}")
        print(f"---" * 10)
        
        try:
            # Ao chamar essa função, os logs de linha (100, 200, 300...) 
            # e os erros específicos de cada linha aparecerão aqui.
            importar_desde(arquivo=caminho_completo, linha_inicial=1, limite=None)
            
            # Limpeza de segurança após terminar cada arquivo
            db.connections.close_all()
            
        except Exception as e:
            # Esse erro aqui só dispara se a função 'importar_desde' travar inteira (erro fatal)
            print(f"🚨 FALHA CRÍTICA NO ARQUIVO {arquivo}: {e}")
            continue 

    print("\n" + "=" * 60)
    print("✅ PROCESSAMENTO DE PASTA FINALIZADO COM SUCESSO!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--pasta', required=True)
    args = parser.parse_args()
    
    processar_pasta(args.pasta)