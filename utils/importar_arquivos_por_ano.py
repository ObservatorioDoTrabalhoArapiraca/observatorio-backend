"""
Script de importação detalhada de arquivos TXT por ano

Este script importa todos os arquivos TXT de um ano, linha por linha,
rastrea cada falha e fornece relatório completo ao final.

Uso:
    PYTHONPATH=. python utils/importar_arquivos_por_ano.py --ano 2024 --limit 10

    # PYTHONPATH=. python utils/importar_arquivos_por_ano.py --ano 2021 > saida_importacao2021.txt 2>&1

   pra ver o que tá no arquivo de saída, abre outro terminal e digita: tail -f saida_importacao2021.txt
   
   # baixar dump do banco (se precisar):
   PGPASSWORD="npg_5wsWAPueiI7E" pg_dump -h ep-snowy-resonance-acq0bh49-pooler.sa-east-1.aws.neon.tech -U neondb_owner -d neondb -F c -f dump.sql --no-password
"""
import os
import sys
import django
import time
import argparse
from pathlib import Path
from decimal import Decimal, InvalidOperation
from django import db

# --- SETUP DJANGO ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao

# --- MAPEAMENTO ---
MAPEAMENTO_COLUNAS = {
    'competencia_mov': ['competênciamov'],
    'regiao_id': ['região'],
    'uf_id': ['uf'],
    'municipio_id': ['município'],
    'secao_id': ['seção'],
    'subclasse_id': ['subclasse'],
    'saldo_movimentacao': ['saldomovimentação'],
    'cbo2002_ocupacao_id': ['cbo2002ocupação'],
    'categoria_id': ['categoria'],
    'grau_instrucao_id': ['graudeinstrução'],
    'idade': ['idade'],
    'horas_contratuais': ['horascontratuais'],
    'raca_cor_id': ['raçacor'],
    'sexo_id': ['sexo'],
    'tipo_empregador_id': ['tipoempregador'],
    'tipo_estabelecimento_id': ['tipoestabelecimento'],
    'tipo_movimentacao_id': ['tipomovimentação'],
    'tipo_deficiencia_id': ['tipodedeficiência'],
    'ind_trab_intermitente_id': ['indtrabintermitente'],
    'ind_trab_parcial_id': ['indtrabparcial'],
    'salario': ['salário'],
    'tam_estab_jan_id': ['tamestabjan'],
    'indicador_aprendiz_id': ['indicadoraprendiz'],
    'origem_informacao_id': ['origemdainformação'],
    'competencia_dec': ['competênciadec'],
    'competencia_exc': ['competênciaexc'],
    'indicador_exclusao_id': ['indicadordeexclusão'],
    'indicador_fora_prazo_id': ['indicadordeforadoprazo'],
    'unidade_salario_codigo_id': ['unidadesaláriocódigo'],
    'valor_salario_fixo': ['valorsaláriofixo'],
}

def limpar_valor(valor):
    if valor is None: return None
    v = str(valor).replace('“', '').replace('”', '').replace('"', '').replace("'", "").strip()
    if v.upper() in ['', 'NA', 'NULL', 'NAN']: return None
    return v

def processar_linha_caged(row_dict):
    dados_finais = {'salario': Decimal('0.00'), 'valor_salario_fixo': Decimal('0.00'), 'horas_contratuais': 0, 'idade': 0}
    txt_normalizado = {k.strip().lower(): v for k, v in row_dict.items()}
    for campo_banco, nomes_possiveis in MAPEAMENTO_COLUNAS.items():
        valor_bruto = None
        for nome in nomes_possiveis:
            if nome in txt_normalizado:
                valor_bruto = limpar_valor(txt_normalizado[nome])
                break
        if valor_bruto is None: continue
        try:
            if campo_banco in ['salario', 'valor_salario_fixo']:
                v = valor_bruto.replace(',', '.')
                dados_finais[campo_banco] = Decimal(v)
            elif campo_banco.startswith('ind_') or campo_banco in ['idade', 'horas_contratuais', 'saldo_movimentacao', 'competencia_mov', 'competencia_exc', 'indicador_exclusao_id']:
                v_base = valor_bruto.split(',')[0].split('.')[0]
                dados_finais[campo_banco] = int(v_base)
            else:
                dados_finais[campo_banco] = valor_bruto
        except: continue
    return dados_finais

