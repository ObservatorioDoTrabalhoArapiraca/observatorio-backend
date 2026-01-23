# python utils/descompactar_arquivo_unico.py "/home/usuario/Github/RAIS/2020/RAIS_VINC_PUB_CENTRO_OESTE.7z"

import os
import py7zr
from tqdm import tqdm
import gc
import sys

def formatar_bytes(bytes_size):
    """Converte bytes para formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def verificar_espaco_disco(pasta, tamanho_arquivo):
    """Verifica se há espaço suficiente"""
    import shutil
    livre = shutil.disk_usage(pasta).free
    necessario = tamanho_arquivo * 3  # Estimativa: 3x o tamanho compactado
    
    print(f"💾 Espaço livre: {formatar_bytes(livre)}")
    print(f"📊 Espaço estimado necessário: {formatar_bytes(necessario)}")
    
    if livre < necessario:
        print(f"⚠️  AVISO: Espaço pode ser insuficiente!")
        resposta = input("Continuar mesmo assim? (s/n): ").lower()
        return resposta == 's'
    return True

def descompactar_otimizado(caminho_arquivo, pasta_destino=None, chunk_size=100):
    """
    Descompacta arquivo .7z de forma otimizada para arquivos grandes
    
    Args:
        caminho_arquivo: Caminho do arquivo .7z
        pasta_destino: Pasta de destino (None = mesma pasta do arquivo)
        chunk_size: Quantos arquivos processar antes de limpar memória
    """
    
    # ========== VALIDAÇÕES ==========
    if not os.path.exists(caminho_arquivo):
        print(f"❌ Erro: Arquivo não encontrado!")
        print(f"   Caminho: {caminho_arquivo}")
        return False
    
    if not caminho_arquivo.endswith('.7z'):
        print(f"❌ Erro: O arquivo deve ter extensão .7z")
        return False
    
    # Define pasta de destino
    if pasta_destino is None:
        pasta_destino = os.path.dirname(caminho_arquivo)
    
    os.makedirs(pasta_destino, exist_ok=True)
    
    # ========== INFORMAÇÕES DO ARQUIVO ==========
    tamanho_arquivo = os.path.getsize(caminho_arquivo)
    nome_arquivo = os.path.basename(caminho_arquivo)
    
    print("\n" + "="*60)
    print("📦 DESCOMPACTAÇÃO DE ARQUIVO")
    print("="*60)
    print(f"📄 Arquivo: {nome_arquivo}")
    print(f"📊 Tamanho: {formatar_bytes(tamanho_arquivo)}")
    print(f"📂 Destino: {pasta_destino}")
    print("="*60 + "\n")
    
    # Verifica espaço em disco
    if not verificar_espaco_disco(pasta_destino, tamanho_arquivo):
        print("❌ Operação cancelada pelo usuário.")
        return False
    
    # ========== DESCOMPACTAÇÃO COM CHUNKS ==========
    try:
        print("🔍 Analisando arquivo compactado...")
        
        with py7zr.SevenZipFile(caminho_arquivo, mode='r') as z:
            # Lista todos os arquivos internos
            allfiles = z.getnames()
            total_arquivos = len(allfiles)
            
            print(f"📄 Total de arquivos dentro: {total_arquivos}")
            print(f"⚙️  Processando em lotes de {chunk_size} arquivos")
            print(f"⏳ Iniciando extração...\n")
            
            # Barra de progresso
            with tqdm(
                total=total_arquivos,
                desc="Extraindo",
                unit="arquivo",
                unit_scale=False,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            ) as pbar:
                
                # Processa em chunks
                for i in range(0, total_arquivos, chunk_size):
                    chunk = allfiles[i:i + chunk_size]
                    
                    # Extrai chunk
                    z.extract(path=pasta_destino, targets=chunk)
                    
                    # Atualiza progresso
                    pbar.update(len(chunk))
                    
                    # Libera memória a cada chunk
                    gc.collect()
        
        print("\n" + "="*60)
        print("✅ DESCOMPACTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print(f"📂 Arquivos extraídos em: {pasta_destino}")
        print(f"📊 Total de arquivos: {total_arquivos}")
        print("="*60 + "\n")
        
        return True
        
    except MemoryError:
        print("\n❌ ERRO: Memória insuficiente!")
        print("💡 Dica: Feche outros programas e tente novamente")
        return False
        
    except KeyboardInterrupt:
        print("\n⚠️  Operação cancelada pelo usuário (Ctrl+C)")
        return False
        
    except Exception as e:
        print(f"\n❌ ERRO ao descompactar: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")
        return False

def menu_interativo():
    """Menu interativo para descompactar arquivos"""
    print("\n" + "="*60)
    print("🗜️  DESCOMPACTADOR DE ARQUIVOS .7z")
    print("="*60 + "\n")
    
    # Solicita caminho do arquivo
    while True:
        caminho = input("📂 Digite o caminho completo do arquivo .7z:\n> ").strip()
        
        # Remove aspas se o usuário copiar/colar do explorador
        caminho = caminho.strip('"').strip("'")
        
        if os.path.exists(caminho):
            if caminho.endswith('.7z'):
                break
            else:
                print("❌ O arquivo deve ter extensão .7z!\n")
        else:
            print("❌ Arquivo não encontrado!")
            print(f"   Caminho digitado: {caminho}\n")
            
            opcao = input("Tentar novamente? (s/n): ").lower()
            if opcao != 's':
                print("👋 Programa encerrado.")
                return
    
    # Pergunta se quer pasta de destino diferente
    print("\n📁 Deseja extrair para uma pasta diferente?")
    print("   (deixe em branco para extrair na mesma pasta do arquivo)")
    
    pasta_destino = input("> ").strip().strip('"').strip("'")
    
    if not pasta_destino:
        pasta_destino = None
    
    # Pergunta tamanho do chunk
    print("\n⚙️  Tamanho do lote de processamento:")
    print("   (50-100 recomendado para arquivos grandes)")
    
    try:
        chunk_input = input("> ").strip()
        chunk_size = int(chunk_input) if chunk_input else 100
        if chunk_size < 1:
            chunk_size = 100
    except ValueError:
        chunk_size = 100
    
    print(f"\n✅ Usando lotes de {chunk_size} arquivos\n")
    
    # Inicia descompactação
    sucesso = descompactar_otimizado(caminho, pasta_destino, chunk_size)
    
    if sucesso:
        print("\n🎉 Tudo pronto!")
    else:
        print("\n😞 Algo deu errado. Verifique os erros acima.")

if __name__ == "__main__":
    try:
        menu_interativo()
    except KeyboardInterrupt:
        print("\n\n👋 Programa encerrado pelo usuário.")
        sys.exit(0)