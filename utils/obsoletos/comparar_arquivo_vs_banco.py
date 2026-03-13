# PYTHONPATH=. python utils/comparar_arquivo_vs_banco.py --ano 2023

"""
Compara total de registros nos arquivos Parquet vs Banco de Dados

Uso:
    PYTHONPATH=. python utils/comparar_arquivo_vs_banco.py --ano 2023
"""

import os
import sys
import django
import argparse
import pandas as pd
from pathlib import Path

# Configuração do Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao
from django.db.models import Count


def contar_registros_arquivos(base_dir, ano):
    """
    Conta quantos registros existem nos arquivos Parquet, agrupados por competência.
    """
    print(f"📂 Analisando arquivos em: {base_dir}")
    
    dados_arquivo = {}
    arquivos_processados = 0
    
    for root, dirs, files in os.walk(base_dir):
        for arquivo in sorted(files):
            if arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
                caminho = os.path.join(root, arquivo)
                
                try:
                    df = pd.read_parquet(caminho)
                    arquivos_processados += 1
                    
                    # Agrupa por competência
                    for _, row in df.iterrows():
                        comp = row.get('competênciamov')
                        if comp:
                            comp_str = str(comp)
                            # Filtra apenas o ano solicitado
                            if comp_str.startswith(str(ano)):
                                if comp_str not in dados_arquivo:
                                    dados_arquivo[comp_str] = 0
                                dados_arquivo[comp_str] += 1
                    
                except Exception as e:
                    print(f"   ❌ Erro ao processar {arquivo}: {e}")
    
    print(f"   ✓ Processados {arquivos_processados} arquivos\n")
    return dados_arquivo


def contar_registros_banco(ano):
    """
    Conta quantos registros existem no banco, agrupados por competência.
    """
    print(f"💾 Consultando banco de dados...")
    
    dados_banco = {}
    
    registros = Movimentacao.objects.filter(
        competencia_movimentacao__startswith=str(ano)
    ).values('competencia_movimentacao').annotate(
        total=Count('id')
    ).order_by('competencia_movimentacao')
    
    for reg in registros:
        comp = reg['competencia_movimentacao']
        dados_banco[comp] = reg['total']
    
    print(f"   ✓ Encontrados {len(dados_banco)} competências diferentes\n")
    return dados_banco


def comparar_dados(dados_arquivo, dados_banco):
    """
    Compara os dados dos arquivos com o banco e retorna relatório.
    """
    todas_competencias = sorted(set(list(dados_arquivo.keys()) + list(dados_banco.keys())))
    
    resultados = []
    total_arquivo = 0
    total_banco = 0
    total_faltando = 0
    meses_com_problema = []
    
    for comp in todas_competencias:
        qtd_arquivo = dados_arquivo.get(comp, 0)
        qtd_banco = dados_banco.get(comp, 0)
        diferenca = qtd_arquivo - qtd_banco
        
        total_arquivo += qtd_arquivo
        total_banco += qtd_banco
        
        if diferenca > 0:
            total_faltando += diferenca
            meses_com_problema.append({
                'competencia': comp,
                'faltando': diferenca,
                'arquivo': qtd_arquivo,
                'banco': qtd_banco
            })
        
        status = "✅ OK" if diferenca == 0 else ("⚠️ FALTA" if diferenca > 0 else "❓ EXTRA")
        
        resultados.append({
            'competencia': comp,
            'arquivo': qtd_arquivo,
            'banco': qtd_banco,
            'diferenca': diferenca,
            'status': status
        })
    
    return resultados, total_arquivo, total_banco, total_faltando, meses_com_problema


