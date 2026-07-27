# PYTHONPATH=. python utils/teste_import_rais.py 

import os
import django
import pandas as pd
from decimal import Decimal

# Configuração para o script rodar fora do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoesrais.models import MovimentacaoRais

def limpar_valor(valor_str):
    """Converte '0000001110,00' em Decimal(1110.00)"""
    if pd.isna(valor_str) or str(valor_str).strip() in ['{ñ', '', '{ñ class}']:
        return Decimal('0.00')
    valor_limpo = valor_str.replace('.', '').replace(',', '.').strip()
    try:
      return Decimal(valor_limpo)
    except:
      return Decimal('0.00')

def limpar_int(val):
    """Converte para inteiro, tratando erros e valores nulos"""
    try:
        # Se for algo como '0003', o int() limpa os zeros à esquerda
        return int(float(str(val).replace('{ñ', '0').strip()))
    except:
        return 0

def limpar_str(val):
    """Limpa espaços em branco e trata valores nulos"""
    if pd.isna(val):
        return ""
    return str(val).strip()

def testar_importacao():
    caminho = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/RAIS/2021/RAIS_VINC_PUB_ARAPIRACA.txt'
    
    print(f"Lendo as primeiras 5 linhas para teste... {caminho}")
    df = pd.read_csv(caminho, sep=';', encoding='latin-1', nrows=5, dtype=str)
    
    mapeamento = {
        'Bairros SP': 'bairros_sp', 'Bairros Fortaleza': 'bairros_fortaleza', 'Bairros RJ': 'bairros_rj',
        'Causa Afastamento 1': 'causa_afastamento_1', 'Causa Afastamento 2': 'causa_afastamento_2',
        'Causa Afastamento 3': 'causa_afastamento_3', 'Motivo Desligamento': 'motivo_desligamento',
        'CBO Ocupação 2002': 'cbo_ocupacao_2002', 'CNAE 2.0 Classe': 'cnae_2_0_classe',
        'CNAE 95 Classe': 'cnae_95_classe', 'Distritos SP': 'distritos_sp',
        'Vínculo Ativo 31/12': 'vinculo_ativo_31_12', 'Faixa Etária': 'faixa_etaria',
        'Faixa Hora Contrat': 'faixa_hora_contrat', 'Faixa Remun Dezem (SM)': 'faixa_remun_dezem_sm',
        'Faixa Remun Média (SM)': 'faixa_remun_media_sm', 'Faixa Tempo Emprego': 'faixa_tempo_emprego',
        'Escolaridade após 2005': 'escolaridade_apos_2005', 'Qtd Hora Contr': 'qtd_hora_contr',
        'Idade': 'idade', 'Ind CEI Vinculado': 'ind_cei_vinculado', 'Ind Simples': 'ind_simples',
        'Mês Admissão': 'mes_admissao', 'Mês Desligamento': 'mes_desligamento',
        'Mun Trab': 'mun_trab', 'Município': 'municipio', 'Nacionalidade': 'nacionalidade',
        'Natureza Jurídica': 'natureza_juridica', 'Ind Portador Defic': 'ind_portador_defic',
        'Qtd Dias Afastamento': 'qtd_dias_afastamento', 'Raça Cor': 'raca_cor',
        'Vl Remun Dezembro Nom': 'vl_remun_dezembro_nom', 'Vl Remun Dezembro (SM)': 'vl_remun_dezembro_sm',
        'Vl Remun Média Nom': 'vl_remun_media_nom', 'Vl Remun Média (SM)': 'vl_remun_media_sm',
        'CNAE 2.0 Subclasse': 'cnae_2_0_subclasse', 'Sexo Trabalhador': 'sexo_trabalhador',
        'Tamanho Estabelecimento': 'tamanho_estabelecimento', 'Tempo Emprego': 'tempo_emprego',
        'Tipo Admissão': 'tipo_admissao', 'Tipo Estab': 'tipo_estab', 'Tipo Estab.1': 'tipo_estab_1',
        'Tipo Defic': 'tipo_defic', 'Tipo Vínculo': 'tipo_vinculo', 'IBGE Subsetor': 'ibge_subsetor',
        'Vl Rem Janeiro SC': 'vl_rem_janeiro_sc', 'Vl Rem Fevereiro SC': 'vl_rem_fevereiro_sc',
        'Vl Rem Março SC': 'vl_rem_marco_sc', 'Vl Rem Abril SC': 'vl_rem_abril_sc',
        'Vl Rem Maio SC': 'vl_rem_maio_sc', 'Vl Rem Junho SC': 'vl_rem_junho_sc',
        'Vl Rem Julho SC': 'vl_rem_julho_sc', 'Vl Rem Agosto SC': 'vl_rem_agosto_sc',
        'Vl Rem Setembro SC': 'vl_rem_setembro_sc', 'Vl Rem Outubro SC': 'vl_rem_outubro_sc',
        'Vl Rem Novembro SC': 'vl_rem_novembro_sc', 'Ano Chegada Brasil': 'ano_chegada_brasil',
        'Ind Trab Intermitente': 'ind_trab_intermitente', 'Ind Trab Parcial': 'ind_trab_parcial'
    }

    objetos_para_bulk = []

    for _, row in df.iterrows():
        dados_higienizados = {'ano_base': 2021}
        
        for coluna_txt, campo_model in mapeamento.items():
            valor_bruto = row[coluna_txt]
            
            # Lógica de limpeza baseada no prefixo ou nome do campo
            if "Vl Rem" in coluna_txt or coluna_txt == "Tempo Emprego":
                dados_higienizados[campo_model] = limpar_valor(valor_bruto)
            elif campo_model in ['mun_trab', 'municipio', 'cbo_ocupacao_2002', 'cnae_2_0_classe', 'cnae_95_classe', 'cnae_2_0_subclasse', 'mes_desligamento', 'tipo_estab_1', 'bairros_sp', 'bairros_fortaleza', 'bairros_rj', 'distritos_sp']:
                dados_higienizados[campo_model] = limpar_str(valor_bruto)
            else:
                dados_higienizados[campo_model] = limpar_int(valor_bruto)

        objetos_para_bulk.append(MovimentacaoRais(**dados_higienizados))

    # Inserção no Neon
    MovimentacaoRais.objects.bulk_create(objetos_para_bulk)
    print(f"✅ Sucesso! {len(objetos_para_bulk)} registros inseridos com todas as colunas.")

if __name__ == "__main__":
    testar_importacao()