"""
Script para importar dados de movimentações do CAGED para o banco de dados.

Uso:
    PYTHONPATH=. python utils/importar_parquet_para_db.py --ano 2023
    PYTHONPATH=. python utils/importar_parquet_para_db.py --ano 2023 --mes 01
    PYTHONPATH=. python utils/importar_parquet_para_db.py --ano 2023 --limite 100
"""

import os
import sys
import django
import argparse
import pandas as pd
import gc
from pathlib import Path

# Configuração do Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from apps.referenciais.models import (
    MunicipioReferencia,
    Cbo2002ocupacaoReferencia,
    GraudeinstrucaoReferencia,
    RacaCorReferencia,
    SexoReferencia,
    TipoDeficienciaReferencia,
)
from apps.movimentacoes.models import Movimentacao

# Variável global para limite de linhas
LIMITE_LINHAS = None


def limpar_numero(valor):
    """
    Converte string com vírgula em número float.
    Exemplos: '36,00' -> 36.0 | '1.020,50' -> 1020.5
    """
    if valor is None or pd.isna(valor):
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

    # Remove pontos de milhar e troca vírgula por ponto
    valor_str = str(valor).replace('.', '').replace(',', '.')

    try:
        return float(valor_str)
    except (ValueError, TypeError):
        return None


def get_referencia(model, codigo):
    """Busca um registro na tabela de referência."""
    try:
        if codigo is None or pd.isna(codigo):
            return None

        # Converte para int se for possível
        try:
            codigo = int(codigo)
        except (ValueError, TypeError):
            pass

        obj = model.objects.filter(codigo=codigo).first()

        if obj is None:
            print(f"      ⚠️  {model.__name__} código '{codigo}' não encontrado")

        return obj

    except Exception as e:
        print(f"      ❌ Erro ao buscar {model.__name__} código {codigo}: {e}")
        return None


def processar_movimentacao(df):
    """Processa e salva dados de movimentação (CAGEDMOV)"""
    print(f"  📊 Processando {len(df)} registros de movimentação...")

    registros_processados = 0
    registros_com_erro = 0
    erros_detalhados = []

    for idx, row in df.iterrows():
        try:
            with transaction.atomic():
                # Mostra progresso a cada 100 registros
                if idx > 0 and idx % 100 == 0:
                    print(f"      📝 Progresso: {idx}/{len(df)} registros (erros: {registros_com_erro})")

                # Busca referências
                municipio = get_referencia(MunicipioReferencia, row.get('município'))
                cbo = get_referencia(Cbo2002ocupacaoReferencia, row.get('cbo2002ocupação'))
                grau_instrucao = get_referencia(GraudeinstrucaoReferencia, row.get('graudeinstrução'))
                raca_cor = get_referencia(RacaCorReferencia, row.get('raçacor'))
                sexo = get_referencia(SexoReferencia, row.get('sexo'))
                tipo_deficiencia = get_referencia(TipoDeficienciaReferencia, row.get('tipodedeficiência'))

                # Limpa campos numéricos
                salario = limpar_numero(row.get('salário'))
                idade = limpar_numero(row.get('idade'))
                saldo_movimentacao = row.get('saldomovimentação')

                # Converte saldo_movimentacao
                if pd.notna(saldo_movimentacao):
                    try:
                        saldo_movimentacao = int(float(saldo_movimentacao))
                    except (ValueError, TypeError):
                        saldo_movimentacao = None
                else:
                    saldo_movimentacao = None

                # Converte idade para inteiro
                if idade is not None:
                    idade = int(idade)

                # Cria o objeto
                movimentacao = Movimentacao(
                    competencia_movimentacao=row.get('competênciamov'),
                    municipio=municipio,
                    cbo2002_ocupacao=cbo,
                    grau_instrucao=grau_instrucao,
                    idade=idade,
                    raca_cor=raca_cor,
                    sexo=sexo,
                    tipo_deficiencia=tipo_deficiencia,
                    saldo_movimentacao=saldo_movimentacao,
                    salario=salario,
                )

                movimentacao.save()
                registros_processados += 1

        except Exception as e:
            registros_com_erro += 1

            # Captura informações detalhadas do erro
            import traceback
            erro_traceback = traceback.format_exc()

            erro_info = {
                'arquivo': 'atual',
                'linha': idx + 1,
                'tipo_erro': type(e).__name__,
                'mensagem_erro': str(e),
                'traceback': erro_traceback,
                'dados': {
                    'competencia': row.get('competênciamov'),
                    'municipio': row.get('município'),
                    'cbo': row.get('cbo2002ocupação'),
                    'salario': row.get('salário'),
                    'idade': row.get('idade'),
                    'saldo': row.get('saldomovimentação'),
                    'sexo': row.get('sexo'),
                    'raca_cor': row.get('raçacor'),
                    'grau_instrucao': row.get('graudeinstrução'),
                }
            }
            erros_detalhados.append(erro_info)

    # Resumo do processamento
    print(f"\n  {'='*50}")
    print(f"  ✅ Total processado: {registros_processados}")
    print(f"  ⚠️  Erros: {registros_com_erro}")
    print(f"  {'='*50}")

    return registros_processados, erros_detalhados


