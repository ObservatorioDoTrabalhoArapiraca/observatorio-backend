import os
import sys
import django
import argparse
from pathlib import Path
from decimal import Decimal, InvalidOperation
from django import db

# Setup do Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.movimentacoes.models import Movimentacao

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

def importar_desde(arquivo, linha_inicial, limite=None, lote_tamanho=1000):
    try:
        # Tenta abrir com UTF-8, se falhar tenta Latin-1
        try:
            f = open(arquivo, 'r', encoding='utf-8')
            header_line = f.readline()
        except UnicodeDecodeError:
            f = open(arquivo, 'r', encoding='latin-1')
            header_line = f.readline()

        header = [h.strip().lower() for h in header_line.strip().split(';')]
        
        batch = []
        cont_sucesso = 0
        
        print(f"🚀 Arquivo: {os.path.basename(arquivo)}")
        print(f"📍 Começando na linha: {linha_inicial}")
        if limite:
            print(f"🛑 MODO TESTE: Importando apenas {limite} linha(s).")
        else:
            print(f"🛰️ MODO PRODUÇÃO: Importando até o final do arquivo.")

        for i, linha_texto in enumerate(f, 1):
            # 1. Pula até chegar na linha inicial
            if i < linha_inicial:
                continue
            
            # 2. Lógica do Limite
            if limite and cont_sucesso >= limite:
                break

            campos = linha_texto.strip().split(';')
            if len(campos) < len(header):
                continue
                
            row_dict = dict(zip(header, campos))
            dados = processar_linha_caged(row_dict)
            
            # Adiciona ao lote ou salva direto se for apenas uma linha
            if limite == 1:
                obj = Movimentacao(**dados)
                obj.save()
                print(f"✅ Linha {i} importada individualmente para teste.")
                cont_sucesso += 1
                break # Encerra após a única linha de teste
            else:
                batch.append(Movimentacao(**dados))
                cont_sucesso += 1

            # Salva em lotes para performance
            if len(batch) >= lote_tamanho:
                Movimentacao.objects.bulk_create(batch)
                print(f"✅ {cont_sucesso} registros... (Linha atual: {i})")
                batch = []
                db.reset_queries()

        # Salva o restante
        if batch:
            Movimentacao.objects.bulk_create(batch)
            
        print(f"🎉 Concluído! Total de registros inseridos: {cont_sucesso}")
        f.close()

    except Exception as e:
        print(f"❌ Erro fatal na linha {i if 'i' in locals() else '?'}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--arquivo', required=True)
    parser.add_argument('--id_linha', required=True, type=int, help="Linha por onde começar")
    parser.add_argument('--limite', type=int, default=None, help="Quantidade de linhas para importar (deixe vazio para importar tudo)")
    args = parser.parse_args()
    
    importar_desde(args.arquivo, args.id_linha, args.limite)