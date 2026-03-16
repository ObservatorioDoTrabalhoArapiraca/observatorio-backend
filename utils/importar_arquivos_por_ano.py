"""
Script de importação detalhada de arquivos TXT por ano

Este script importa todos os arquivos TXT de um ano, linha por linha,
rastrea cada falha e fornece relatório completo ao final.

Uso:
    PYTHONPATH=. python utils/importar_arquivos_por_ano.py --ano 2024 --limit 10

    # PYTHONPATH=. python utils/importar_arquivos_por_ano.py --ano 2021 > saida_importacao2021.txt 2>&1

   pra ver o que tá no arquivo de saída, abre outro terminal e digita: tail -f saida_importacao.txt
"""

import os
import sys
import django
import argparse
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

import time
print("Início do script:", time.strftime("%H:%M:%S"))


parser = argparse.ArgumentParser(description='Script de importação detalhada de arquivos TXT por ano')
parser.add_argument('--ano', required=True, help='Ano a ser analisado (ex: 2020)')
parser.add_argument('--limit', type=int, default=None, help='Limite de linhas a importar (para testes)')
args = parser.parse_args()

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao
from django.core.exceptions import ValidationError


print("Antes de conectar ao banco:", time.strftime("%H:%M:%S"))
# código de conexão ao banco
print("Conectado ao banco:", time.strftime("%H:%M:%S"))

COLUNAS_BANCO = [
    'competênciamov', 'município', 'saldomovimentação', 'cbo2002ocupação',
    'graudeinstrução', 'idade', 'raçacor', 'sexo', 'tipodedeficiência', 'salário'
]


def obter_tipo_python(valor):
    return type(valor).__name__

def formatar_valor_para_exibicao(valor):
    if valor is None:
        return 'None'
    elif isinstance(valor, str) and len(valor) > 50:
        return f'"{valor[:50]}..."'
    else:
        return str(valor)

def exibir_dados_linha(id_sequencial, dados_estruturados, mostrar_todos=False):
    print(f"   ID: {id_sequencial}")
    campos_para_mostrar = dados_estruturados.items()
    if not mostrar_todos:
        campos_para_mostrar = list(dados_estruturados.items())[:5]
    for campo, info in campos_para_mostrar:
        valor_formatado = formatar_valor_para_exibicao(info['valor'])
        print(f"   • {campo}: {valor_formatado} ({info['tipo']})")
    if not mostrar_todos and len(dados_estruturados) > 5:
        print(f"   ... e mais {len(dados_estruturados) - 5} campos")

def validar_e_preparar_dados(dados_estruturados, id_sequencial):
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
        if sal_valor is None or sal_valor in ['', 'NA', '0', '00', ',0', ',00' ]:
            sal_valor = Decimal('0.00')
        else:
            try:
                if isinstance(sal_valor, str):
                    sal_valor = sal_valor.replace(',', '.')  # Substitui vírgula por ponto, se necessário
                # Trabalha com o valor como string para truncar as casas decimais
                sal_valor_str = str(sal_valor)
                if '.' in sal_valor_str:  # Se houver parte decimal
                    parte_inteira, parte_decimal = sal_valor_str.split('.')
                    sal_valor_str = f"{parte_inteira}.{parte_decimal[:2]}"  # Trunca para 2 casas decimais
                else:
                    sal_valor_str = f"{sal_valor_str}.00"  # Adiciona ".00" se não houver parte decimal
                sal_valor = Decimal(sal_valor_str)  # Converte para Decimal após truncar
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

def tentar_inserir_no_banco(dados_preparados, id_sequencial):
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
        erro_str = str(e)
        if 'foreign key constraint' in erro_str.lower() or 'violates foreign key' in erro_str.lower():
            if 'cbo2002_ocupacao_id' in erro_str:
                return (False, f"CBO '{dados_preparados.get('cbo2002_ocupacao_id')}' não existe na tabela de referência")
            elif 'municipio_id' in erro_str:
                return (False, f"Município '{dados_preparados.get('municipio_id')}' não existe na tabela de referência")
            elif 'grau_instrucao_id' in erro_str:
                return (False, f"Grau Instrução '{dados_preparados.get('grau_instrucao_id')}' não existe na tabela de referência")
            elif 'sexo_id' in erro_str:
                return (False, f"Sexo '{dados_preparados.get('sexo_id')}' não existe na tabela de referência")
            elif 'raca_cor_id' in erro_str:
                return (False, f"Raça/Cor '{dados_preparados.get('raca_cor_id')}' não existe na tabela de referência")
            elif 'tipo_deficiencia_id' in erro_str:
                return (False, f"Tipo Deficiência '{dados_preparados.get('tipo_deficiencia_id')}' não existe na tabela de referência")
            else:
                return (False, f"Erro de Foreign Key: {erro_str}")
        elif 'connection' in erro_str.lower() or 'timeout' in erro_str.lower():
            return (False, f"Perda de conexão com o banco: {erro_str}")
        else:
            return (False, f"Erro ao salvar no banco: {erro_str}")