def importar_parquet(caminho_arquivo):
    """Importa arquivo Parquet filtrado para o banco de dados"""
    nome_arquivo = os.path.basename(caminho_arquivo)
    print(f"\n→ Processando: {nome_arquivo}")

    try:
        # Carrega o arquivo Parquet
        df = pd.read_parquet(caminho_arquivo)
        print(f"  📁 Total de registros no arquivo: {len(df)}")

        # Aplica limite se definido
        if LIMITE_LINHAS:
            df = df.head(LIMITE_LINHAS)
            print(f"  🔢 Limitado a: {len(df)} linhas")

        # Verifica se o arquivo está vazio
        if len(df) == 0:
            print(f"  ⚠️  Arquivo vazio, pulando...")
            return True, []

        # Processa as movimentações
        registros, erros = processar_movimentacao(df)

        # Adiciona nome do arquivo aos erros
        for erro in erros:
            erro['arquivo'] = nome_arquivo

        print(f"  ✓ Arquivo processado!\n")
        return True, erros

    except Exception as e:
        print(f"  ✗ Erro ao carregar arquivo: {e}")
        import traceback
        traceback.print_exc()

        return False, [{
            'arquivo': nome_arquivo,
            'tipo_erro': 'ErroCarregamento',
            'mensagem_erro': str(e),
            'traceback': traceback.format_exc()
        }]

    finally:
        gc.collect()


