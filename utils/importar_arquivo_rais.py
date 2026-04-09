# PYTHONPATH=. python utils/importar_rais_por_ano.py --arquivo /home/charlie/Documentos/RAIS/2022/RAIS_VINC_PUB_ARAPIRACA.txt --ano 2022

import os
import sys
import django
import time
import argparse
from pathlib import Path
from decimal import Decimal
from django import db

# --- SETUP DJANGO ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoesrais.models import MovimentacaoRais

# --- MAPEAMENTO RAIS 

MAPEAMENTO_RAIS = {
    # --- LOCALIZAÇÃO ---
    'bairros_sp': ['bairros sp', 'bairro sp'],
    'bairros_fortaleza': ['bairros fortaleza'],
    'bairros_rj': ['bairros rj'],
    'distritos_sp': ['distritos sp'],
    'regioes_adm_df': ['regiões adm df', 'regiao adm df'],
    'mun_trab': ['município', 'municipio', 'mun trab'],
    'municipio': ['município', 'municipio'],

    # --- ATIVIDADE ---
    'cbo_ocupacao_2002': ['cbo ocupação 2002', 'cbo 2002 ocupação', 'cbo2002 ocupação'],
    'cnae_2_0_classe': ['cnae 2.0 classe'],
    'cnae_95_classe': ['cnae 95 classe'],
    'cnae_2_0_subclasse': ['cnae 2.0 subclasse'],
    'ibge_subsetor': ['ibge subsetor'],
    'natureza_juridica': ['natureza jurídica', 'natureza juridica'],

    # --- TRABALHADOR ---
    'idade': ['idade'],
    'faixa_etaria': ['faixa etária', 'faixa etaria'],
    'sexo_trabalhador': ['sexo trabalhador'],
    'raca_cor': ['raça cor', 'raca cor'],
    'escolaridade_apos_2005': ['escolaridade após 2005', 'instrução', 'grau instrução'],
    'nacionalidade': ['nacionalidade'],
    'ind_portador_defic': ['ind portador defic'],
    'tipo_defic': ['tipo defic', 'tipo deficiência'],
    'ano_chegada_brasil': ['ano chegada brasil'],

    # --- VÍNCULO ---
    'vinculo_ativo_31_12': ['vínculo ativo 31/12', 'vinculo ativo 31/12'],
    'faixa_hora_contrat': ['faixa hora contrat'],
    'qtd_hora_contr': ['qtd hora contr'],
    'faixa_tempo_emprego': ['faixa tempo emprego'],
    'tempo_emprego': ['tempo emprego'],
    'tipo_admissao': ['tipo admissão', 'tipo admissao'],
    'tipo_estab': ['tipo estab'],
    'tipo_estab_1': ['tipo estab.1'],
    'tipo_vinculo': ['tipo vínculo', 'tipo vinculo'],
    'tamanho_estabelecimento': ['tamanho estabelecimento'],
    'ind_cei_vinculado': ['ind cei vinculado'],
    'ind_simples': ['ind simples'],
    'ind_trab_intermitente': ['ind trab intermitente'],
    'ind_trab_parcial': ['ind trab parcial'],

    # --- MOVIMENTAÇÃO ---
    'causa_afastamento_1': ['causa afastamento 1'],
    'causa_afastamento_2': ['causa afastamento 2'],
    'causa_afastamento_3': ['causa afastamento 3'],
    'motivo_desligamento': ['motivo desligamento'],
    'mes_admissao': ['mês admissão', 'mes admissao'],
    'mes_desligamento': ['mês desligamento', 'mes desligamento'],
    'qtd_dias_afastamento': ['qtd dias afastamento'],

    # --- REMUNERAÇÕES ANUAIS ---
    'vl_remun_dezembro_nom': ['vl remun dezembro nom'],
    'vl_remun_dezembro_sm': ['vl remun dezembro (sm)'],
    'vl_remun_media_nom': ['vl remun média nom', 'vl remun media nom'],
    'vl_remun_media_sm': ['vl remun média (sm)', 'vl remun media (sm)'],
    'faixa_remun_dezem_sm': ['faixa remun dezem (sm)'],
    'faixa_remun_media_sm': ['faixa remun média (sm)', 'faixa remun media (sm)'],

    # --- REMUNERAÇÕES MENSAIS ---
    'vl_rem_janeiro_sc': ['vl rem janeiro sc'],
    'vl_rem_fevereiro_sc': ['vl rem fevereiro sc'],
    'vl_rem_marco_sc': ['vl rem março sc', 'vl rem marco sc'],
    'vl_rem_abril_sc': ['vl rem abril sc'],
    'vl_rem_maio_sc': ['vl rem maio sc'],
    'vl_rem_junho_sc': ['vl rem junho sc'],
    'vl_rem_julho_sc': ['vl rem julho sc'],
    'vl_rem_agosto_sc': ['vl rem agosto sc'],
    'vl_rem_setembro_sc': ['vl rem setembro sc'],
    'vl_rem_outubro_sc': ['vl rem outubro sc'],
    'vl_rem_novembro_sc': ['vl rem novembro sc'],
}

