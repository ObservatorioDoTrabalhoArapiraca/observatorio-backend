
# PYTHONPATH=. python utils/importar_linha_arquivo.py --arquivo /home/charlie/Documentos/NOVO\ CAGED/2025/202508/CAGEDMOV202508-Al-Arapiraca_filtrado.txt --id_linha 142 
import os
import sys
import django
import argparse
from pathlib import Path
from decimal import Decimal
from datetime import datetime

# Ajuste o caminho do projeto conforme necessário
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao
from django.core.exceptions import ValidationError

COLUNAS_BANCO = [
    'competênciamov', 'município', 'saldomovimentação', 'cbo2002ocupação',
    'graudeinstrução', 'idade', 'raçacor', 'sexo', 'tipodedeficiência', 'salário'
]

def validar_e_preparar_dados(dados_estruturados):
    try:
        dados_preparados = {}
        colunas_disponiveis = list(dados_estruturados.keys())
        coluna_competencia = None
        for possivel_nome in ['competênciamov', 'competencia', 'Competência', 'COMPETENCIA', 'competência', 'competência_mov', 'competencia_mov']:
            if possivel_nome in dados_estruturados:
                coluna_competencia = possivel_nome
                break
        if not coluna_competencia:
            return (False, None, f"Campo 'competencia' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        comp_valor = dados_estruturados[coluna_competencia]['valor']
        if comp_valor is None:
            return (False, None, f"Campo 'competencia' está vazio (None)")
        dados_preparados['competencia_movimentacao'] = comp_valor

        coluna_cbo = None
        for possivel_nome in ['cbo2002ocupação', 'cbo2002', 'CBO', 'cbo']:
            if possivel_nome in dados_estruturados:
                coluna_cbo = possivel_nome
                break
        if not coluna_cbo:
            return (False, None, f"Campo 'cbo' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        cbo_valor = dados_estruturados[coluna_cbo]['valor']
        if cbo_valor is None:
            return (False, None, "Campo 'cbo' está vazio (None)")
        dados_preparados['cbo2002_ocupacao_id'] = cbo_valor

        coluna_municipio = None
        for possivel_nome in ['município', 'municipio', 'Município', 'MUNICIPIO']:
            if possivel_nome in dados_estruturados:
                coluna_municipio = possivel_nome
                break
        if not coluna_municipio:
            return (False, None, f"Campo 'municipio' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        mun_valor = dados_estruturados[coluna_municipio]['valor']
        if mun_valor is None:
            return (False, None, "Campo 'municipio' está vazio (None)")
        dados_preparados['municipio_id'] = mun_valor

        coluna_salario = None
        for possivel_nome in [ 'salario', 'salário', 'Salario', 'SALARIO']:
            if possivel_nome in dados_estruturados:
                coluna_salario = possivel_nome
                break
        if not coluna_salario:
            return (False, None, f"Campo 'salario' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        sal_valor = dados_estruturados[coluna_salario]['valor']
        if sal_valor is None:
            return (False, None, "Campo 'salario' está vazio (None)")
        try:
            if isinstance(sal_valor, str):
                sal_valor = sal_valor.replace(',', '.')
            sal_valor = Decimal(str(sal_valor))
        except Exception:
            return (False, None, f"Campo 'salario' deve ser decimal, recebeu '{sal_valor}'")
        dados_preparados['salario'] = sal_valor

        coluna_saldo = None
        for possivel_nome in ['saldomovimentação', 'saldo_movimentacao', 'saldo']:
            if possivel_nome in dados_estruturados:
                coluna_saldo = possivel_nome
                break
        if coluna_saldo:
            saldo_valor = dados_estruturados[coluna_saldo]['valor']
            if saldo_valor is not None:
                dados_preparados['saldo_movimentacao'] = saldo_valor

        if 'sexo' in dados_estruturados:
            sexo_valor = dados_estruturados['sexo']['valor']
            if sexo_valor is not None:
                dados_preparados['sexo_id'] = sexo_valor
        if 'idade' in dados_estruturados:
            idade_valor = dados_estruturados['idade']['valor']
            if idade_valor is not None and idade_valor != '':
                try: 
                    dados_preparados['idade'] = int(idade_valor)
                except Exception:
                    return (False, None, f"Campo 'idade' deve ser um número inteiro, recebeu '{idade_valor}'")
        for possivel_nome in ['raçacor', 'racacor', 'raca_cor']:
            if possivel_nome in dados_estruturados:
                raca_valor = dados_estruturados[possivel_nome]['valor']
                if raca_valor is not None:
                    dados_preparados['raca_cor_id'] = raca_valor
                break
        for possivel_nome in ['graudeinstrução', 'grauinstrucao', 'grau_instrucao']:
            if possivel_nome in dados_estruturados:
                grau_valor = dados_estruturados[possivel_nome]['valor']
                if grau_valor is not None:
                    dados_preparados['grau_instrucao_id'] = grau_valor
                break
        coluna_def = None
        for nome in ['tipodedeficiência', 'tipodeficiencia', 'tipo_deficiencia']:
            if nome in dados_estruturados:
                coluna_def = nome
                break
        if coluna_def:
            def_valor = dados_estruturados[coluna_def]['valor']
            if def_valor is not None:
                dados_preparados['tipo_deficiencia_id'] = def_valor
        return (True, dados_preparados, None)
    except Exception as e:
        return (False, None, f"Erro inesperado na validação: {str(e)}")


def tentar_inserir_no_banco(dados_preparados):
    try:
        movimentacao = Movimentacao(**dados_preparados)
        movimentacao.full_clean()
        movimentacao.save()
        return (True, None)
    except ValidationError as e:
        erros = []
        for campo, mensagens in e.message_dict.items():
            erros.append(f"{campo}: {', '.join(mensagens)}")
        return (False, f"Erro de validação: {'; '.join(erros)}")
    except Exception as e:
        return (False, f"Erro ao salvar no banco: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importar uma linha específica de um arquivo TXT para o banco")
    parser.add_argument('--arquivo', required=True, type=str, help="Caminho completo do arquivo .txt")
    parser.add_argument('--id_linha', required=True, type=int, help="ID sequencial da linha (igual ao do script de importação)")
    args = parser.parse_args()

    with open(args.arquivo, 'r', encoding='utf-8') as f:
        linhas = f.readlines()
    header = linhas[0].strip().split(';')
    linha = linhas[args.id_linha].strip()
    campos = linha.split(';')
    row_dict = dict(zip(header, campos))
    row_filtrado = {col: row_dict.get(col) for col in COLUNAS_BANCO if col in row_dict}
    dados_estruturados = {}
    for coluna in COLUNAS_BANCO:
        valor = row_filtrado.get(coluna)
        valor_limpo = valor if valor not in [None, '', 'NA'] else None
        dados_estruturados[coluna] = {'valor': valor_limpo, 'tipo': type(valor_limpo).__name__}

    # Copie a função validar_e_preparar_dados do importador e use aqui:
    sucesso_validacao, dados_preparados, erro_validacao = validar_e_preparar_dados(dados_estruturados)
    if not sucesso_validacao:
        print(f"❌ Erro na validação: {erro_validacao}")
        sys.exit(1)
    sucesso_insercao, erro_insercao = tentar_inserir_no_banco(dados_preparados)
    if sucesso_insercao:
        print("✅ Linha importada com sucesso!")
    else:
        print(f"❌ Erro ao inserir no banco: {erro_insercao}")