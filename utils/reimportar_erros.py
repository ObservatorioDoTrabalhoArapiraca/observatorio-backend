"""
Script para reimportar apenas registros que falharam na importação anterior.

Uso:
    PYTHONPATH=. python utils/reimportar_erros.py --ano 2023
    PYTHONPATH=. python utils/reimportar_erros.py --ano 2023 --mes 01
    PYTHONPATH=. python utils/reimportar_erros.py --ano 2023 --arquivo CAGEDMOV202301-Al-Arapiraca_filtrado.parquet
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


def limpar_numero(valor):
    """Converte string com vírgula em número float."""
    if valor is None or pd.isna(valor):
        return None

    if isinstance(valor, (int, float)):
        return float(valor)

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

        try:
            codigo = int(codigo)
        except (ValueError, TypeError):
            pass

        return model.objects.filter(codigo=codigo).first()

    except Exception:
        return None


def registro_ja_existe(competencia, municipio_codigo, cbo_codigo, idade, salario, saldo):
    """
    Verifica se um registro já existe no banco.
    Usa os campos principais como identificador único.
    """
    try:
        filtro = {'competencia_movimentacao': competencia}
        
        # Adiciona filtros opcionais
        if municipio_codigo:
            municipio = MunicipioReferencia.objects.filter(codigo=municipio_codigo).first()
            if municipio:
                filtro['municipio'] = municipio
        
        if cbo_codigo:
            cbo = Cbo2002ocupacaoReferencia.objects.filter(codigo=cbo_codigo).first()
            if cbo:
                filtro['cbo2002_ocupacao'] = cbo
        
        if idade is not None:
            filtro['idade'] = int(idade) if idade else None
            
        if salario is not None:
            filtro['salario'] = salario
            
        if saldo is not None:
            filtro['saldo_movimentacao'] = saldo
        
        return Movimentacao.objects.filter(**filtro).exists()
        
    except Exception:
        return False


def identificar_registros_faltantes(caminho_arquivo):
    """
    Compara registros do arquivo com o banco e identifica quais faltam.
    Retorna DataFrame apenas com registros não importados.
    """
    print(f"\n🔍 Analisando: {os.path.basename(caminho_arquivo)}")
    
    try:
        # Carrega o arquivo
        df = pd.read_parquet(caminho_arquivo)
        total_arquivo = len(df)
        print(f"  📁 Total no arquivo: {total_arquivo}")
        
        # Identifica registros faltantes
        registros_faltantes = []
        
        for idx, row in df.iterrows():
            if idx > 0 and idx % 100 == 0:
                print(f"      Verificando {idx}/{total_arquivo}...")
            
            competencia = row.get('competênciamov')
            municipio_codigo = row.get('município')
            cbo_codigo = row.get('cbo2002ocupação')
            idade = limpar_numero(row.get('idade'))
            salario = limpar_numero(row.get('salário'))
            saldo = row.get('saldomovimentação')
            
            # Converte saldo
            if pd.notna(saldo):
                try:
                    saldo = int(float(saldo))
                except (ValueError, TypeError):
                    saldo = None
            else:
                saldo = None
            
            # Verifica se já existe
            if not registro_ja_existe(competencia, municipio_codigo, cbo_codigo, idade, salario, saldo):
                registros_faltantes.append(idx)
        
        if not registros_faltantes:
            print(f"  ✅ Todos os registros já foram importados!")
            return None
        
        df_faltantes = df.iloc[registros_faltantes]
        print(f"  ⚠️  Faltam {len(df_faltantes)} registros de {total_arquivo} ({len(df_faltantes)/total_arquivo*100:.1f}%)")
        
        return df_faltantes
        
    except Exception as e:
        print(f"  ❌ Erro ao analisar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return None


def importar_registros_faltantes(df, nome_arquivo):
    """
    Importa apenas os registros que ainda não estão no banco.
    """
    print(f"\n📥 Importando {len(df)} registros faltantes...")
    
    registros_importados = 0
    registros_com_erro = 0
    erros_detalhados = []
    
    total = len(df)
    
    for contador, (idx, row) in enumerate(df.iterrows(), start=1):
        try:
            with transaction.atomic():
                if contador > 0 and contador % 10 == 0:
                     print(f"      📝 Progresso: {contador}/{total}...")
                
                # Busca referências
                municipio = get_referencia(MunicipioReferencia, row.get('município'))
                cbo = get_referencia(Cbo2002ocupacaoReferencia, row.get('cbo2002ocupação'))
                grau_instrucao = get_referencia(GraudeinstrucaoReferencia, row.get('graudeinstrução'))
                raca_cor = get_referencia(RacaCorReferencia, row.get('raçacor'))
                sexo = get_referencia(SexoReferencia, row.get('sexo'))
                tipo_deficiencia = get_referencia(TipoDeficienciaReferencia, row.get('tipodedeficiência'))
                
                # Limpa campos
                salario = limpar_numero(row.get('salário'))
                idade = limpar_numero(row.get('idade'))
                saldo_movimentacao = row.get('saldomovimentação')
                
                if pd.notna(saldo_movimentacao):
                    try:
                        saldo_movimentacao = int(float(saldo_movimentacao))
                    except (ValueError, TypeError):
                        saldo_movimentacao = None
                else:
                    saldo_movimentacao = None
                
                if idade is not None:
                    idade = int(idade)
                
                # Cria registro
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
                registros_importados += 1
                
        except Exception as e:
            registros_com_erro += 1
            
            import traceback
            erro_info = {
                'arquivo': nome_arquivo,
                'linha': idx + 1,
                'tipo_erro': type(e).__name__,
                'mensagem': str(e),
                'traceback': traceback.format_exc(),
                'dados': {
                    'competencia': row.get('competênciamov'),
                    'municipio': row.get('município'),
                    'cbo': row.get('cbo2002ocupação'),
                }
            }
            erros_detalhados.append(erro_info)
    
    print(f"\n  {'='*50}")
    print(f"  ✅ Importados: {registros_importados}/{total}")
    print(f"  ❌ Erros: {registros_com_erro}")
    print(f"  {'='*50}")
    
    return registros_importados, erros_detalhados


def processar_arquivo(caminho_arquivo):
    """Identifica e importa registros faltantes de um arquivo."""
    nome_arquivo = os.path.basename(caminho_arquivo)
    
    # Identifica registros faltantes
    df_faltantes = identificar_registros_faltantes(caminho_arquivo)
    
    if df_faltantes is None or len(df_faltantes) == 0:
        return 0, []
    
    # Importa apenas os faltantes
    importados, erros = importar_registros_faltantes(df_faltantes, nome_arquivo)
    
    return importados, erros


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reimportar registros que falharam")
    parser.add_argument('--ano', required=True, help='Ano (ex: 2023)')
    parser.add_argument('--mes', help='Mês específico (ex: 01)')
    parser.add_argument('--arquivo', help='Nome específico do arquivo')
    args = parser.parse_args()
    
    base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{args.ano}/'
    
    if not os.path.isdir(base_dir):
        print(f"❌ Diretório não encontrado: {base_dir}")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"🔄 REIMPORTAÇÃO DE REGISTROS FALTANTES")
    print(f"{'='*60}")
    print(f"📂 Diretório: {base_dir}")
    print(f"📅 Ano: {args.ano}")
    if args.mes:
        print(f"📆 Mês: {args.mes}")
    if args.arquivo:
        print(f"📄 Arquivo: {args.arquivo}")
    print(f"{'='*60}")
    
    # Busca arquivos
    arquivos_encontrados = []
    
    if args.arquivo:
        # Arquivo específico
        caminho = os.path.join(base_dir, args.arquivo)
        if os.path.isfile(caminho):
            arquivos_encontrados.append(caminho)
        else:
            # Busca recursivamente
            for root, dirs, files in os.walk(base_dir):
                if args.arquivo in files:
                    arquivos_encontrados.append(os.path.join(root, args.arquivo))
    else:
        # Busca todos os arquivos
        for root, dirs, files in os.walk(base_dir):
            for arquivo in sorted(files):
                if arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
                    if args.mes:
                        partes = arquivo.split('-')[0]
                        if len(partes) >= 8:
                            mes_no_arquivo = partes[-2:]
                            if mes_no_arquivo != args.mes:
                                continue
                    
                    arquivos_encontrados.append(os.path.join(root, arquivo))
    
    if not arquivos_encontrados:
        print(f"\n⚠️  Nenhum arquivo encontrado!")
        sys.exit(1)
    
    print(f"\n✓ Encontrados {len(arquivos_encontrados)} arquivo(s)\n")
    
    # Processa cada arquivo
    total_importados = 0
    todos_erros = []
    
    for caminho in arquivos_encontrados:
        try:
            importados, erros = processar_arquivo(caminho)
            total_importados += importados
            todos_erros.extend(erros)
        except Exception as e:
            print(f"\n❌ Erro ao processar arquivo: {e}")
            import traceback
            traceback.print_exc()
        finally:
            gc.collect()
    
    # Resumo final
    print(f"\n{'='*60}")
    print(f"📊 RESUMO FINAL")
    print(f"{'='*60}")
    print(f"   ✅ Total de registros importados: {total_importados}")
    print(f"   ❌ Total de erros: {len(todos_erros)}")
    print(f"{'='*60}")
    
    # Mostra erros detalhados
    if todos_erros:
        print(f"\n{'='*60}")
        print(f"❌ DETALHES DOS ERROS")
        print(f"{'='*60}")
        
        for idx, erro in enumerate(todos_erros[:10], 1):
            print(f"\n{idx}. {erro.get('tipo_erro')}")
            print(f"   Arquivo: {erro.get('arquivo')}")
            print(f"   Linha: {erro.get('linha')}")
            print(f"   Mensagem: {erro.get('mensagem')}")
            print(f"   Dados: {erro.get('dados')}")
        
        if len(todos_erros) > 10:
            print(f"\n... e mais {len(todos_erros) - 10} erros")
        
        print(f"\n{'='*60}\n")
    else:
        print(f"\n✅ Todos os registros foram importados com sucesso!\n")