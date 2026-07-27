

import os
# PYTHONPATH=. python utils/parquet_to_csv_arapiraca.py --anos 2022,2023,2024,2025

import os
import argparse
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def buscar_descricoes(engine):
    """Busca as descrições das tabelas de referência"""
    descricoes = {}
    
    # Descrições de seção
    query_secao = text("SELECT codigo, descricao FROM referenciais_secaoreferencia")
    with engine.connect() as conn:
        result = conn.execute(query_secao)
        descricoes['secao'] = {str(row[0]): row[1] for row in result}
    
    # Descrições de município
    query_municipio = text("SELECT codigo, descricao FROM referenciais_municipioreferencia")
    with engine.connect() as conn:
        result = conn.execute(query_municipio)
        descricoes['municipio'] = {int(row[0]): row[1] for row in result}
        
    
    # Descrições de CBO
    query_cbo = text("SELECT codigo, descricao FROM referenciais_cbo2002ocupacaoreferencia")
    with engine.connect() as conn:
        result = conn.execute(query_cbo)
        descricoes['cbo'] = {int(row[0]): row[1] for row in result}
    
    return descricoes

def processar_parquet_para_csv(caminho_parquet, descricoes):
    """Processa um arquivo Parquet e retorna DataFrame com descrições"""
    try:
        # Lê o arquivo Parquet
        df = pd.read_parquet(caminho_parquet)
        
        # Extrai ano e mês de competencia_mov (formato YYYYMM)
        df['competênciamov'] = df['competênciamov'].astype(str)
        df['ano'] = df['competênciamov'].str[:4].astype(int)
        df['mes'] = df['competênciamov'].str[4:6].astype(int)
        
        # Seleciona colunas necessárias
        df_filtrado = df[[
            'ano', 'mes', 
            'município', 
            'cbo2002ocupação', 
            'seção', 
            'saldomovimentação'
        ]].copy()
        
       
        
        # Converte para tipos adequados para mapeamento
        df_filtrado['município'] = df_filtrado['município'].astype(int)
        df_filtrado['cbo2002ocupação'] = df_filtrado['cbo2002ocupação'].astype(int)
        df_filtrado['seção'] = df_filtrado['seção'].astype(str)
        
        # Adiciona descrições
        df_filtrado['municipio_descricao'] = df_filtrado['município'].map(descricoes['municipio'])
        df_filtrado['cbo2002_ocupacao_descricao'] = df_filtrado['cbo2002ocupação'].map(descricoes['cbo'])
        df_filtrado['secao_descricao'] = df_filtrado['seção'].map(descricoes['secao'])
        
        # Reordena colunas
        df_final = df_filtrado[[
            'ano', 'mes', 
            'município', 'municipio_descricao',
            'cbo2002ocupação', 'cbo2002_ocupacao_descricao',
            'seção', 'secao_descricao',
            'saldomovimentação'
        ]]
        
        return df_final
        
    except Exception as e:
        print(f"Erro ao processar {caminho_parquet}: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    parser = argparse.ArgumentParser(description="Exportar dados de Arapiraca para Excel.")
    parser.add_argument('--anos', required=True, help='Anos a serem processados (ex: 2022,2023,2024,2025)')
    parser.add_argument('--output-dir', default='./output_csv', help='Diretório de saída dos arquivos')
    args = parser.parse_args()
    
    anos = [ano.strip() for ano in args.anos.split(',')]
    output_dir = args.output_dir
    os.makedirs(output_dir, exist_ok=True)
    
    # Conecta ao banco de dados
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
      print("Erro: variável DATABASE_URL não encontrada no .env")
      return
    engine = create_engine(database_url)
    
    print("Buscando descrições do banco de dados...")
    descricoes = buscar_descricoes(engine)
    print(f"Descrições carregadas: {len(descricoes['secao'])} seções, {len(descricoes['municipio'])} municípios, {len(descricoes['cbo'])} CBOs")
   
    dados_por_ano = {}
    # Processa cada ano
    base_dir = '/home/usuario/Github/NOVO CAGED/'
    
    for ano in anos:
        print(f"\nProcessando ano {ano}...")
        ano_dir = os.path.join(base_dir, ano)
        
        if not os.path.exists(ano_dir):
            print(f"Diretório não encontrado: {ano_dir}")
            continue
        
        dataframes = []
        arquivos_processados = 0
        
        # Itera sobre os arquivos do ano
        for root, dirs, files in os.walk(ano_dir):
            for arquivo in files:
                if arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
                    caminho_parquet = os.path.join(root, arquivo)
                    print(f"Processando: {caminho_parquet}")
                    
                    df = processar_parquet_para_csv(caminho_parquet, descricoes)
                    if df is not None:
                        dataframes.append(df)
                        arquivos_processados += 1
        
        # Consolida dados do ano
        if dataframes:
            df_ano = pd.concat(dataframes, ignore_index=True)
            dados_por_ano[ano] = df_ano
            
            # Ainda salva CSV individual para compatibilidade
            arquivo_csv = os.path.join(output_dir, f'arapiraca_{ano}.csv')
            df_ano.to_csv(arquivo_csv, index=False, encoding='utf-8-sig')
            print(f"  ✓ CSV do ano {ano} salvo: {arquivo_csv}")
            print(f"    - {arquivos_processados} arquivos processados")
            print(f"    - {len(df_ano)} linhas totais")
        else:
            print(f"  ⚠ Nenhum dado encontrado para o ano {ano}")
    
    # Cria arquivo Excel consolidado com abas por ano
    print("\n" + "="*80)
    print("Criando arquivo Excel consolidado com abas por ano...")
    
    if dados_por_ano:
        arquivo_excel = os.path.join(output_dir, 'arapiraca_2022_2025_consolidado.xlsx')
        
        with pd.ExcelWriter(arquivo_excel, engine='openpyxl') as writer:
            for ano in sorted(dados_por_ano.keys()):
                df = dados_por_ano[ano]
                df.to_excel(writer, sheet_name=ano, index=False)
                print(f"  + Aba '{ano}': {len(df)} linhas")
        
        print(f"\n✓ Arquivo Excel consolidado salvo: {arquivo_excel}")
        print(f"  - Abas criadas: {', '.join(sorted(dados_por_ano.keys()))}")
        print("="*80)
    else:
        print("  ⚠ Nenhum dado encontrado para gerar o Excel consolidado")
 
if __name__ == '__main__':
    main()