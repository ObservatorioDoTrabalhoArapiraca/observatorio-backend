"""
Script de importação detalhada de arquivo Parquet

Este script importa um arquivo Parquet linha por linha, rastreando cada falha
e fornecendo relatório completo ao final.

Uso:
 
    
    PYTHONPATH=. python utils/importar_arquivo_detalhado.py --ano 2023 --mes 01 --type MOV
"""

import os
import sys
import django
import argparse
import pandas as pd
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

parser = argparse.ArgumentParser(description='Script de importação detalhada de arquivo Parquet')
parser.add_argument('--ano', required=True, help='Ano a ser analisado (ex: 2020)')
parser.add_argument('--mes', required=True, help='Mês a ser analisado (ex: 01)')
parser.add_argument('--type', required=True, help='Tipo de arquivo (ex: MOV, EXC, FOR)')
args = parser.parse_args()
# Configuração do Django
# Estas linhas permitem que o script acesse os models do Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Imports do Django (só funcionam após django.setup())
from apps.movimentacoes.models import Movimentacao
from django.db import transaction, connection
from django.core.exceptions import ValidationError

CAMINHO_ARQUIVO = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{args.ano}/{args.ano}{args.mes}/CAGED{args.type}{args.ano}{args.mes}-Al-Arapiraca_filtrado.parquet'

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def obter_tipo_python(valor):
    """
    Retorna o tipo do valor em formato legível
    
    Exemplos:
        obter_tipo_python(123) -> 'int'
        obter_tipo_python('texto') -> 'str'
        obter_tipo_python(None) -> 'NoneType'
    """
    return type(valor).__name__


def formatar_valor_para_exibicao(valor):
    """
    Formata um valor para exibição no console
    
    - Se for string, coloca entre aspas
    - Se for None, mostra 'None'
    - Se for número, mostra sem aspas
    - Limita tamanho para não poluir console
    """
    if valor is None:
        return 'None'
    elif isinstance(valor, str) and len(valor) > 50:
        # Limita strings muito longas
      return f'"{valor[:50]}..."'
    else:
        return str(valor)


def extrair_dados_linha(row, id_sequencial):
    """
    Extrai todos os dados de uma linha do DataFrame e retorna
    um dicionário estruturado com valores e tipos
    
    Args:
        row: Linha do pandas DataFrame
        id_sequencial: ID criado sequencialmente (1, 2, 3...)
    
    Returns:
        dict: Dicionário com estrutura:
        {
            'campo1': {'valor': valor1, 'tipo': 'int'},
            'campo2': {'valor': valor2, 'tipo': 'str'},
            ...
        }
    """
    dados_estruturados = {}
    
    # Percorre cada coluna da linha
    for coluna in row.index:
        valor = row[coluna]
        
        # Pandas usa pd.NA ou np.nan para valores vazios
        # Convertemos para None do Python
        if pd.isna(valor):
            valor_limpo = None
        else:
            valor_limpo = valor
        
        # Armazena valor e seu tipo
        dados_estruturados[coluna] = {
            'valor': valor_limpo,
            'tipo': obter_tipo_python(valor_limpo)
        }
    
    return dados_estruturados


def exibir_dados_linha(id_sequencial, dados_estruturados, mostrar_todos=False):
    """
    Exibe os dados de uma linha formatados
    
    Args:
        id_sequencial: ID da linha
        dados_estruturados: Dicionário retornado por extrair_dados_linha()
        mostrar_todos: Se True, mostra todos os campos. Se False, mostra resumo
    """
    print(f"   ID: {id_sequencial}")
    
    campos_para_mostrar = dados_estruturados.items()
    if not mostrar_todos:
        # Mostra apenas primeiros 5 campos
        campos_para_mostrar = list(dados_estruturados.items())[:5]
    
    for campo, info in campos_para_mostrar:
        valor_formatado = formatar_valor_para_exibicao(info['valor'])
        print(f"   • {campo}: {valor_formatado} ({info['tipo']})")
    
    if not mostrar_todos and len(dados_estruturados) > 5:
        print(f"   ... e mais {len(dados_estruturados) - 5} campos")


