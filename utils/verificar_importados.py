# PYTHONPATH=. python utils/verificar_importados.py --ano 2026 --mes 01 --type MOV

import os
import sys
import django
from pathlib import Path

# Configuração do Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao

PASTA_ARQUIVOS = '/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/2026/202601'
CAMPOS_CHAVE = [
    'competênciamov', 'município', 'cbo2002ocupação', 'salário', 'idade', 'graudeinstrução', 'sexo', 
]

def linha_ja_importada(dados):
    filtro = {
        'competencia_movimentacao': dados['competênciamov'],
        'municipio_id': dados['município'],
        'cbo2002_ocupacao_id': dados['cbo2002ocupação'],
        'salario': dados['salário'],
        'idade': dados['idade'],
        'grau_instrucao_id': dados['graudeinstrução'],
        'sexo': dados['sexo'],
    }
    return Movimentacao.objects.filter(**filtro).exists()

def analisar_arquivo(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        header = f.readline().strip().split(';')
        idxs = {campo: header.index(campo) for campo in CAMPOS_CHAVE if campo in header}
        total = 0
        duplicados = 0
        for linha in f:
            campos = linha.strip().split(';')
            dados = {campo: campos[idxs[campo]] for campo in idxs}
            total += 1
            if linha_ja_importada(dados):
                duplicados += 1
        print(f"{os.path.basename(caminho)}: {duplicados}/{total} duplicados")

def analisar_pasta():
    for arquivo in os.listdir(PASTA_ARQUIVOS):
        if arquivo.endswith('.txt'):
            caminho = os.path.join(PASTA_ARQUIVOS, arquivo)
            analisar_arquivo(caminho)

if __name__ == "__main__":
    analisar_pasta()