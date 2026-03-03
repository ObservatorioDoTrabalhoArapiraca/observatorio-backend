# TODO: ver se é possível adicionar todos os dados lá no banco de dados. Criar um script que faça o calculo de quantos md os arquivos parquet tem e depois tentar importar um ano inteiro pra ver quanto 1 ano vai consumir (pegar um ano grande 2022 ou 2023 para o teste) o db tem 0,5GB e só usamos 0,03gb. tem que limpar as tabelas que não estão sendo usadas e depois importar os dados.

# TODO: colcoar as alterações no documento do estagio

# IDADE

# PYTHONPATH=. python utils/importar_parquet_para_db.py --ano 2020
# PYTHONPATH=. python utils/importar_parquet_para_db.py --ano 2020 --mes 01

# Escolaridade



# 1. Delete
# python manage.py shell

# from apps.movimentacoes.models import Movimentacao
# Movimentacao.objects.all().delete()
# exit()

# 2. Reimporte
# PYTHONPATH=. python utils/importar_parquet_para_db.py --ano 2020 --mes 01

import os
import sys
import django
import argparse
import pandas as pd
import gc 
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import transaction
from apps.referenciais.models import (
    RegiaoReferencia, SecaoReferencia, UfReferencia,
    MunicipioReferencia, SubclasseReferencia, CategoriaReferencia,
    Cbo2002ocupacaoReferencia, GraudeinstrucaoReferencia, RacaCorReferencia,
    SexoReferencia, TipoEmpregadorReferencia, TipoEstabelecimentoReferencia,
    TipoMovimentacaoReferencia, TipoDeficienciaReferencia,
) 
from apps.movimentacoes.models import Movimentacao

LIMITE_LINHAS = 2

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
    """
    Busca um registro na tabela de referência.
    """
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
            print(f"  ⚠️  {model.__name__} código '{codigo}' não encontrado")
        
        return obj
        
    except Exception as e:
        print(f"  ❌ Erro ao buscar {model.__name__} código {codigo}: {e}")
        return None

def processar_movimentacao(df):
    """Processa e salva dados de movimentação (CAGEDMOV)"""
    print(f"  📊 Processando {len(df)} registros de movimentação...")
    
    registros_processados = 0
    registros_com_erro = 0
    
    for idx, row in df.iterrows():
        try:
            with transaction.atomic():
                print(f"\n  📝 Processando registro {idx + 1}/{len(df)}:")
                
                # Mostra valores
                print(f"     competênciamov: {row.get('competênciamov')}")
                print(f"     município: {row.get('município')}")
                print(f"     salário: {row.get('salário')}")
                print(f"     idade: {row.get('idade')}")
                print(f"     horas: {row.get('horascontratuais')}")
                
                
                # Busca referências
                regiao = get_referencia(RegiaoReferencia, row.get('região'))
                uf = get_referencia(UfReferencia, row.get('uf'))
                municipio = get_referencia(MunicipioReferencia, row.get('município'))
                secao = get_referencia(SecaoReferencia, row.get('seção'))
                subclasse = get_referencia(SubclasseReferencia, row.get('subclasse'))
                cbo = get_referencia(Cbo2002ocupacaoReferencia, row.get('cbo2002ocupação'))
                categoria = get_referencia(CategoriaReferencia, row.get('categoria'))
                grau_instrucao = get_referencia(GraudeinstrucaoReferencia, row.get('graudeinstrução'))
                raca_cor = get_referencia(RacaCorReferencia, row.get('raçacor'))
                sexo = get_referencia(SexoReferencia, row.get('sexo'))
                tipo_empregador = get_referencia(TipoEmpregadorReferencia, row.get('tipoempregador'))
                tipo_estabelecimento = get_referencia(TipoEstabelecimentoReferencia, row.get('tipoestabelecimento'))
                tipo_movimentacao = get_referencia(TipoMovimentacaoReferencia, row.get('tipomovimentação'))
                tipo_deficiencia = get_referencia(TipoDeficienciaReferencia, row.get('tipodedeficiência'))
                
                # ✅ Limpa os campos numéricos
                salario = limpar_numero(row.get('salário'))
                horas_contratuais = limpar_numero(row.get('horascontratuais'))
                idade = limpar_numero(row.get('idade'))
                tam_estab = limpar_numero(row.get('tamestabjan'))
                saldo_mov = limpar_numero(row.get('saldomovimentação'))
                
                # Converte para inteiro quando necessário
                if idade is not None:
                    idade = int(idade)
                if horas_contratuais is not None:
                    horas_contratuais = int(horas_contratuais)
                if tam_estab is not None:
                    tam_estab = int(tam_estab)
                if saldo_mov is not None:
                    saldo_mov = int(saldo_mov)
                
                print(f"     salário limpo: {salario}")
                print(f"     horas limpas: {horas_contratuais}")
                
                # Cria o objeto
                movimentacao = Movimentacao(
                    competencia_movimentacao=row.get('competênciamov'),
                    regiao=regiao,
                    uf=uf,
                    municipio=municipio,
                    secao=secao,
                    subclasse=subclasse,
                    saldo_movimentacao=saldo_mov,
                    cbo2002_ocupacao=cbo,
                    categoria=categoria,
                    grau_instrucao=grau_instrucao,
                    idade=idade,
                    horas_contratuais=horas_contratuais,
                    raca_cor=raca_cor,
                    sexo=sexo,
                    tipo_empregador=tipo_empregador,
                    tipo_estabelecimento=tipo_estabelecimento,
                    tipo_movimentacao=tipo_movimentacao,
                    tipo_deficiencia=tipo_deficiencia,
                    indicador_trabalho_intermitente=row.get('indtrabintermitente'),
                    indicador_trabalho_parcial=row.get('indtrabparcial'),
                    salario=salario,
                    tamanho_estabelecimento=tam_estab,
                    indicador_aprendiz=row.get('indicadoraprendiz'),
                    origem_informacao=row.get('origemdainformação'),
                )
                
                movimentacao.save()
                
                registros_processados += 1
                print(f"  ✅ Registro {idx + 1} salvo com ID: {movimentacao.id}")
                print(f"     Grau Instrução: {movimentacao.grau_instrucao}")
            
        except Exception as e:
            registros_com_erro += 1
            print(f"\n  ❌ ERRO ao processar linha {idx + 1}:")
            print(f"     Mensagem: {e}")
            if registros_com_erro <= 3:
                import traceback
                traceback.print_exc()
    
    print(f"\n  {'='*50}")
    print(f"  ✅ Total processado: {registros_processados}")
    print(f"  ⚠️  Erros: {registros_com_erro}")
    print(f"  {'='*50}")
    return registros_processados