def importar_arquivo_txt(caminho_arquivo, pasta, arquivo, relatorio_erros, limit=None):
    print(f"\n{'='*90}")
    print(f"📂 IMPORTAÇÃO DETALHADA DE ARQUIVO TXT")
    print(f"{'='*90}\n")
    print(f"Arquivo: {caminho_arquivo}")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    if not os.path.isfile(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        relatorio_erros.append({'pasta': pasta, 'arquivo': arquivo, 'linha': 0, 'motivo': 'Arquivo não encontrado'})
        return
    print(f"✓ Arquivo encontrado")
    try:
        print(f"⏳ Lendo arquivo TXT...")
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        print(f"✓ Arquivo lido")
        print(f"   Linhas: {len(linhas)-1}")
    except Exception as e:
        print(f"❌ Erro ao ler: {str(e)}")
        relatorio_erros.append({'pasta': pasta, 'arquivo': arquivo, 'linha': 0, 'motivo': f"Erro ao ler arquivo: {str(e)}"})
        return
    header = linhas[0].strip().split(';')
    total_linhas_arquivo = len(linhas) - 1
    print(f"Total de linhas no arquivo: {total_linhas_arquivo:,}")
    total_banco_antes = Movimentacao.objects.count()
    print(f"Total no banco (antes): {total_banco_antes:,}")
    linhas_com_falha = []
    linhas_importadas_com_sucesso = 0
    linhas_a_processar = linhas[1:]
    if limit:
        linhas_a_processar = linhas_a_processar[:limit]
    for id_sequencial, linha in enumerate(linhas_a_processar, start=1):
        campos = linha.strip().split(';')
        row_dict = dict(zip(header, campos))
        row_filtrado = {col: row_dict.get(col) for col in COLUNAS_BANCO if col in row_dict}
        dados_estruturados = {}
        for coluna in COLUNAS_BANCO:
            valor = row_filtrado.get(coluna)
            valor_limpo = valor if valor not in [None, '', 'NA'] else None
            dados_estruturados[coluna] = {
                'valor': valor_limpo,
                'tipo': obter_tipo_python(valor_limpo)
            }
        sucesso_validacao, dados_preparados, erro_validacao = validar_e_preparar_dados(
            dados_estruturados, 
            id_sequencial
        )
        if not sucesso_validacao:
            print(f"Linha {id_sequencial} ERRO na validação:")
            exibir_dados_linha(id_sequencial, dados_estruturados, mostrar_todos=True)
            print(f"   ❌ Motivo: {erro_validacao}\n")
            linhas_com_falha.append({
                'id_sequencial': id_sequencial,
                'dados': dados_estruturados,
                'motivo_erro': erro_validacao,
                'pasta': pasta,
                'arquivo': arquivo
            })
            relatorio_erros.append({'pasta': pasta, 'arquivo': arquivo, 'linha': id_sequencial, 'motivo': erro_validacao})
            continue
        sucesso_insercao, erro_insercao = tentar_inserir_no_banco(
            dados_preparados, 
            id_sequencial
        )
        if not sucesso_insercao:
            print(f"Linha {id_sequencial} ERRO na inserção:")
            exibir_dados_linha(id_sequencial, dados_estruturados, mostrar_todos=True)
            print(f"   ❌ Motivo: {erro_insercao}\n")
            linhas_com_falha.append({
                'id_sequencial': id_sequencial,
                'dados': dados_estruturados,
                'motivo_erro': erro_insercao,
                'pasta': pasta,
                'arquivo': arquivo
            })
            relatorio_erros.append({'pasta': pasta, 'arquivo': arquivo, 'linha': id_sequencial, 'motivo': erro_insercao})
            continue
        linhas_importadas_com_sucesso += 1
        print(f"Linha {id_sequencial} importada ✓")
    total_banco_depois = Movimentacao.objects.count()
    total_importado = total_banco_depois - total_banco_antes
    print(f"\n{'='*90}")
    print(f"📊 ETAPA 4: CONTAGEM FINAL")
    print(f"{'='*90}\n")
    print(f"Total de linhas no banco (depois): {total_banco_depois:,}")
    print(f"Linhas importadas nesta execução: {total_importado:,}")
    print(f"Linhas com sucesso (contador): {linhas_importadas_com_sucesso:,}")
    print(f"Total de falhas: {len(linhas_com_falha):,}")
    print(f"\n{'='*90}")
    print(f"📋 RELATÓRIO FINAL")
    print(f"{'='*90}\n")
    total_estimado = total_banco_antes + total_linhas_arquivo
    print(f"Total de linhas no arquivo: {total_linhas_arquivo:,}")
    print(f"Total de linhas no banco (antes): {total_banco_antes:,}")
    print(f"Total de linhas no banco (depois): {total_banco_depois:,}")
    print(f"Total estimado de linhas no banco : {total_estimado:,}")
    print(f"Diferença do estimado para o que tem no banco : { total_banco_depois - total_estimado:,}")
    print(f"Total de falhas: {len(linhas_com_falha):,}\n")
    if len(linhas_com_falha) > 0:
        print(f"{'='*90}")
        print(f"❌ LINHAS COM FALHA ({len(linhas_com_falha)})")
        print(f"{'='*90}\n")
        for falha in linhas_com_falha:
            print(f"Pasta: {falha['pasta']} | Arquivo: {falha['arquivo']} | ID: {falha['id_sequencial']}")
            exibir_dados_linha(
                falha['id_sequencial'], 
                falha['dados'], 
                mostrar_todos=True
            )
            print(f"   ❌ Motivo: {falha['motivo_erro']}\n")
            print(f"{'-'*90}\n")
    else:
        print(f"✅ Todas as linhas foram importadas com sucesso!\n")
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*90}\n")

