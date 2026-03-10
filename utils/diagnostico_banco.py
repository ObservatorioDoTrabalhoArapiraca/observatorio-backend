"""
Diagnóstico completo do banco de dados

Uso:
    PYTHONPATH=. python utils/diagnostico_banco.py --ano 2023 --cbo 521110
"""

import os
import sys
import django
import argparse
from pathlib import Path

# Configuração do Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao
from django.db import connection


def diagnostico_completo(ano, cbo_filtro):
    """Faz diagnóstico completo do banco de dados"""
    
    print(f"\n{'='*90}")
    print(f"🔍 DIAGNÓSTICO COMPLETO DO BANCO DE DADOS")
    print(f"{'='*90}\n")
    print(f"Ano: {ano}")
    print(f"CBO: {cbo_filtro}")
    print()
    
    # 1. Via ORM do Django
    print(f"{'='*90}")
    print(f"1️⃣ CONSULTA VIA ORM (Django)")
    print(f"{'='*90}\n")
    
    # Competência como integer: 202301, 202302, etc.
    comp_inicio = int(f"{ano}01")
    comp_fim = int(f"{ano}12")
    
    queryset = Movimentacao.objects.filter(
        competencia_mov__gte=comp_inicio,
        competencia_mov__lte=comp_fim,
        cbo2002_ocupacao_id=str(cbo_filtro)
    )
    
    total_orm = queryset.count()
    print(f"   Total de registros (ORM): {total_orm:,}")
    
    if total_orm > 0:
        print(f"\n   Primeiros 5 registros:")
        for idx, mov in enumerate(queryset[:5], 1):
            print(f"      {idx}. ID: {mov.id} | Comp: {mov.competencia_mov} | CBO: {mov.cbo2002_ocupacao_id}")
    
    # 2. Via SQL Direto
    print(f"\n{'='*90}")
    print(f"2️⃣ CONSULTA VIA SQL DIRETO")
    print(f"{'='*90}\n")
    
    tabela = Movimentacao._meta.db_table
    print(f"   Tabela: {tabela}")
    
    with connection.cursor() as cursor:
        # Conta total
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM {tabela}
            WHERE competencia_mov >= %s 
              AND competencia_mov <= %s
              AND cbo2002_ocupacao_id = %s
        """, [comp_inicio, comp_fim, str(cbo_filtro)])
        
        total_sql = cursor.fetchone()[0]
        print(f"   Total de registros (SQL): {total_sql:,}")
        
        # Mostra alguns exemplos
        if total_sql > 0:
            cursor.execute(f"""
                SELECT id, competencia_mov, cbo2002_ocupacao_id, municipio_id
                FROM {tabela}
                WHERE competencia_mov >= %s 
                  AND competencia_mov <= %s
                  AND cbo2002_ocupacao_id = %s
                LIMIT 5
            """, [comp_inicio, comp_fim, str(cbo_filtro)])
            
            print(f"\n   Primeiros 5 registros:")
            for idx, row in enumerate(cursor.fetchall(), 1):
                print(f"      {idx}. ID: {row[0]} | Comp: {row[1]} | CBO: {row[2]} | Mun: {row[3]}")
    
    # 3. Verificação de formato do CBO
    print(f"\n{'='*90}")
    print(f"3️⃣ VERIFICAÇÃO DO FORMATO DO CBO")
    print(f"{'='*90}\n")
    
    with connection.cursor() as cursor:
        # Busca CBOs similares
        cursor.execute(f"""
            SELECT DISTINCT cbo2002_ocupacao_id, COUNT(*) as total
            FROM {tabela}
            WHERE cbo2002_ocupacao_id LIKE %s
            GROUP BY cbo2002_ocupacao_id
            ORDER BY total DESC
            LIMIT 10
        """, [f"{cbo_filtro[:3]}%"])
        
        cbos_similares = cursor.fetchall()
        
        if cbos_similares:
            print(f"   CBOs que começam com '{cbo_filtro[:3]}':")
            for cbo, total in cbos_similares:
                print(f"      • {cbo}: {total:,} registros")
        else:
            print(f"   ⚠️  Nenhum CBO encontrado começando com '{cbo_filtro[:3]}'")
    
    # 4. Verificação de competências
    print(f"\n{'='*90}")
    print(f"4️⃣ VERIFICAÇÃO DAS COMPETÊNCIAS")
    print(f"{'='*90}\n")
    
    with connection.cursor() as cursor:
        # Todas as competências do ano
        cursor.execute(f"""
            SELECT DISTINCT competencia_mov
            FROM {tabela}
            WHERE competencia_mov >= %s 
              AND competencia_mov <= %s
            ORDER BY competencia_mov
            LIMIT 20
        """, [comp_inicio, comp_fim])
        
        competencias = cursor.fetchall()
        
        if competencias:
            print(f"   Competências disponíveis no ano {ano}:")
            for comp in competencias:
                print(f"      • {comp[0]}")
        else:
            print(f"   ⚠️  Nenhuma competência encontrada para o ano {ano}")
    
    # 5. Verificação cruzada (Competência + CBO)
    print(f"\n{'='*90}")
    print(f"5️⃣ DISTRIBUIÇÃO POR COMPETÊNCIA (CBO {cbo_filtro})")
    print(f"{'='*90}\n")
    
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT competencia_mov, COUNT(*) as total
            FROM {tabela}
            WHERE competencia_mov >= %s 
              AND competencia_mov <= %s
              AND cbo2002_ocupacao_id = %s
            GROUP BY competencia_mov
            ORDER BY competencia_mov
        """, [comp_inicio, comp_fim, str(cbo_filtro)])
        
        distribuicao = cursor.fetchall()
        
        if distribuicao:
            print(f"   Registros por mês:")
            total_distribuicao = 0
            for comp, total in distribuicao:
                print(f"      • {comp}: {total:,} registros")
                total_distribuicao += total
            print(f"\n   TOTAL: {total_distribuicao:,} registros")
        else:
            print(f"   ⚠️  Nenhum registro encontrado")
    
    # 6. Verificação sem filtro de CBO
    print(f"\n{'='*90}")
    print(f"6️⃣ TESTE SEM FILTRO DE CBO")
    print(f"{'='*90}\n")
    
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM {tabela}
            WHERE competencia_mov >= %s 
              AND competencia_mov <= %s
        """, [comp_inicio, comp_fim])
        
        total_sem_filtro = cursor.fetchone()[0]
        print(f"   Total de registros no ano {ano} (sem filtro CBO): {total_sem_filtro:,}")
    
    # 7. Verificação do tipo de dados
    print(f"\n{'='*90}")
    print(f"7️⃣ VERIFICAÇÃO DE TIPOS DE DADOS")
    print(f"{'='*90}\n")
    
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s 
              AND column_name IN ('competencia_mov', 'cbo2002_ocupacao_id')
        """, [tabela])
        
        tipos = cursor.fetchall()
        print(f"   Tipos de dados:")
        for col, tipo in tipos:
            print(f"      • {col}: {tipo}")
    
    # 8. Resumo e diagnóstico
    print(f"\n{'='*90}")
    print(f"📊 RESUMO DO DIAGNÓSTICO")
    print(f"{'='*90}\n")
    
    print(f"   Total via ORM: {total_orm:,}")
    print(f"   Total via SQL: {total_sql:,}")
    print(f"   Total no ano (sem filtro CBO): {total_sem_filtro:,}")
    
    print(f"\n{'='*90}")
    print(f"💡 ANÁLISE")
    print(f"{'='*90}\n")
    
    if total_orm != total_sql:
        print(f"   ⚠️  DISCREPÂNCIA: ORM ({total_orm:,}) ≠ SQL ({total_sql:,})")
        print(f"   Isso pode indicar problema no modelo ou na query do ORM")
    elif total_sql == 0:
        print(f"   ❌ PROBLEMA IDENTIFICADO:")
        print(f"   • Nenhum registro encontrado com CBO {cbo_filtro}")
        print(f"   • Verifique se o CBO está no formato correto")
        print(f"   • Verifique se os dados foram realmente importados")
    elif total_sql < 100:
        print(f"   ⚠️  ATENÇÃO:")
        print(f"   • Apenas {total_sql:,} registros encontrados")
        print(f"   • Esperado: maior quantidade baseado nos arquivos Parquet")
        print(f"   • Possível importação incompleta")
    else:
        print(f"   ✅ Registros encontrados: {total_sql:,}")
        print(f"   Dados parecem corretos!")
    
    print(f"\n{'='*90}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Diagnóstico do banco de dados")
    parser.add_argument('--ano', required=True, type=int, help='Ano (ex: 2023)')
    parser.add_argument('--cbo', required=True, type=str, help='CBO específico (ex: 521110)')
    args = parser.parse_args()
    
    diagnostico_completo(args.ano, args.cbo)