def importar_parquet(caminho_arquivo):
    """Importa arquivo Parquet filtrado para o banco de dados"""
    print(f"\n→ Processando: {os.path.basename(caminho_arquivo)}")
    
    try:
        df = pd.read_parquet(caminho_arquivo)
        print(f"  📁 Total de registros no arquivo: {len(df)}")
        
        df = df.head(LIMITE_LINHAS)
        print(f"  🔢 Limitado a: {len(df)} linhas")
        
        if len(df) == 0:
            print(f"  ⚠️  Arquivo vazio, pulando...")
            return False
        
        print(f"  📋 Colunas: {list(df.columns)[:5]}...")
        
        # ✅ SEM transaction.atomic() aqui - cada registro tem sua própria transação
        processar_movimentacao(df)
        
        print(f"  ✓ Arquivo importado com sucesso!")
        return True
        
    except Exception as e:
        print(f"  ✗ Erro ao importar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        gc.collect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importar movimentações (CAGEDMOV) de Arapiraca")
    parser.add_argument('--ano', required=True, help='Ano a ser processado (ex: 2020)')
    parser.add_argument('--mes', help='Mês específico (opcional, ex: 01)')
    args = parser.parse_args()
    
    base_dir = f'/home/usuario/Github/NOVO CAGED/{args.ano}/'
    
    if not os.path.isdir(base_dir):
        print(f"❌ Diretório não encontrado: {base_dir}")
        sys.exit(1)
    
    total_importados = 0
    total_erros = 0
    arquivos_encontrados = []
    
    print(f"\n{'='*60}")
    print(f"🔍 Buscando arquivos CAGEDMOV*-Al-Arapiraca_filtrado.parquet")
    print(f"📂 Diretório base: {base_dir}")
    print(f"🔢 Limite de linhas: {LIMITE_LINHAS}")
    print(f"{'='*60}")
    
    for root, dirs, files in os.walk(base_dir):
        for arquivo in sorted(files):
            if arquivo.startswith('CAGEDMOV') and arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
                if args.mes:
                    mes_no_arquivo = arquivo.replace('CAGEDMOV', '').split('-')[0]
                    if not mes_no_arquivo.endswith(args.mes):
                        continue
                
                caminho_completo = os.path.join(root, arquivo)
                arquivos_encontrados.append(caminho_completo)
    
    if not arquivos_encontrados:
        print(f"\n⚠️  Nenhum arquivo CAGEDMOV filtrado encontrado!")
        if args.mes:
            print(f"   Mês especificado: {args.mes}")
        sys.exit(1)
    
    print(f"\n✓ Encontrados {len(arquivos_encontrados)} arquivo(s)\n")
    
    for caminho_completo in arquivos_encontrados:
        if importar_parquet(caminho_completo):
            total_importados += 1
        else:
            total_erros += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Resumo da importação:")
    print(f"   ✅ Arquivos importados: {total_importados}")
    print(f"   ❌ Erros: {total_erros}")
    print(f"   📦 Total de linhas processadas: {total_importados * LIMITE_LINHAS}")
    print(f"{'='*60}\n")