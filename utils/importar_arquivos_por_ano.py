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
import argparse
from pathlib import Path
from datetime import datetime
from decimal import Decimal, InvalidOperation

import time
print("Início do script:", time.strftime("%H:%M:%S"))


parser = argparse.ArgumentParser(description='Script de importação detalhada de arquivos TXT por ano')
parser.add_argument('--ano', required=True, help='Ano a ser analisado (ex: 2020)')
parser.add_argument('--limit', type=int, default=None, help='Limite de linhas a importar (para testes)')
args = parser.parse_args()

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao
from django.core.exceptions import ValidationError


print("Antes de conectar ao banco:", time.strftime("%H:%M:%S"))
# código de conexão ao banco
print("Conectado ao banco:", time.strftime("%H:%M:%S"))

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
    if valor is None:
        return None
    # Remove aspas tipográficas (curvas), aspas comuns e espaços
    v = str(valor).replace('“', '').replace('”', '').replace('"', '').replace("'", "").strip()
    if v.upper() in ['', 'NA', 'NULL', 'NAN']:
        return None
    return v

def processar_linha_caged(row_dict):
    dados_finais = {
        'salario': Decimal('0.00'),
        'valor_salario_fixo': Decimal('0.00'),
        'horas_contratuais': 0,
        'idade': 0
    }
    
    # Normaliza as chaves do dicionário do TXT (tira espaços e põe minusculo)
    txt_normalizado = {k.strip().lower(): v for k, v in row_dict.items()}

    for campo_banco, nomes_possiveis in MAPEAMENTO_COLUNAS.items():
        valor_bruto = None
        
        # Tenta encontrar o valor usando os nomes possíveis do mapeamento
        for nome in nomes_possiveis:
            if nome in txt_normalizado:
                valor_bruto = limpar_valor(txt_normalizado[nome])
                break
        
        if valor_bruto is None:
            continue

        try:
            # 1. Tratamento para SALÁRIOS
            if campo_banco in ['salario', 'valor_salario_fixo']:
                if not valor_bruto or valor_bruto.upper() in ['NA', '0', '0,00', '0.00']:
                    dados_finais[campo_banco] = Decimal('0.00')
                else:
                    v = valor_bruto.replace(',', '.')
                    dados_finais[campo_banco] = Decimal(v)
            
            # 2. Tratamento para INDICADORES (ind_)
            elif campo_banco.startswith('ind_'):
                if not valor_bruto:
                    dados_finais[campo_banco] = 0 
                else:
                    # Garante que pegue só a parte inteira (ex: "1,00" -> 1)
                    v_limpo = valor_bruto.split(',')[0].split('.')[0]
                    dados_finais[campo_banco] = int(v_limpo)

            # 3. Tratamento para INTEIROS (idade, horas, etc)
            elif campo_banco in ['idade', 'horas_contratuais', 'saldo_movimentacao', 'competencia_mov', 'competencia_exc', 'indicador_exclusao_id']:
                if not valor_bruto or valor_bruto.upper() in ['NA', 'NULL', '']:
                    dados_finais[campo_banco] = 0
                else:
                    v_base = valor_bruto.split(',')[0].split('.')[0]
                    dados_finais[campo_banco] = int(v_base)

            # 4. Outros campos (Strings/IDs)
            else:
                dados_finais[campo_banco] = valor_bruto
                    
        except (ValueError, InvalidOperation, Exception) as e:
            # Em caso de erro em campos numéricos, define um padrão para não quebrar o save()
            if campo_banco in ['salario', 'valor_salario_fixo']:
                dados_finais[campo_banco] = Decimal('0.00')
            elif campo_banco.startswith('ind_') or campo_banco in ['idade', 'horas_contratuais', 'saldo_movimentacao', 'competencia_mov', 'competencia_exc', 'indicador_exclusao_id']:
                dados_finais[campo_banco] = 0
            else:
                dados_finais[campo_banco] = None
            print(f"⚠️ Aviso: Campo {campo_banco} tratado com padrão devido a erro: {valor_bruto}")

        except:
            continue
    return dados_finais


