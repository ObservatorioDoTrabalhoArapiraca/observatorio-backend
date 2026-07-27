"""
Verifica se há perda de dados entre arquivo Parquet e banco de dados

Uso:
    PYTHONPATH=. python utils/verificar_perda_dados.py --ano 2023 --cbo 521110
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


def analisar_arquivo_parquet(base_dir, ano, cbo_filtro=None):
    """Analisa os arquivos Parquet originais"""
    print(f"\n{'='*90}")
    print(f"📂 ANÁLISE DOS ARQUIVOS PARQUET")
    print(f"{'='*90}\n")
    
    total_linhas = 0
    total_com_cbo = 0
    registros_por_mes = {}
    arquivos_analisados = []
    erros = []
    
    for root, dirs, files in os.walk(base_dir):
        for arquivo in sorted(files):
            if arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
                caminho = os.path.join(root, arquivo)
                
                try:
                    print(f"   📄 Lendo: {arquivo}")
                    df = pd.read_parquet(caminho)
                    linhas_arquivo = len(df)
                    total_linhas += linhas_arquivo
                    
                    # Verifica colunas disponíveis
                    colunas = df.columns.tolist()
                    print(f"      • Total de linhas: {linhas_arquivo:,}")
                    
                    # Identifica coluna de CBO
                    coluna_cbo = None
                    for col in colunas:
                        if 'cbo' in col.lower():
                            coluna_cbo = col
                            break
                    
                    if not coluna_cbo:
                        print(f"      ⚠️  Coluna CBO não encontrada. Colunas: {colunas[:5]}...")
                        continue
                    
                    print(f"      • Coluna CBO: {coluna_cbo}")
                    
                    # Identifica coluna de competência
                    coluna_comp = None
                    for col in colunas:
                        if 'compet' in col.lower():
                            coluna_comp = col
                            break
                    
                    if coluna_comp:
                        print(f"      • Coluna Competência: {coluna_comp}")
                    
                    # Inicializa contador
                    linhas_com_cbo = 0
                    
                    # Filtra por CBO se especificado
                    if cbo_filtro and coluna_cbo:
                        # Tenta diferentes formatos do CBO
                        df_filtrado = df[
                            (df[coluna_cbo].astype(str) == str(cbo_filtro)) |
                            (df[coluna_cbo].astype(str) == cbo_filtro) |
                            (df[coluna_cbo].astype(str).str.replace('-', '') == str(cbo_filtro)) |
                            (df[coluna_cbo].astype(str).str.zfill(6) == str(cbo_filtro))
                        ]
                        
                        linhas_com_cbo = len(df_filtrado)
                        total_com_cbo += linhas_com_cbo
                        
                        print(f"      • Registros com CBO {cbo_filtro}: {linhas_com_cbo:,}")
                        
                        if linhas_com_cbo > 0:
                            # Mostra alguns exemplos
                            print(f"      • Exemplos de valores CBO encontrados:")
                            exemplos_cbo = df_filtrado[coluna_cbo].head(5).tolist()
                            for ex in exemplos_cbo:
                                print(f"        - {ex}")
                            
                            # Agrupa por competência
                            if coluna_comp:
                                por_comp = df_filtrado.groupby(coluna_comp).size()
                                print(f"      • Distribuição por competência:")
                                for comp, qtd in por_comp.items():
                                    comp_str = str(int(comp)) if isinstance(comp, float) else str(comp)
                                    comp_formatada = comp_str.zfill(6)
                                    print(f"        - {comp_formatada}: {qtd:,} registros")
                                    
                                    if comp_formatada not in registros_por_mes:
                                        registros_por_mes[comp_formatada] = 0
                                    registros_por_mes[comp_formatada] += qtd
                    
                    arquivos_analisados.append({
                        'arquivo': arquivo,
                        'total': linhas_arquivo,
                        'com_cbo': linhas_com_cbo if cbo_filtro else linhas_arquivo
                    })
                    
                    print()
                    
                except Exception as e:
                    erro_msg = f"Erro ao processar {arquivo}: {str(e)}"
                    print(f"      ❌ {erro_msg}\n")
                    erros.append(erro_msg)
    
    print(f"{'='*90}")
    print(f"📊 RESUMO DOS ARQUIVOS PARQUET")
    print(f"{'='*90}\n")
    print(f"   • Arquivos analisados: {len(arquivos_analisados)}")
    print(f"   • Total de linhas: {total_linhas:,}")
    
    if cbo_filtro:
        print(f"   • Total com CBO {cbo_filtro}: {total_com_cbo:,}")
        
        if registros_por_mes:
            print(f"\n   📅 Registros por mês:")
            for mes in sorted(registros_por_mes.keys()):
                print(f"      • {mes}: {registros_por_mes[mes]:,}")
    
    if erros:
        print(f"\n   ⚠️  Erros encontrados: {len(erros)}")
        for erro in erros:
            print(f"      • {erro}")
    
    print(f"\n{'='*90}\n")
    
    return total_linhas, total_com_cbo, registros_por_mes


def analisar_banco(ano, cbo_filtro=None):
    """Analisa dados no banco de dados"""
    print(f"\n{'='*90}")
    print(f"💾 ANÁLISE DO BANCO DE DADOS")
    print(f"{'='*90}\n")
    
    # Total geral no ano
    queryset = Movimentacao.objects.filter(
        competencia_movimentacao__startswith=str(ano)
    )
    total_ano = queryset.count()
    print(f"   • Total de registros no ano {ano}: {total_ano:,}")
    
    # Com CBO específico
    if cbo_filtro:
        queryset_cbo = queryset.filter(cbo2002_ocupacao_id=str(cbo_filtro))
        total_cbo = queryset_cbo.count()
        print(f"   • Total com CBO {cbo_filtro}: {total_cbo:,}")
        
        if total_cbo > 0:
            # Por competência
            from django.db.models import Count
            por_mes = queryset_cbo.values('competencia_movimentacao').annotate(
                total=Count('id')
            ).order_by('competencia_movimentacao')
            
            print(f"\n   📅 Registros por competência:")
            registros_banco = {}
            for item in por_mes:
                comp = item['competencia_movimentacao']
                qtd = item['total']
                print(f"      • {comp}: {qtd:,}")
                registros_banco[comp] = qtd
            
            # Mostra exemplos
            print(f"\n   📝 Exemplos de registros no banco:")
            exemplos = queryset_cbo[:5]
            for idx, mov in enumerate(exemplos, 1):
                print(f"      {idx}. ID: {mov.id}")
                print(f"         Comp: {mov.competencia_movimentacao}")
                print(f"         CBO: {mov.cbo2002_ocupacao_id}")
                print(f"         Município: {mov.municipio_id}")
                print(f"         Salário: R$ {mov.salario:.2f}")
                print(f"         Saldo Mov: {mov.saldo_movimentacao}")
                print()
            
            print(f"{'='*90}\n")
            return total_ano, total_cbo, registros_banco
    
    print(f"{'='*90}\n")
    return total_ano, 0, {}


def comparar_resultados(registros_arquivo, registros_banco):
    """Compara registros entre arquivo e banco"""
    print(f"\n{'='*90}")
    print(f"🔄 COMPARAÇÃO ARQUIVO vs BANCO")
    print(f"{'='*90}\n")
    
    # Normaliza as chaves para string
    registros_arquivo_norm = {str(k): v for k, v in registros_arquivo.items()}
    registros_banco_norm = {str(k): v for k, v in registros_banco.items()}
    
    todas_competencias = sorted(set(list(registros_arquivo_norm.keys()) + list(registros_banco_norm.keys())))
    
    perdas = []
    total_perdido = 0
    
    print(f"{'Competência':<15} {'Arquivo':<12} {'Banco':<12} {'Diferença':<12} {'Status':<15}")
    print(f"{'-'*90}")
    
    for comp in todas_competencias:
        qtd_arquivo = registros_arquivo_norm.get(comp, 0)
        qtd_banco = registros_banco_norm.get(comp, 0)
        diferenca = qtd_arquivo - qtd_banco
        
        if diferenca > 0:
            status = "❌ PERDEU"
            perdas.append((comp, diferenca, qtd_arquivo, qtd_banco))
            total_perdido += diferenca
        elif diferenca < 0:
            status = "❓ EXTRA"
        else:
            status = "✅ OK"
        
        print(f"{comp:<15} {qtd_arquivo:<12,} {qtd_banco:<12,} {diferenca:<12,} {status:<15}")
    
    print(f"{'-'*90}")
    
    total_arquivo = sum(registros_arquivo_norm.values())
    total_banco = sum(registros_banco_norm.values())
    
    print(f"{'TOTAL':<15} {total_arquivo:<12,} {total_banco:<12,} {total_perdido:<12,}")
    
    if perdas:
        print(f"\n{'='*90}")
        print(f"⚠️  PERDA DE DADOS DETECTADA")
        print(f"{'='*90}\n")
        
        if total_arquivo > 0:
            percentual = (total_perdido / total_arquivo) * 100
            print(f"   • Total no arquivo: {total_arquivo:,}")
            print(f"   • Total no banco: {total_banco:,}")
            print(f"   • Registros perdidos: {total_perdido:,} ({percentual:.2f}%)")
        
        print(f"\n   📋 Detalhamento das perdas:")
        for comp, qtd_perdida, qtd_arq, qtd_banco in perdas:
            print(f"      • {comp}: Perdidos {qtd_perdida:,} de {qtd_arq:,} registros")
        
        print(f"\n{'='*90}")
        print(f"🔍 POSSÍVEIS CAUSAS")
        print(f"{'='*90}\n")
        print(f"   1. Erros durante a importação (validação, conversão de tipos)")
        print(f"   2. Registros duplicados sendo ignorados")
        print(f"   3. Transações falhando parcialmente")
        print(f"   4. Filtros aplicados durante importação")
        print(f"   5. Problemas de encoding ou caracteres especiais")
        
        print(f"\n{'='*90}")
        print(f"💡 RECOMENDAÇÕES")
        print(f"{'='*90}\n")
        
        ano = list(registros_arquivo_norm.keys())[0][:4] if registros_arquivo_norm else '2023'
        print(f"   1. Execute o script de importação mês a mês com rastreamento:")
        print(f"      PYTHONPATH=. python utils/importar_mes_a_mes.py --ano {ano} --mes 1")
        print(f"\n   2. Verifique os logs de erro gerados")
        print(f"\n   3. Use o modo de diagnóstico detalhado:")
        print(f"      PYTHONPATH=. python utils/diagnosticar_dados.py")
        
    else:
        print(f"\n✅ Nenhuma perda de dados detectada!")
    
    print(f"\n{'='*90}\n")
  
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verificar perda de dados entre Parquet e Banco")
    parser.add_argument('--ano', required=True, type=int, help='Ano (ex: 2023)')
    parser.add_argument('--cbo', type=str, help='CBO específico para análise (ex: 521110)')
    args = parser.parse_args()
    
    base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{args.ano}/'
    
    if not os.path.isdir(base_dir):
        print(f"❌ Diretório não encontrado: {base_dir}")
        sys.exit(1)
    
    print(f"\n{'='*90}")
    print(f"🔍 VERIFICAÇÃO DE PERDA DE DADOS")
    print(f"{'='*90}")
    print(f"   Ano: {args.ano}")
    if args.cbo:
        print(f"   CBO: {args.cbo}")
    print(f"{'='*90}")
    
    # 1. Analisa arquivos Parquet
    total_linhas, total_com_cbo, registros_arquivo = analisar_arquivo_parquet(
        base_dir, 
        args.ano, 
        args.cbo
    )
    
    # 2. Analisa banco de dados
    total_banco_ano, total_banco_cbo, registros_banco = analisar_banco(
        args.ano, 
        args.cbo
    )
    
    # 3. Compara resultados
    if args.cbo and registros_arquivo:
        comparar_resultados(registros_arquivo, registros_banco)
    elif not args.cbo:
        print(f"\n{'='*90}")
        print(f"📊 RESUMO COMPARATIVO")
        print(f"{'='*90}\n")
        print(f"   Total no arquivo: {total_linhas:,}")
        print(f"   Total no banco: {total_banco_ano:,}")
        diferenca = total_linhas - total_banco_ano
        print(f"   Diferença: {diferenca:,}")
        
        if diferenca > 0:
            percentual = (diferenca / total_linhas) * 100 if total_linhas > 0 else 0
            print(f"   Perda: {percentual:.2f}%")
        
        print(f"\n   💡 Use --cbo para análise detalhada de um CBO específico")
        print(f"{'='*90}\n")