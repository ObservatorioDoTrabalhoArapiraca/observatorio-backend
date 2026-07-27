# PYTHONPATH=. python utils/verificar_estrutura_parquet.py --ano 2020

import os
import sys
import argparse
import pandas as pd

def verificar_estrutura(caminho_arquivo):
    """Mostra a estrutura e primeiras linhas de um arquivo Parquet"""
    print(f"\n{'='*80}")
    print(f"📄 Arquivo: {os.path.basename(caminho_arquivo)}")
    print(f"{'='*80}")
    
    try:
        # Lê apenas as primeiras linhas para economizar memória
        df = pd.read_parquet(caminho_arquivo)
        
        print(f"\n📊 Informações Gerais:")
        print(f"   Total de linhas: {len(df)}")
        print(f"   Total de colunas: {len(df.columns)}")
        
        print(f"\n📋 Colunas e tipos:")
        print("-" * 80)
        for col in df.columns:
            tipo = df[col].dtype
            nao_nulos = df[col].count()
            print(f"   {col:<40} | Tipo: {str(tipo):<15} | Não-nulos: {nao_nulos}")
        
        print(f"\n📝 Primeiras 3 linhas:")
        print("-" * 80)
        print(df.head(3).to_string())
        
        print(f"\n💡 Exemplo de valores únicos (primeiras 5 colunas):")
        print("-" * 80)
        for col in df.columns[:5]:
            valores_unicos = df[col].nunique()
            exemplos = df[col].dropna().unique()[:3]
            print(f"   {col}: {valores_unicos} valores únicos")
            print(f"      Exemplos: {list(exemplos)}")
        
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verificar estrutura dos arquivos Parquet")
    parser.add_argument('--ano', required=True, help='Ano a ser processado (ex: 2020)')
    parser.add_argument('--mes', help='Mês específico (opcional, ex: 01)')
    args = parser.parse_args()
    
    base_dir = f'/home/usuario/Github/NOVO CAGED/{args.ano}/'
    
    if not os.path.isdir(base_dir):
        print(f"❌ Diretório não encontrado: {base_dir}")
        sys.exit(1)
    
    tipos_arquivo = ['CAGEDMOV', 'CAGEDFOR', 'CAGEDEXC']
    arquivos_encontrados = []
    
    print(f"\n{'='*80}")
    print(f"🔍 Buscando arquivos em: {base_dir}")
    print(f"{'='*80}")
    
    # Procura arquivos de cada tipo
    for root, dirs, files in os.walk(base_dir):
        for arquivo in sorted(files):
            # Busca arquivos filtrados de Arapiraca
            if arquivo.endswith('-Al-Arapiraca_filtrado.parquet'):
                for tipo in tipos_arquivo:
                    if arquivo.startswith(tipo):
                        # Se especificou um mês, filtra
                        if args.mes:
                            mes_no_arquivo = arquivo.replace(tipo, '').split('-')[0]
                            if not mes_no_arquivo.endswith(args.mes):
                                continue
                        
                        caminho_completo = os.path.join(root, arquivo)
                        arquivos_encontrados.append((tipo, caminho_completo))
                        break
    
    if not arquivos_encontrados:
        print(f"\n⚠️  Nenhum arquivo encontrado!")
        sys.exit(1)
    
    # Agrupa por tipo
    por_tipo = {}
    for tipo, caminho in arquivos_encontrados:
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(caminho)
    
    print(f"\n✓ Encontrados {len(arquivos_encontrados)} arquivo(s):")
    for tipo, arquivos in por_tipo.items():
        print(f"   {tipo}: {len(arquivos)} arquivo(s)")
    
    # Verifica a estrutura de um arquivo de cada tipo
    print(f"\n{'='*80}")
    print(f"📊 VERIFICANDO ESTRUTURA DE CADA TIPO")
    print(f"{'='*80}")
    
    for tipo, arquivos in por_tipo.items():
        # Pega o primeiro arquivo de cada tipo
        verificar_estrutura(arquivos[0])
    
    print(f"\n{'='*80}")
    print(f"✅ Verificação concluída!")
    print(f"{'='*80}\n")