def exibir_relatorio(resultados, total_arquivo, total_banco, total_faltando, meses_com_problema, ano):
    """
    Exibe o relatório formatado.
    """
    print(f"{'='*90}")
    print(f"COMPARAÇÃO DETALHADA: Arquivos vs Banco de Dados - {ano}")
    print(f"{'='*90}\n")
    
    # Tabela detalhada
    print(f"{'Competência':<15} {'Arquivo':<12} {'Banco':<12} {'Diferença':<12} {'Status':<15}")
    print(f"{'-'*90}")
    
    for res in resultados:
        print(f"{res['competencia']:<15} {res['arquivo']:<12} {res['banco']:<12} {res['diferenca']:<12} {res['status']:<15}")
    
    print(f"{'-'*90}")
    print(f"{'TOTAL':<15} {total_arquivo:<12} {total_banco:<12} {total_faltando:<12}")
    
    # Resumo
    print(f"\n{'='*90}")
    print(f"📊 RESUMO GERAL")
    print(f"{'='*90}")
    print(f"  📁 Total nos arquivos: {total_arquivo:,} linhas")
    print(f"  💾 Total no banco: {total_banco:,} registros")
    
    if total_faltando > 0:
        percentual = (total_faltando / total_arquivo * 100) if total_arquivo > 0 else 0
        print(f"  ⚠️  Faltando importar: {total_faltando:,} registros ({percentual:.2f}%)")
    else:
        print(f"  ✅ Todos os registros foram importados corretamente!")
    
    print(f"{'='*90}\n")
    
    # Detalhamento dos problemas
    if meses_com_problema:
        print(f"{'='*90}")
        print(f"⚠️  MESES COM REGISTROS FALTANTES ({len(meses_com_problema)} meses)")
        print(f"{'='*90}\n")
        
        for mes in meses_com_problema:
            print(f"  📅 {mes['competencia']}:")
            print(f"     • No arquivo: {mes['arquivo']}")
            print(f"     • No banco: {mes['banco']}")
            print(f"     • Faltam: {mes['faltando']}")
            print()
        
        print(f"{'='*90}")
        print(f"💡 SUGESTÕES PARA CORRIGIR:")
        print(f"{'='*90}\n")
        
        if len(meses_com_problema) <= 3:
            print(f"  Opção 1: Reimportar apenas os meses problemáticos")
            for mes in meses_com_problema:
                mes_numero = mes['competencia'][-2:]
                print(f"    PYTHONPATH=. python utils/reimportar_erros.py --ano {ano} --mes {mes_numero}")
        else:
            print(f"  Opção 1: Reimportar todo o ano {ano}")
            print(f"    # Limpar o ano")
            print(f"    psql \"...\" -c \"DELETE FROM movimentacoes WHERE competencia_mov LIKE '{ano}%';\"")
            print(f"    # Importar novamente")
            print(f"    PYTHONPATH=. python utils/importar_parquet_para_db.py --ano {ano}")
        
        print(f"\n  Opção 2: Reimportar tudo com verificação de duplicados")
        print(f"    PYTHONPATH=. python utils/reimportar_erros.py --ano {ano}")
        
        print(f"\n{'='*90}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comparar arquivos Parquet vs Banco de Dados")
    parser.add_argument('--ano', required=True, help='Ano a verificar (ex: 2023)')
    args = parser.parse_args()
    
    # Define diretório base
    base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{args.ano}/'
    
    # Verifica se o diretório existe
    if not os.path.isdir(base_dir):
        print(f"❌ Diretório não encontrado: {base_dir}")
        sys.exit(1)
    
    print(f"\n{'='*90}")
    print(f"🔍 ANÁLISE DE CONSISTÊNCIA - ANO {args.ano}")
    print(f"{'='*90}\n")
    
    # 1. Conta registros nos arquivos
    dados_arquivo = contar_registros_arquivos(base_dir, args.ano)
    
    if not dados_arquivo:
        print(f"⚠️  Nenhum registro encontrado nos arquivos para o ano {args.ano}")
        sys.exit(1)
    
    # 2. Conta registros no banco
    dados_banco = contar_registros_banco(args.ano)
    
    # 3. Compara
    resultados, total_arquivo, total_banco, total_faltando, meses_com_problema = comparar_dados(
        dados_arquivo, 
        dados_banco
    )
    
    # 4. Exibe relatório
    exibir_relatorio(
        resultados, 
        total_arquivo, 
        total_banco, 
        total_faltando, 
        meses_com_problema, 
        args.ano
    )