def importar_todos_os_arquivos_do_ano(ano, limit=None):
    # base_dir = f'/home/charlie/Documentos/NOVO CAGED/{ano}'
    base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{ano}'
    relatorio_erros = []
    total_linhas_analisadas = 0
    total_banco_antes = Movimentacao.objects.count()
    for pasta in sorted(os.listdir(base_dir)):
        pasta_path = os.path.join(base_dir, pasta)
        if not os.path.isdir(pasta_path):
            continue
        for arquivo in sorted(os.listdir(pasta_path)):
            if arquivo.endswith('.txt'):
                caminho_arquivo = os.path.join(pasta_path, arquivo)
                print(f"Importando: {caminho_arquivo}")
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                linhas_a_processar = linhas[1:]
                if limit:
                    linhas_a_processar = linhas_a_processar[:limit]
                total_linhas_analisadas += len(linhas_a_processar)
                importar_arquivo_txt(caminho_arquivo, pasta, arquivo, relatorio_erros, limit)
                total_banco_depois = Movimentacao.objects.count()
    print("\n" + "="*90)
    print("RELATÓRIO FINAL DE ERROS (GERAL)")
    print("="*90)
    print(f"Total de linhas analisadas: {total_linhas_analisadas:,}")
    print(f"Total de linhas no banco (antes): {total_banco_antes:,}")
    print(f"Total de linhas no banco (depois): {total_banco_depois:,}")
    print(f"Total estimado de linhas no banco : {total_banco_antes + total_linhas_analisadas:,}")
    print(f"Diferença do estimado para o que tem no banco : {total_banco_depois - (total_banco_antes + total_linhas_analisadas):,}")
    if relatorio_erros:
        for erro in relatorio_erros:
            print(f"Pasta: {erro['pasta']} | Arquivo: {erro['arquivo']} | Linha: {erro['linha']} | Motivo: {erro['motivo']}")
    else:
        print("✅ Todos os arquivos importados sem erros.")
    print("="*90)

if __name__ == "__main__":
    importar_todos_os_arquivos_do_ano(args.ano, args.limit)