if __name__ == "__main__":
    # Argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Importar movimentações (CAGEDMOV) de Arapiraca")
    parser.add_argument('--ano', required=True, help='Ano a ser processado (ex: 2023)')
    parser.add_argument('--mes', help='Mês específico (opcional, ex: 01)')
    parser.add_argument('--limite', type=int, help='Limitar número de linhas por arquivo (teste)')
    args = parser.parse_args()

    # Aplica limite se fornecido
    if args.limite:
        LIMITE_LINHAS = args.limite

    # Define diretório base
    base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{args.ano}/'

    # Verifica se o diretório existe
    if not os.path.isdir(base_dir):
        print(f"❌ Diretório não encontrado: {base_dir}")
        sys.exit(1)

    # Cabeçalho
    print(f"\n{'='*60}")
    print(f"🔍 IMPORTAÇÃO DE DADOS DO CAGED - ARAPIRACA")
    print(f"{'='*60}")
    print(f"📂 Diretório: {base_dir}")
    print(f"📅 Ano: {args.ano}")
    if args.mes:
        print(f"📆 Mês: {args.mes}")
    if LIMITE_LINHAS:
        print(f"🔢 Limite: {LIMITE_LINHAS} linhas por arquivo")
    print(f"{'='*60}")

    # Busca arquivos
    arquivos_encontrados = []

    for root, dirs, files in os.walk(base_dir):
        for arquivo in sorted(files):
            if arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
                # Filtra por mês se especificado
                if args.mes:
                    partes = arquivo.split('-')[0]  # Ex: CAGEDMOV202301
                    if len(partes) >= 8:
                        mes_no_arquivo = partes[-2:]  # Últimos 2 dígitos
                        if mes_no_arquivo != args.mes:
                            continue

                caminho_completo = os.path.join(root, arquivo)
                arquivos_encontrados.append(caminho_completo)

    # Verifica se encontrou arquivos
    if not arquivos_encontrados:
        print(f"\n⚠️  Nenhum arquivo filtrado encontrado!")
        if args.mes:
            print(f"   Mês especificado: {args.mes}")
        sys.exit(1)

    print(f"\n✓ Encontrados {len(arquivos_encontrados)} arquivo(s)\n")

    # Processa arquivos
    total_importados = 0
    total_erros_arquivo = 0
    todos_erros = []

    for caminho_completo in arquivos_encontrados:
        sucesso, erros = importar_parquet(caminho_completo)

        if sucesso:
            total_importados += 1
        else:
            total_erros_arquivo += 1

        todos_erros.extend(erros)

    # Resumo final
    print(f"\n{'='*60}")
    print(f"📊 RESUMO DA IMPORTAÇÃO")
    print(f"{'='*60}")
    print(f"   ✅ Arquivos importados: {total_importados}/{len(arquivos_encontrados)}")
    print(f"   ❌ Arquivos com erro: {total_erros_arquivo}")
    print(f"   ⚠️  Total de erros de registro: {len(todos_erros)}")
    if LIMITE_LINHAS:
        print(f"   📦 Limite aplicado: {LIMITE_LINHAS} linhas/arquivo")
    print(f"{'='*60}")

    # Mostra análise detalhada dos erros
    if todos_erros:
        print(f"\n{'='*60}")
        print(f"❌ ANÁLISE DETALHADA DOS ERROS ({len(todos_erros)} total)")
        print(f"{'='*60}")

        # Agrupa por tipo de erro
        erros_por_tipo = {}
        for erro in todos_erros:
            tipo = erro.get('tipo_erro', 'Desconhecido')
            if tipo not in erros_por_tipo:
                erros_por_tipo[tipo] = []
            erros_por_tipo[tipo].append(erro)

        # Mostra cada tipo de erro (ordenado por frequência)
        for idx, (tipo, ocorrencias) in enumerate(
            sorted(erros_por_tipo.items(), key=lambda x: len(x[1]), reverse=True), 1
        ):
            print(f"\n{'─'*60}")
            print(f"{idx}. TIPO: {tipo}")
            print(f"   Ocorrências: {len(ocorrencias)}")
            print(f"{'─'*60}")

            # Mostra até 3 exemplos deste tipo
            for i, erro in enumerate(ocorrencias[:3], 1):
                print(f"\n   Exemplo {i}:")
                print(f"   📁 Arquivo: {erro.get('arquivo')}")
                print(f"   📍 Linha: {erro.get('linha')}")
                print(f"   💬 Mensagem: {erro.get('mensagem_erro')}")

                dados = erro.get('dados', {})
                if dados:
                    print(f"   📊 Dados da linha:")
                    for chave, valor in dados.items():
                        print(f"      • {chave}: {valor}")

                # Mostra traceback completo apenas do primeiro exemplo
                if i == 1:
                    print(f"\n   🐛 Traceback completo:")
                    traceback_lines = erro.get('traceback', 'N/A').split('\n')
                    for line in traceback_lines:
                        print(f"      {line}")

        print(f"\n{'='*60}\n")

    else:
        print(f"\n✅ Importação concluída sem erros!\n")