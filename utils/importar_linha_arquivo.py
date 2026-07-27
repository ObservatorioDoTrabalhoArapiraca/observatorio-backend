# cbo que nao tem
# PYTHONPATH=. python utils/importar_linha_arquivo.py --arquivo "/home/charlie/Documentos/NOVO\ CAGED/2025/202508/CAGEDMOV202508-Al-Arapiraca_filtrado.txt" --id_linha 142 

# salario vindo null
# PYTHONPATH=. python utils/importar_linha_arquivo.py --arquivo "/mnt/c/Users/Usuário/Documents/dados-pdet/_/pdet/microdados/NOVO CAGED/2022/202212/CAGEDMOV202212-Al-Arapiraca_filtrado.txt" --id_linha 181



import os
import sys
import django
import argparse
from pathlib import Path
from decimal import Decimal, InvalidOperation
from datetime import datetime

# Ajuste o caminho do projeto conforme necessário
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao
from django.core.exceptions import ValidationError

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
            elif campo_banco.startswith('ind_') or campo_banco in ['idade', 'horas_contratuais', 'competencia_mov', 'competencia_exc', 'indicador_exclusao_id']:
                dados_finais[campo_banco] = 0
            else:
                dados_finais[campo_banco] = None
            print(f"⚠️ Aviso: Campo {campo_banco} tratado com padrão devido a erro: {valor_bruto}")

    return dados_finais

def importar(arquivo, id_linha):
    try:
        # Usamos latin-1 ou iso-8859-1 se o utf-8 falhar em arquivos do governo
        with open(arquivo, 'r', encoding='utf-8') as f:
            header = f.readline().strip().split(';')
            for i, linha_texto in enumerate(f, 1):
                if i == id_linha:
                    campos = linha_texto.strip().split(';')
                    row_dict = dict(zip(header, campos))
                    
                    dados = processar_linha_caged(row_dict)
                    print(f"DEBUG - Salário processado: {dados.get('salario')} (Tipo: {type(dados.get('salario'))})")
                    obj = Movimentacao(**dados)
                    obj.full_clean()
                    obj.save()
                    print(f"✅ Sucesso! Linha {id_linha} importada no banco.")
                    return # Sai da função após sucesso
            
            print(f"❌ Linha {id_linha} não encontrada no arquivo.")
            
    except UnicodeDecodeError:
        print("❌ Erro de encoding. Tentando abrir com latin-1...")
        # Caso o arquivo do governo não esteja em UTF-8
        # Você pode repetir a lógica com encoding='latin-1' se necessário
    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--arquivo', required=True)
    parser.add_argument('--id_linha', required=True, type=int)
    args = parser.parse_args()
    
    importar(args.arquivo, args.id_linha)