def obter_tipo_python(valor):
    return type(valor).__name__

def formatar_valor_para_exibicao(valor):
    if valor is None:
        return 'None'
    elif isinstance(valor, str) and len(valor) > 50:
        return f'"{valor[:50]}..."'
    else:
        return str(valor)

def exibir_dados_linha(id_sequencial, dados_estruturados, mostrar_todos=False):
    print(f"   ID: {id_sequencial}")
    campos_para_mostrar = dados_estruturados.items()
    if not mostrar_todos:
        campos_para_mostrar = list(dados_estruturados.items())[:5]
    for campo, info in campos_para_mostrar:
        valor_formatado = formatar_valor_para_exibicao(info['valor'])
        print(f"   • {campo}: {valor_formatado} ({info['tipo']})")
    if not mostrar_todos and len(dados_estruturados) > 5:
        print(f"   ... e mais {len(dados_estruturados) - 5} campos")

def validar_e_preparar_dados(dados_estruturados, id_sequencial):
    try:
        dados_preparados = {}
        colunas_disponiveis = list(dados_estruturados.keys())
        coluna_competencia = None
        for possivel_nome in ['competênciamov', 'competencia', 'Competência', 'COMPETENCIA', 'competência', 'competência_mov', 'competencia_mov']:
            if possivel_nome in dados_estruturados:
                coluna_competencia = possivel_nome
                break
        if not coluna_competencia:
            return (False, None, f"Campo 'competencia' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        comp_valor = dados_estruturados[coluna_competencia]['valor']
        if comp_valor is None:
            return (False, None, f"Campo 'competencia' está vazio (None)")
        dados_preparados['competencia_movimentacao'] = comp_valor

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
        dados_preparados['municipio_id'] = mun_valor

        coluna_salario = None
        for possivel_nome in [ 'salario', 'salário', 'Salario', 'SALARIO']:
            if possivel_nome in dados_estruturados:
                coluna_salario = possivel_nome
                break
        if not coluna_salario:
            return (False, None, f"Campo 'salario' não encontrado. Colunas disponíveis: {colunas_disponiveis[:10]}")
        sal_valor = dados_estruturados[coluna_salario]['valor']
        if sal_valor is None or sal_valor in ['', 'NA', '0', '00', ',0', ',00' ]:
            sal_valor = Decimal('0.00')
        else:
            try:
                if isinstance(sal_valor, str):
                    sal_valor = sal_valor.replace(',', '.')  # Substitui vírgula por ponto, se necessário
                # Trabalha com o valor como string para truncar as casas decimais
                sal_valor_str = str(sal_valor)
                if '.' in sal_valor_str:  # Se houver parte decimal
                    parte_inteira, parte_decimal = sal_valor_str.split('.')
                    sal_valor_str = f"{parte_inteira}.{parte_decimal[:2]}"  # Trunca para 2 casas decimais
                else:
                    sal_valor_str = f"{sal_valor_str}.00"  # Adiciona ".00" se não houver parte decimal
                sal_valor = Decimal(sal_valor_str)  # Converte para Decimal após truncar
            except Exception:
                return (False, None, f"Campo 'salario' deve ser decimal, recebeu '{sal_valor}'")
        dados_preparados['salario'] = sal_valor

        coluna_saldo = None
        for possivel_nome in ['saldomovimentação', 'saldo_movimentacao', 'saldo']:
            if possivel_nome in dados_estruturados:
                coluna_saldo = possivel_nome
                break
        if coluna_saldo:
            saldo_valor = dados_estruturados[coluna_saldo]['valor']
            if saldo_valor is not None:
                dados_preparados['saldo_movimentacao'] = saldo_valor

        if 'sexo' in dados_estruturados:
            sexo_valor = dados_estruturados['sexo']['valor']
            if sexo_valor is not None:
                dados_preparados['sexo_id'] = sexo_valor
        if 'idade' in dados_estruturados:
            idade_valor = dados_estruturados['idade']['valor']
            if idade_valor is not None and idade_valor != '':
                try: 
                    dados_preparados['idade'] = int(idade_valor)
                except Exception:
                    return (False, None, f"Campo 'idade' deve ser um número inteiro, recebeu '{idade_valor}'")
        for possivel_nome in ['raçacor', 'racacor', 'raca_cor']:
            if possivel_nome in dados_estruturados:
                raca_valor = dados_estruturados[possivel_nome]['valor']
                if raca_valor is not None:
                    dados_preparados['raca_cor_id'] = raca_valor
                break
        for possivel_nome in ['graudeinstrução', 'grauinstrucao', 'grau_instrucao']:
            if possivel_nome in dados_estruturados:
                grau_valor = dados_estruturados[possivel_nome]['valor']
                if grau_valor is not None:
                    dados_preparados['grau_instrucao_id'] = grau_valor
                break
        coluna_def = None
        for nome in ['tipodedeficiência', 'tipodeficiencia', 'tipo_deficiencia']:
            if nome in dados_estruturados:
                coluna_def = nome
                break
        if coluna_def:
            def_valor = dados_estruturados[coluna_def]['valor']
            if def_valor is not None:
                dados_preparados['tipo_deficiencia_id'] = def_valor
        return (True, dados_preparados, None)
    except Exception as e:
        return (False, None, f"Erro inesperado na validação: {str(e)}")

def tentar_inserir_no_banco(dados_preparados, id_sequencial):
    try:
        movimentacao = Movimentacao(**dados_preparados)
        movimentacao.full_clean()
        movimentacao.save()
        return (True, None)
    except ValidationError as e:
        erros = []
        for campo, mensagens in e.message_dict.items():
            erros.append(f"{campo}: {', '.join(mensagens)}")
        return (False, f"Erro de validação: {'; '.join(erros)}")
    except Exception as e:
        erro_str = str(e)
        if 'foreign key constraint' in erro_str.lower() or 'violates foreign key' in erro_str.lower():
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
        elif 'connection' in erro_str.lower() or 'timeout' in erro_str.lower():
            return (False, f"Perda de conexão com o banco: {erro_str}")
        else:
            return (False, f"Erro ao salvar no banco: {erro_str}")

def importar_arquivo_txt(caminho_arquivo, pasta, arquivo, relatorio_erros, limit=None):
    print(f"\n{'='*90}")
    print(f"📂 IMPORTAÇÃO DETALHADA DE ARQUIVO TXT")
    print(f"{'='*90}\n")
    print(f"Arquivo: {caminho_arquivo}")
    print(f"Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    # if not os.path.isfile(caminho_arquivo):
    #     print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
    #     relatorio_erros.append({'pasta': pasta, 'arquivo': arquivo, 'linha': 0, 'motivo': 'Arquivo não encontrado'})
    #     return
    # print(f"✓ Arquivo encontrado")
    try:
        print(f"⏳ Lendo arquivo TXT...")
  
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            linhas = f.readlines()
        header = linhas[0].strip().split(';')
        linhas_dados_no_arquivo = len(linhas) - 1
        print(f"📊 Linhas totais no arquivo: {linhas_dados_no_arquivo:,}")
        
        linhas_a_processar = linhas[1:limit+1] if limit else linhas[1:]
        total_a_processar = len(linhas_a_processar)
    except Exception as e:
        print(f"❌ Erro ao ler: {str(e)}")
        relatorio_erros.append({'pasta': pasta, 'arquivo': arquivo, 'linha': 0, 'motivo': f"Erro leitura: {e}"})
        return

    total_banco_antes = Movimentacao.objects.count()
    print(f"🏠 Linhas no banco antes: {total_banco_antes:,}")
    linhas_com_falha = []
    linhas_importadas_com_sucesso = 0

    for id_sequencial, linha in enumerate(linhas_a_processar, start=1):
        campos = linha.strip().split(';')
        row_dict = dict(zip(header, campos))
        
        # 1. Processa a linha usando o mapeamento de 30 colunas
        dados_preparados = processar_linha_caged(row_dict)
        
        # 2. Tenta salvar
        sucesso, erro_insercao = tentar_inserir_no_banco(dados_preparados, id_sequencial)
        
        if sucesso:
            linhas_importadas_com_sucesso += 1
            print(f"Linha {id_sequencial} de {total_a_processar} importada ✓ ")
        else:
            # 3. Só entra aqui se der erro de verdade
            print(f"Linha {id_sequencial} ❌ ERRO: {erro_insercao}")
            
            falha_info = {
                'id_sequencial': id_sequencial,
                'dados': dados_preparados,
                'motivo_erro': erro_insercao,
                'pasta': pasta,
                'arquivo': arquivo
            }
            linhas_com_falha.append(falha_info)
            relatorio_erros.append({'pasta': pasta, 'arquivo': arquivo, 'linha': id_sequencial, 'motivo': erro_insercao})

    # --- RESUMO DO ARQUIVO ---
    total_banco_agora = Movimentacao.objects.count()
    total_esperado = total_banco_antes + total_a_processar
    diferenca_final = total_esperado - total_banco_agora
    total_banco_depois = Movimentacao.objects.count()
    print(f"\n{'-'*40} RESUMO {'-'*40}")
    print(f"\n✅ Sucesso: {linhas_importadas_com_sucesso} | ❌ Falhas: {len(linhas_com_falha)}")
    print(f"📈 Linhas importadas nesta sessão: {linhas_importadas_com_sucesso}")
    print(f"🏠 Linhas no banco antes: {total_banco_antes}")
    print(f"🚀 Linhas no banco agora: {total_banco_agora}")
    print(f"🎯 Total de linhas esperado: {total_esperado}")
    print(f"Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*90}\n")
    if diferenca_final == 0:
        print(f"💎 Diferença entre o esperado e o banco: 0 (Perfeito!)")
    else:
        print(f"⚠️ Diferença entre o esperado e o banco: {diferenca_final} (Atenção!)")

    if len(linhas_com_falha) == 0:
        print(f"\n✅ Concluído: Todas as {total_a_processar} linhas foram processadas sem erros.")
    
    else:
        print(f"⚠️ O arquivo foi processado, mas houve {len(linhas_com_falha)} falhas.\n")

def importar_todos_os_arquivos_do_ano(ano, limit=None):
    # base_dir = f'/home/charlie/Documentos/NOVO CAGED/{ano}'
    base_dir = f'/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/{ano}'
    relatorio_erros = []
    total_linhas_analisadas = 0
    total_banco_antes = Movimentacao.objects.count()
    for pasta in sorted(os.listdir(base_dir)):
        pasta_path = os.path.join(base_dir, pasta)
        if not os.path.isdir(pasta_path):
            continue
        for arquivo in sorted(os.listdir(pasta_path)):
            if arquivo.endswith('.txt'):
                caminho_arquivo = os.path.join(pasta_path, arquivo)
                print(f"Importando: {caminho_arquivo}")
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    linhas = f.readlines()
                linhas_a_processar = linhas[1:]
                if limit:
                    linhas_a_processar = linhas_a_processar[:limit]
                total_linhas_analisadas += len(linhas_a_processar)
                importar_arquivo_txt(caminho_arquivo, pasta, arquivo, relatorio_erros, limit)
                total_banco_depois = Movimentacao.objects.count()
    print("\n" + "="*90)
    print("RELATÓRIO FINAL DE ERROS (GERAL)")
    print("="*90)
    print(f"Total de linhas analisadas: {total_linhas_analisadas:,}")
    print(f"Total de linhas no banco (antes): {total_banco_antes:,}")
    print(f"Total de linhas no banco (depois): {total_banco_depois:,}")
    print(f"Total estimado de linhas no banco : {total_banco_antes + total_linhas_analisadas:,}")
    print(f"Diferença do estimado para o que tem no banco : {total_banco_depois - (total_banco_antes + total_linhas_analisadas):,}")
    if relatorio_erros:
        for erro in relatorio_erros:
            print(f"Pasta: {erro['pasta']} | Arquivo: {erro['arquivo']} | Linha: {erro['linha']} | Motivo: {erro['motivo']}")
    else:
        print("✅ Todos os arquivos importados sem erros.")
    print("="*90)

if __name__ == "__main__":
    importar_todos_os_arquivos_do_ano(args.ano, args.limit)