def limpar_valor_rais(valor):
    if valor is None: return None
    v = str(valor).replace('“', '').replace('”', '').replace('"', '').replace("'", "").strip()
    # Tratando o famoso '{ñ' da RAIS e campos vazios
    if v.upper() in ['', 'NA', 'NULL', 'NAN', '{Ñ', '{Ñ}', '000000000,00']: 
        return None
    return v

def processar_linha_rais(row_dict, ano_base):
    dados_finais = {'ano_base': int(ano_base)}
    txt_normalizado = {k.strip().lower(): v for k, v in row_dict.items()}

    for campo_banco, nomes_possiveis in MAPEAMENTO_RAIS.items():
        valor_bruto = None
        for nome in nomes_possiveis:
            if nome in txt_normalizado:
                valor_bruto = limpar_valor_rais(txt_normalizado[nome])
                break
        
        if valor_bruto is None: continue

        try:
            if campo_banco.startswith('vl_') or campo_banco == 'tempo_emprego':
                v = valor_bruto.replace(',', '.')
                dados_finais[campo_banco] = Decimal(v)
            elif campo_banco in ['idade', 'faixa_etaria', 'sexo_trabalhador', 'raca_cor', 
                               'escolaridade_apos_2005', 'nacionalidade', 'ind_portador_defic',
                               'tipo_defic', 'ano_chegada_brasil', 'vinculo_ativo_31_12',
                               'qtd_hora_contr', 'mes_admissao', 'ano_base']:
                v_limpo = valor_bruto.split(',')[0].split('.')[0]
                dados_finais[campo_banco] = int(v_limpo)
            else:
                dados_finais[campo_banco] = valor_bruto
        except:
            continue
    return dados_finais

def importar_arquivo_individual(caminho_arquivo, ano_base, limit=None, lote_tamanho=2000):
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Erro: Arquivo não encontrado em {caminho_arquivo}")
        return

    start_time = time.time()
    print(f"🚀 Iniciando: {os.path.basename(caminho_arquivo)} (Ano Base: {ano_base})")

    try:
        # Tenta Latin-1 (padrão RAIS), se não UTF-8
        try:
            f = open(caminho_arquivo, 'r', encoding='latin-1')
            header_line = f.readline()
        except UnicodeDecodeError:
            f = open(caminho_arquivo, 'r', encoding='utf-8')
            header_line = f.readline()

        # Detecta separador (RAIS varia entre ';' e '\t')
        separator = ';' if ';' in header_line else '\t'
        header = [h.strip().lower() for h in header_line.strip().split(separator)]
        
        batch = []
        cont_sucesso = 0
        
        for i, linha_texto in enumerate(f, 1):
            if limit and cont_sucesso >= limit: break
            
            try:
                campos = linha_texto.strip().split(separator)
                if len(campos) < len(header): continue
                
                row_dict = dict(zip(header, campos))
                dados = processar_linha_rais(row_dict, ano_base)
                
                batch.append(MovimentacaoRais(**dados))
                cont_sucesso += 1

                if i % 2000 == 0:
                    print(f"   ⏳ Linha {i} processada...")

                if len(batch) >= lote_tamanho:
                    MovimentacaoRais.objects.bulk_create(batch)
                    batch = []
                    db.reset_queries()
            except Exception as e:
                continue
        
        if batch:
            MovimentacaoRais.objects.bulk_create(batch)
        
        f.close()
        duration = time.time() - start_time
        print(f"✅ Finalizado! {cont_sucesso:,} registros em {duration:.2f}s")

    except Exception as e:
        print(f"🚨 Erro fatal: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--arquivo', required=True, help="Caminho completo do arquivo .txt ou .comt")
    parser.add_argument('--ano', required=True, help="Ano base para gravar no banco")
    parser.add_argument('--limit', type=int, default=None)
    args = parser.parse_args()
    
    importar_arquivo_individual(args.arquivo, args.ano, args.limit)