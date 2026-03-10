"""
Investiga por que registros específicos estão sendo perdidos na importação

Uso:
    PYTHONPATH=. python utils/investigar_registros_perdidos.py --ano 2023 --cbo 521110
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


def analisar_registros_perdidos(base_dir, ano, cbo_filtro):
    """Analisa detalhadamente os registros que não foram importados"""
    print(f"\n{'='*90}")
    print(f"🔍 INVESTIGAÇÃO DE REGISTROS PERDIDOS")
    print(f"{'='*90}\n")
    
    registros_arquivo = []
    
    # 1. Coleta TODOS os registros do arquivo
    print("📂 Coletando registros dos arquivos Parquet...")
    for root, dirs, files in os.walk(base_dir):
        for arquivo in sorted(files):
            if arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
                caminho = os.path.join(root, arquivo)
                
                try:
                    df = pd.read_parquet(caminho)
                    
                    # Identifica coluna CBO
                    coluna_cbo = None
                    for col in df.columns:
                        if 'cbo' in col.lower():
                            coluna_cbo = col
                            break
                    
                    if not coluna_cbo:
                        continue
                    
                    # Identifica coluna competência
                    coluna_comp = None
                    for col in df.columns:
                        if 'compet' in col.lower():
                            coluna_comp = col
                            break
                    
                    # Filtra por CBO
                    df_filtrado = df[
                        (df[coluna_cbo].astype(str) == str(cbo_filtro)) |
                        (df[coluna_cbo].astype(str).str.replace('-', '') == str(cbo_filtro))
                    ]
                    
                    if len(df_filtrado) > 0:
                        print(f"   ✓ {arquivo}: {len(df_filtrado)} registros")
                        
                        for idx, row in df_filtrado.iterrows():
                            comp = row.get(coluna_comp)
                            if comp:
                                comp_str = str(int(comp)) if isinstance(comp, float) else str(comp)
                                comp_formatada = comp_str.zfill(6)
                                
                                # Armazena registro
                                registros_arquivo.append({
                                    'arquivo': arquivo,
                                    'linha': idx + 1,
                                    'competencia': comp_formatada,
                                    'dados': dict(row)
                                })
                
                except Exception as e:
                    print(f"   ❌ Erro em {arquivo}: {e}")
    
    print(f"\n   Total de registros coletados: {len(registros_arquivo)}\n")
    
    # 2. Verifica quais estão no banco
    print("💾 Verificando quais registros estão no banco...")
    registros_no_banco = set()
    
    for reg in registros_arquivo:
        comp = reg['competencia']
        
        # Tenta encontrar o registro no banco (usando campos chave)
        existe = Movimentacao.objects.filter(
            competencia_movimentacao=comp,
            cbo2002_ocupacao_id=str(cbo_filtro)
        ).exists()
        
        if existe:
            registros_no_banco.add((comp, reg['arquivo'], reg['linha']))
    
    print(f"   Registros encontrados no banco: {len(registros_no_banco)}\n")
    
    # 3. Identifica registros perdidos
    registros_perdidos = []
    for reg in registros_arquivo:
        chave = (reg['competencia'], reg['arquivo'], reg['linha'])
        if chave not in registros_no_banco:
            registros_perdidos.append(reg)
    
    print(f"{'='*90}")
    print(f"❌ REGISTROS PERDIDOS: {len(registros_perdidos)}")
    print(f"{'='*90}\n")
    
    if not registros_perdidos:
        print("✅ Todos os registros foram importados com sucesso!\n")
        return
    
    # 4. Analisa os registros perdidos
    print("🔬 ANÁLISE DETALHADA DOS REGISTROS PERDIDOS:\n")
    
    problemas = {
        'municipio_vazio': [],
        'cpf_invalido': [],
        'salario_invalido': [],
        'campos_obrigatorios_vazios': [],
        'outros': []
    }
    
    for idx, reg in enumerate(registros_perdidos[:50], 1):  # Analisa até 50
        dados = reg['dados']
        problemas_registro = []
        
        print(f"{idx}. Arquivo: {reg['arquivo']} | Linha: {reg['linha']} | Comp: {reg['competencia']}")
        
        # Verifica município
        municipio = dados.get('município', dados.get('municipio', None))
        if pd.isna(municipio) or str(municipio).strip() == '':
            problemas_registro.append("município vazio")
            problemas['municipio_vazio'].append(reg)
        else:
            print(f"   Município: {municipio}")
        
        # Verifica CPF
        cpf = dados.get('cpf', None)
        if pd.isna(cpf) or str(cpf).strip() == '':
            problemas_registro.append("CPF vazio")
            problemas['cpf_invalido'].append(reg)
        else:
            print(f"   CPF: {str(cpf)[:6]}***")
        
        # Verifica salário
        salario = dados.get('saldomovimentação', dados.get('salario', None))
        if pd.isna(salario):
            problemas_registro.append("salário vazio")
            problemas['salario_invalido'].append(reg)
        else:
            try:
                sal_float = float(salario)
                print(f"   Salário: R$ {sal_float:.2f}")
            except:
                problemas_registro.append("salário inválido")
                problemas['salario_invalido'].append(reg)
        
        # Verifica outros campos
        campos_verificar = ['região', 'uf', 'sexo']
        for campo in campos_verificar:
            valor = dados.get(campo)
            if pd.isna(valor) or str(valor).strip() == '':
                problemas_registro.append(f"{campo} vazio")
                problemas['campos_obrigatorios_vazios'].append(reg)
        
        if problemas_registro:
            print(f"   ⚠️  Problemas: {', '.join(problemas_registro)}")
        else:
            print(f"   ❓ Sem problemas óbvios identificados")
            problemas['outros'].append(reg)
            
            # Mostra todos os campos para investigação
            print(f"   📋 Campos do registro:")
            for campo, valor in dados.items():
                if not pd.isna(valor):
                    print(f"      • {campo}: {valor}")
        
        print()
    
    if len(registros_perdidos) > 50:
        print(f"... e mais {len(registros_perdidos) - 50} registros não exibidos\n")
    
    # 5. Resumo dos problemas
    print(f"{'='*90}")
    print(f"📊 RESUMO DOS PROBLEMAS IDENTIFICADOS")
    print(f"{'='*90}\n")
    
    for tipo, lista in problemas.items():
        if lista:
            print(f"   • {tipo.replace('_', ' ').title()}: {len(lista)} registros")
    
    print(f"\n{'='*90}")
    print(f"💡 PRÓXIMOS PASSOS")
    print(f"{'='*90}\n")
    print(f"1. Se há muitos campos vazios:")
    print(f"   → Ajuste as validações no script de importação")
    print(f"   → Permita valores NULL onde apropriado")
    print(f"\n2. Se os dados parecem válidos:")
    print(f"   → Verifique transações no banco")
    print(f"   → Execute importação com verbose para ver erros")
    print(f"\n3. Para reimportar apenas os perdidos:")
    print(f"   → Use o script de importação mês a mês")
    print(f"   → PYTHONPATH=. python utils/importar_mes_a_mes.py --ano {ano} --mes 1")
    print(f"\n{'='*90}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Investigar registros perdidos")
    parser.add_argument('--ano', required=True, type=int, help='Ano (ex: 2023)')
    parser.add_argument('--cbo', required=True, type=str, help='CBO específico (ex: 521110)')
    args = parser.parse_args()
    
    base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{args.ano}/'
    
    if not os.path.isdir(base_dir):
        print(f"❌ Diretório não encontrado: {base_dir}")
        sys.exit(1)
    
    analisar_registros_perdidos(base_dir, args.ano, args.cbo)