# --- FUNÇÕES DE IMPORTAÇÃO ---

def importar_arquivo_txt(caminho_arquivo, limit=None, lote_tamanho=1000):
    try:
        try:
            f = open(caminho_arquivo, 'r', encoding='utf-8')
            header_line = f.readline()
        except UnicodeDecodeError:
            f = open(caminho_arquivo, 'r', encoding='latin-1')
            header_line = f.readline()

        header = [h.strip().lower() for h in header_line.strip().split(';')]
        batch = []
        cont_sucesso = 0
        cont_erro = 0
        
        print(f"📄 Arquivo: {os.path.basename(caminho_arquivo)}")

        for i, linha_texto in enumerate(f, 1):
            if limit and cont_sucesso >= limit: break
            try:
                campos = linha_texto.strip().split(';')
                if len(campos) < len(header): continue
                row_dict = dict(zip(header, campos))
                dados = processar_linha_caged(row_dict)
                batch.append(Movimentacao(**dados))
                cont_sucesso += 1

                if i % 500 == 0:
                    print(f"   ⏳ Lendo linha {i}...")

                if len(batch) >= lote_tamanho:
                    try:
                        Movimentacao.objects.bulk_create(batch)
                        print(f"   📦 [LOTE OK] {cont_sucesso} registros salvos.")
                    except Exception as e_bulk:
                        cont_erro += len(batch)
                        print(f"   ❌ ERRO NO LOTE (Linhas {i-lote_tamanho+1} até {i}): O lote foi descartado devido a um erro de integridade (ex: CBO inválido).")
                        # Opcional: print(f"   Detalhe do erro: {e_bulk}")
                    
                    # ESSENCIAL: Limpa o batch SEMPRE, mesmo se deu erro
                    batch = []
                    db.reset_queries()
            except Exception as e_linha:
                cont_erro += 1
                print(f"   ❌ ERRO NA LINHA {i}: {e_linha}")
        
        if batch:
            Movimentacao.objects.bulk_create(batch)
        f.close()
        return cont_sucesso, cont_erro
    except Exception as e:
        print(f"🚨 Erro fatal no arquivo: {e}")
        return 0, 0

def importar_todos_os_arquivos_do_ano(ano, limit=None):
    base_dir = f'/home/charlie/Documentos/NOVO CAGED/{ano}'
    if not os.path.exists(base_dir):
        print(f"❌ Pasta do ano {ano} não encontrada!")
        return

    print(f"Início do script: {time.strftime('%H:%M:%S')}")
    total_geral_sucesso = 0
    total_geral_erro = 0
    total_banco_antes = Movimentacao.objects.count()

    for pasta in sorted(os.listdir(base_dir)):
        pasta_path = os.path.join(base_dir, pasta)
        if not os.path.isdir(pasta_path): continue
        for arquivo in sorted(os.listdir(pasta_path)):
            if arquivo.endswith('.txt'):
                caminho_arquivo = os.path.join(pasta_path, arquivo)
                # CHAMADA CORRIGIDA ABAIXO:
                sucesso, erro = importar_arquivo_txt(caminho_arquivo, limit=limit)
                total_geral_sucesso += sucesso
                total_geral_erro += erro
                db.connections.close_all()

    total_banco_depois = Movimentacao.objects.count()
    print(f"\n🏆 FIM: {time.strftime('%H:%M:%S')} | SUCESSO: {total_geral_sucesso:,} | ERROS: {total_geral_erro:,}")
    print(f"📊 BANCO: {total_banco_antes:,} -> {total_banco_depois:,}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ano', required=True)
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()
    importar_todos_os_arquivos_do_ano(args.ano, args.limit)