#     Próximos passos (Parte 2):

# Lógica de tentativa de importação de cada linha
# Captura de erros detalhados
# Validações de tipos e campos


# ============================================================================
# PARTE 2: FUNÇÃO DE VALIDAÇÃO E PREPARAÇÃO DOS DADOS
# ============================================================================

def validar_e_preparar_dados(dados_estruturados, id_sequencial):
    """
    Valida os dados de uma linha e prepara para inserção no banco
    
    Args:
        dados_estruturados: Dicionário retornado por extrair_dados_linha()
        id_sequencial: ID da linha (para mensagens de erro)
    
    Returns:
        tuple: (sucesso: bool, dados_preparados: dict ou None, erro: str ou None)
        
    Exemplo de retorno em caso de sucesso:
        (True, {'competencia_mov': 202301, 'salario': 1500, ...}, None)
        
    Exemplo de retorno em caso de erro:
        (False, None, "Campo 'salario' deve ser numérico, recebeu string")
    """
    
    # MAPEAMENTO = {
    # # Arquivo → Banco
    # 'competênciamov': 'competencia_mov',        # INTEGER
    # 'município': 'municipio_id',                # INTEGER (FK)
    # 'saldomovimentação': 'saldo_movimentacao',  # INTEGER
    # 'cbo2002ocupação': 'cbo2002_ocupacao_id',   # INTEGER (FK)
    # 'graudeinstrução': 'grau_instrucao_id',     # INTEGER (FK)
    # 'idade': 'idade',                           # INTEGER
    # 'raçacor': 'raca_cor_id',                   # INTEGER (FK)
    # 'sexo': 'sexo_id',                          # INTEGER (FK)
    # 'tipodedeficiência': 'tipo_deficiencia_id', # INTEGER (FK)
    # 'salário': 'salario',                       # NUMERIC(10,2)
    # }
    
    try:
        # Dicionário que será usado para criar o objeto no banco
        dados_preparados = {}
        
        # ============================================================
        # VALIDAÇÃO 1: Competência (obrigatório, integer)
        # ============================================================
        
        # Descobre os nomes das colunas no arquivo
        colunas_disponiveis = list(dados_estruturados.keys())
        
        
        # Tenta várias possibilidades de nome da coluna
        coluna_competencia = None
        for possivel_nome in ['competênciamov', 'competencia', 'Competência', 'COMPETENCIA', 'competência', 'competência_mov', 'competencia_mov']:
            if possivel_nome in dados_estruturados:
                coluna_competencia = possivel_nome
                break
        
        if not coluna_competencia:
            return (False, None, f"Campo 'competencia' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        
        # Pega o valor
        comp_valor = dados_estruturados[coluna_competencia]['valor']
        
        # Valida se não é vazio
        if comp_valor is None:
            return (False, None, f"Campo 'competencia' está vazio (None)")
        
        dados_preparados['competencia_movimentacao'] = comp_valor
        
    
        # ============================================================
        # VALIDAÇÃO 2: CBO (obrigatório, string de 6 dígitos)
        # ============================================================
        coluna_cbo = None
        for possivel_nome in ['cbo2002ocupação', 'cbo2002', 'CBO', 'cbo']:
            if possivel_nome in dados_estruturados:
                coluna_cbo = possivel_nome
                break
        
        if not coluna_cbo:
             return (False, None, f"Campo 'cbo' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        
        cbo_valor = dados_estruturados[coluna_cbo]['valor']
        if cbo_valor is None:
            return (False, None, "Campo 'cbo' está vazio (None)")
        
        dados_preparados['cbo2002_ocupacao_id'] = cbo_valor
        
        
        
        # ============================================================
        # VALIDAÇÃO 3: Município (obrigatório, string)
        # ============================================================
        coluna_municipio = None
        for possivel_nome in ['município', 'municipio', 'Município', 'MUNICIPIO']:
            if possivel_nome in dados_estruturados:
                coluna_municipio = possivel_nome
                break
        
        if not coluna_municipio:
            return (False, None, f"Campo 'municipio' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        
        mun_valor = dados_estruturados[coluna_municipio]['valor']
        if mun_valor is None:
            return (False, None, "Campo 'municipio' está vazio (None)")
        
        # MANTÉM EXATAMENTE COMO ESTÁ
        dados_preparados['municipio_id'] = mun_valor
        
        
        # ============================================================
        # VALIDAÇÃO 4: Salário (obrigatório, numérico)
        # ============================================================
        coluna_salario = None
        for possivel_nome in ['saldomovimentação', 'salario', 'salário', 'Salario', 'SALARIO', 'saldomovimentacao']:
            if possivel_nome in dados_estruturados:
                coluna_salario = possivel_nome
                break
        
        if not coluna_salario:
            return (False, None, f"Campo 'salario' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        
        sal_valor = dados_estruturados[coluna_salario]['valor']
        if sal_valor is None:
            return (False, None, "Campo 'salario' está vazio (None)")
        
        # MANTÉM EXATAMENTE COMO ESTÁ
        dados_preparados['salario'] = sal_valor
        # ============================================================
        # VALIDAÇÃO 5: Saldo Movimentação (obrigatório, inteiro)
        # ============================================================
        coluna_saldo = None
        for possivel_nome in ['saldomovimentação', 'saldo_movimentacao', 'saldo']:
            if possivel_nome in dados_estruturados:
                coluna_saldo = possivel_nome
                break
        
        if coluna_saldo:
            saldo_valor = dados_estruturados[coluna_saldo]['valor']
            if saldo_valor is not None:
                # MANTÉM EXATAMENTE COMO ESTÁ
                dados_preparados['saldo_movimentacao'] = saldo_valor
        
        
        
        
        # ============================================================
        # VALIDAÇÃO 6: Campos opcionais (idade, sexo, etc)
        # ============================================================
        # Aqui você pode adicionar mais campos conforme seu modelo
        # Por enquanto, vamos apenas mapear alguns básicos
        
        # Sexo
        if 'sexo' in dados_estruturados:
            sexo_valor = dados_estruturados['sexo']['valor']
            if sexo_valor is not None:
                dados_preparados['sexo_id'] = sexo_valor
        
        # Idade
        if 'idade' in dados_estruturados:
            idade_valor = dados_estruturados['idade']['valor']
            if idade_valor is not None and isinstance(idade_valor, (int, float)):
                dados_preparados['idade'] = idade_valor
        
        # Raça/Cor
        for possivel_nome in ['raçacor', 'racacor', 'raca_cor']:
            if possivel_nome in dados_estruturados:
                raca_valor = dados_estruturados[possivel_nome]['valor']
                if raca_valor is not None:
                    dados_preparados['raca_cor_id'] = raca_valor
                break
        
        # Grau de Instrução
        for possivel_nome in ['graudeinstrução', 'grauinstrucao', 'grau_instrucao']:
            if possivel_nome in dados_estruturados:
                grau_valor = dados_estruturados[possivel_nome]['valor']
                if grau_valor is not None:
                    dados_preparados['grau_instrucao_id'] = grau_valor
                break
        
        # Tipo de deficiência
        coluna_def = None
        for nome in ['tipodedeficiência', 'tipodeficiencia', 'tipo_deficiencia']:
            if nome in dados_estruturados:
                coluna_def = nome
                break
        if coluna_def:
            def_valor = dados_estruturados[coluna_def]['valor']
            if def_valor is not None:
                dados_preparados['tipo_deficiencia_id'] = def_valor
        
        # Se chegou aqui, todos os campos obrigatórios foram validados
        return (True, dados_preparados, None)
        
    except Exception as e:
        # Captura qualquer erro não previsto na validação
        return (False, None, f"Erro inesperado na validação: {str(e)}")


# ============================================================================
# PARTE 3: FUNÇÃO DE INSERÇÃO NO BANCO
# ============================================================================

def tentar_inserir_no_banco(dados_preparados, id_sequencial):
    """
    Tenta inserir os dados no banco e captura erros específicos
    
    Returns:
        tuple: (sucesso: bool, erro_detalhado: str ou None)
    """
    try:
        # Cria o objeto Movimentacao
        movimentacao = Movimentacao(**dados_preparados)
        
        # Valida (chama os validators do Django)
        movimentacao.full_clean()
        
        # Salva no banco
        movimentacao.save()
        
        return (True, None)
        
    except ValidationError as e:
        # Erros de validação do Django (ex: campo obrigatório vazio)
        erros = []
        for campo, mensagens in e.message_dict.items():
            erros.append(f"{campo}: {', '.join(mensagens)}")
        return (False, f"Erro de validação: {'; '.join(erros)}")
        
    except Exception as e:
        erro_str = str(e)
        
        # Detecta erro de Foreign Key
        if 'foreign key constraint' in erro_str.lower() or 'violates foreign key' in erro_str.lower():
            # Tenta identificar qual FK falhou
            if 'cbo2002_ocupacao_id' in erro_str:
                return (False, f"CBO '{dados_preparados.get('cbo2002_ocupacao_id')}' não existe na tabela de referência")
            elif 'municipio_id' in erro_str:
                return (False, f"Município '{dados_preparados.get('municipio_id')}' não existe na tabela de referência")
            elif 'grau_instrucao_id' in erro_str:
                return (False, f"Grau Instrução '{dados_preparados.get('grau_instrucao_id')}' não existe na tabela de referência")
            elif 'sexo_id' in erro_str:
                return (False, f"Sexo '{dados_preparados.get('sexo_id')}' não existe na tabela de referência")
            elif 'raca_cor_id' in erro_str:
                return (False, f"Raça/Cor '{dados_preparados.get('raca_cor_id')}' não existe na tabela de referência")
            elif 'tipo_deficiencia_id' in erro_str:
                return (False, f"Tipo Deficiência '{dados_preparados.get('tipo_deficiencia_id')}' não existe na tabela de referência")
            else:
                return (False, f"Erro de Foreign Key: {erro_str}")
        
        # Detecta erro de conexão
        elif 'connection' in erro_str.lower() or 'timeout' in erro_str.lower():
            return (False, f"Perda de conexão com o banco: {erro_str}")
        
        # Outros erros
        else:
            return (False, f"Erro ao salvar no banco: {erro_str}")


# ============================================================================
# CONTINUAÇÃO DA FUNÇÃO PRINCIPAL (ETAPA 3)
# ============================================================================

def importar_arquivo_detalhado(caminho_arquivo):
    """Função principal que coordena toda a importação"""
    
    print(f"\n{'='*90}")
    print(f"📂 IMPORTAÇÃO DETALHADA DE ARQUIVO PARQUET")
    print(f"{'='*90}\n")
    print(f"Arquivo: {caminho_arquivo}")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ETAPA 1 e 2 (já implementadas acima)
    # ...
    print(f"{'='*90}")
    print(f"📋 ETAPA 1: VALIDAÇÃO E LEITURA")
    print(f"{'='*90}\n")
    
    if not os.path.isfile(caminho_arquivo):
        print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
        return
    
    print(f"✓ Arquivo encontrado")
    
    try:
        print(f"⏳ Lendo arquivo Parquet...")
        df = pd.read_parquet(caminho_arquivo)  # ← AQUI é definido o df
        print(f"✓ Arquivo lido")
        print(f"   Colunas: {len(df.columns)}")
        print(f"   Linhas: {len(df)}")
    except Exception as e:
        print(f"❌ Erro ao ler: {str(e)}")
        return
    
    # ETAPA 2: Contagem inicial
    print(f"\n{'='*90}")
    print(f"📊 ETAPA 2: CONTAGEM INICIAL")
    print(f"{'='*90}\n")
    
    total_linhas_arquivo = len(df)  # ← AQUI é definido
    print(f"Total de linhas no arquivo: {total_linhas_arquivo:,}")
    
    total_banco_antes = Movimentacao.objects.count()  # ← AQUI é definido
    print(f"Total no banco (antes): {total_banco_antes:,}")
    
    # ================================================================
    # ETAPA 3: PROCESSAMENTO LINHA A LINHA (COMPLETA)
    # ================================================================
    
    print(f"\n{'='*90}")
    print(f"⚙️  ETAPA 3: PROCESSAMENTO LINHA A LINHA")
    print(f"{'='*90}\n")
    
    linhas_com_falha = []
    linhas_importadas_com_sucesso = 0
    
    # Processa cada linha
    for id_sequencial, (indice, row) in enumerate(df.iterrows(), start=1):
        
        # Extrai dados da linha
        dados_estruturados = extrair_dados_linha(row, id_sequencial)
        
        # Valida e prepara dados
        sucesso_validacao, dados_preparados, erro_validacao = validar_e_preparar_dados(
            dados_estruturados, 
            id_sequencial
        )
        
        # Se falhou na validação
        if not sucesso_validacao:
            print(f"Linha {id_sequencial} ERRO na validação:")
            exibir_dados_linha(id_sequencial, dados_estruturados, mostrar_todos=True)
            print(f"   ❌ Motivo: {erro_validacao}\n")
            
            # Adiciona ao array de falhas
            linhas_com_falha.append({
                'id_sequencial': id_sequencial,
                'dados': dados_estruturados,
                'motivo_erro': erro_validacao
            })
            continue  # Pula para próxima linha
        
        # Tenta inserir no banco
        sucesso_insercao, erro_insercao = tentar_inserir_no_banco(
            dados_preparados, 
            id_sequencial
        )
        
        # Se falhou na inserção
        if not sucesso_insercao:
            print(f"Linha {id_sequencial} ERRO na inserção:")
            exibir_dados_linha(id_sequencial, dados_estruturados, mostrar_todos=True)
            print(f"   ❌ Motivo: {erro_insercao}\n")
            
            linhas_com_falha.append({
                'id_sequencial': id_sequencial,
                'dados': dados_estruturados,
                'motivo_erro': erro_insercao
            })
            continue
        
        # SUCESSO!
        linhas_importadas_com_sucesso += 1
        print(f"Linha {id_sequencial} importada ✓")
    
    # ================================================================
    # ETAPA 4: CONTAGEM FINAL
    # ================================================================
    
    print(f"\n{'='*90}")
    print(f"📊 ETAPA 4: CONTAGEM FINAL")
    print(f"{'='*90}\n")
    
    total_banco_depois = Movimentacao.objects.count()
    total_importado = total_banco_depois - total_banco_antes
    
    print(f"Total de linhas no banco (depois): {total_banco_depois:,}")
    print(f"Linhas importadas nesta execução: {total_importado:,}")
    print(f"Linhas com sucesso (contador): {linhas_importadas_com_sucesso:,}")
    print(f"Total de falhas: {len(linhas_com_falha):,}")
    
    # ================================================================
    # ETAPA 5: RELATÓRIO FINAL
    # ================================================================
    
    print(f"\n{'='*90}")
    print(f"📋 RELATÓRIO FINAL")
    print(f"{'='*90}\n")
    
    print(f"Total de linhas no arquivo: {total_linhas_arquivo:,}")
    print(f"Total de linhas no banco (antes): {total_banco_antes:,}")
    print(f"Total de linhas no banco (depois): {total_banco_depois:,}")
    print(f"Total de falhas: {len(linhas_com_falha):,}\n")
    
    if len(linhas_com_falha) > 0:
        print(f"{'='*90}")
        print(f"❌ LINHAS COM FALHA ({len(linhas_com_falha)})")
        print(f"{'='*90}\n")
        
        for falha in linhas_com_falha:
            print(f"ID: {falha['id_sequencial']}")
            exibir_dados_linha(
                falha['id_sequencial'], 
                falha['dados'], 
                mostrar_todos=True
            )
            print(f"   ❌ Motivo: {falha['motivo_erro']}\n")
            print(f"{'-'*90}\n")
    else:
        print(f"✅ Todas as linhas foram importadas com sucesso!\n")
    
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*90}\n")


# ============================================================================
# EXECUÇÃO
# ============================================================================

if __name__ == "__main__":
    importar_arquivo_detalhado(CAMINHO_ARQUIVO)