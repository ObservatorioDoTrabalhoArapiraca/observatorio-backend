from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import  Integer, String, and_, case, cast, desc, func, literal, not_, or_
from typing import List, Optional, Union
import math
from ..analisesSchemas import AnaliseGrauInstrucaoRaisResult, AnaliseIdadeResult, AnaliseSalarioOcupacaoRaisResult,  AnaliseSetorResult, AnaliseVinculoCBORaisResult, PaginatedAnalise, AnaliseSexoResult
from ..database import get_db
from ..models import SetorAgregado, MovimentacoesRais
from api.core import models

router = APIRouter(prefix="/analises/rais")

def build_pagination_urls(request: Request, page: int, total_pages: int, page_size: int, extra_params: dict):
    """Gera as URLs de next/previous para a paginação."""
    def get_url(p):
        if p < 1 or p > total_pages:
            return None
        base = str(request.url).split("?")[0]
        params = [f"page={p}", f"page_size={page_size}"]
        for k, v in extra_params.items():
            if v is not None:
                params.append(f"{k}={v}")
        return f"{base}?{'&'.join(params)}"
    return get_url(page + 1), get_url(page - 1)


def paginar(all_results, page: int, page_size: int):
    """Fatia a lista completa para a página atual."""
    start = (page - 1) * page_size
    return all_results[start: start + page_size]


def obter_nome_setor_rais(classe_cnae: str, referencias: list) -> str:
    if not classe_cnae:
        return "Não informado"
    
    try:
        # Extrai os 2 primeiros dígitos (Divisão) da Classe (ex: '10112' -> 10)
        divisao = int(str(classe_cnae)[:2])
    except (ValueError, TypeError):
        return "CNAE Inválido"

    for ref in referencias:
        # Verifica se a divisão está no intervalo (ex: 10 entre 10 e 33)
        if ref.divisao_inicio and ref.divisao_fim:
            if ref.divisao_inicio <= divisao <= ref.divisao_fim:
                return ref.denominacao
        elif ref.divisao_inicio == divisao:
            return ref.denominacao
            
    return "Setor não especificado"

@router.get("/setor", response_model=Union[PaginatedAnalise[AnaliseSetorResult], List[AnaliseSetorResult]])
def get_analise_setor_rais(
    request: Request,
    ano: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Busca referências de setores (mesma tabela do CAGED)
    referencias = db.query(SetorAgregado).all()

    # 2. Query na tabela da RAIS
    # Usando MovimentacaoRais (ou o nome que você deu ao seu Model da RAIS)
    columns = [
        MovimentacoesRais.ano_base.label("ano"),
        MovimentacoesRais.cnae_2_0_classe.label("classe"),
        func.count(MovimentacoesRais.id).label("total")
    ]
    
    query = db.query(*columns)
    
    if ano:
        query = query.filter(MovimentacoesRais.ano_base == ano)
    
    # Agrupamos por ano e classe para processar no Python
    dados_brutos = query.group_by(MovimentacoesRais.ano_base, MovimentacoesRais.cnae_2_0_classe).all()

    # 3. AGRUPAMENTO EM MEMÓRIA (Montinhos por Setor)
    consolidado = {}

    for row in dados_brutos:
        nome_setor = obter_nome_setor_rais(row.classe, referencias)
        
        # Chave: (ano, nome_setor)
        chave = (row.ano, nome_setor)
        
        if chave not in consolidado:
            consolidado[chave] = 0
        consolidado[chave] += row.total

    # 4. Cálculo de totais por ano para o percentual
    totais_por_ano = {}
    for (a, s), valor in consolidado.items():
        totais_por_ano[a] = totais_por_ano.get(a, 0) + valor

    # 5. Montagem da lista final
    lista_processada = []
    for (a, s), total in consolidado.items():
        total_anual = totais_por_ano[a]
        perc = (total / total_anual * 100) if total_anual > 0 else 0
        
        lista_processada.append({
            "ano": a,
            "setor_denominacao": s,
            "total_movimentacoes": total,
            "percentual": f"{perc:.2f}",
            "secao": "Consolidado RAIS" # Adaptado para o seu schema
        })

    # 6. Ordenação (Ano desc, Total desc)
    lista_processada.sort(key=lambda x: (x['ano'], x['total_movimentacoes']), reverse=True)

    if not pagination:
        return lista_processada
    # 7. PAGINAÇÃO MANUAL
    total_registros = len(lista_processada)
    total_pages = math.ceil(total_registros / page_size)
    
    inicio = (page - 1) * page_size
    dados_paginados = lista_processada[inicio : inicio + page_size]

    extra_params = {"ano": ano}
    next_url, prev_url = build_pagination_urls(request, page, total_pages, page_size, extra_params)

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": dados_paginados,
    }
    

@router.get("/sexo", response_model=Union[PaginatedAnalise[AnaliseSexoResult], List[AnaliseSexoResult]])
def get_analise_sexo_rais(
    request: Request,
    ano: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Query Principal (RAIS é anual, não temos agregação mensal)
    query = db.query(
        MovimentacoesRais.ano_base.label("ano"),
        MovimentacoesRais.sexo_trabalhador.label("sexo_id"), 
        func.count(MovimentacoesRais.id).label("total")
    )
      
    
    if ano:
        query = query.filter(MovimentacoesRais.ano_base == ano)
    
    # Agrupamos por ano e pelo ID do sexo
    db_results = query.group_by(MovimentacoesRais.ano_base, MovimentacoesRais.sexo_trabalhador).all()

    # 2. Cálculo de totais por ano para o percentual
    totais_por_ano = {}
    for row in db_results:
        totais_por_ano[row.ano] = totais_por_ano.get(row.ano, 0) + row.total

    # 3. Processamento e Mapeamento Manual (Inferência de Sexo)
    processed_results = []
    for row in db_results:
        total_anual = totais_por_ano[row.ano]
        perc = (row.total / total_anual * 100) if total_anual > 0 else 0
        current_sexo = row.sexo_id
        # Lógica de inferência solicitada
        try:
            val_sexo = int(current_sexo)
        except (ValueError, TypeError):
            val_sexo = 0

        if val_sexo == 1:
            descricao = "Masculino"
        elif val_sexo == 2:
            descricao = "Feminino"
        else:
            descricao = "Não identificado"

        processed_results.append({
            "ano": row.ano,
            "sexo": str(val_sexo),
            "sexo_descricao": descricao,
            "total_movimentacoes": row.total,
            "percentual": f"{perc:.2f}"
        })

    # 4. Ordenação (Ano desc, Descrição asc)
    processed_results.sort(key=lambda x: (x['ano'], x['sexo_descricao']), reverse=True)

    # --- LÓGICA DE RETORNO CONDICIONAL ---
    if not pagination:
        return processed_results

    # 5. Paginação Manual
    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    
    inicio = (page - 1) * page_size
    fim = inicio + page_size
    paginated_results = processed_results[inicio:fim]

    extra_params = {"ano": ano, "pagination": pagination}
    next_url, prev_url = build_pagination_urls(
        request, page, total_pages, page_size, extra_params
    )

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }

MAPEAMENTO_FAIXAS = {
    1: '10 A 14 anos',
    2: '15 A 17 anos',
    3: '18 A 24 anos',
    4: '25 A 29 anos',
    5: '30 A 39 anos',
    6: '40 A 49 anos',
    7: '50 A 64 anos',
    8: '65 anos ou mais'
}

@router.get("/faixa-etaria", response_model=Union[PaginatedAnalise[AnaliseIdadeResult], List[AnaliseIdadeResult]])
def get_analise_faixa_etaria_rais(
    request: Request,
    ano: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True),
    db: Session = Depends(get_db)
):
    # 1. Mapeamento das faixas conforme sua definição
    # Usamos um dicionário para busca rápida no processamento
   

    # 2. Query Principal
    # Assumindo que o campo na RAIS se chama 'faixa_etaria' ou similar
    # Ajuste o nome da coluna se for diferente no seu model MovimentacoesRais
    columns = [
        MovimentacoesRais.ano_base.label("ano"),
        MovimentacoesRais.faixa_etaria.label("faixa_id"), 
        func.count(MovimentacoesRais.id).label("total")
    ]
    
    query = db.query(*columns).filter(MovimentacoesRais.faixa_etaria.isnot(None))
    
    if ano:
        query = query.filter(MovimentacoesRais.ano_base == ano)
    
    # Agrupamos por ano e pelo ID da faixa
    db_results = query.group_by(MovimentacoesRais.ano_base, MovimentacoesRais.faixa_etaria).all()

    # 3. Cálculo de totais por ano para o percentual
    totais_por_ano = {}
    for row in db_results:
        totais_por_ano[row.ano] = totais_por_ano.get(row.ano, 0) + row.total

    # 4. Processamento dos resultados
    processed_results = []
    for row in db_results:
        total_anual = totais_por_ano[row.ano]
        perc = (row.total / total_anual * 100) if total_anual > 0 else 0
        
        # Obtém a descrição do dicionário ou 'Não informado' se o ID não existir
        descricao = MAPEAMENTO_FAIXAS.get(row.faixa_id, "Não informado")

        processed_results.append({
            "ano": row.ano,
            "faixa_etaria": descricao,
            "total_movimentacoes": row.total,
            "percentual": f"{perc:.2f}"
        })

    # 5. Ordenação (Ano desc, Faixa etária)
    # Dica: Se quiser ordenar as faixas logicamente (10-14 antes de 15-17), 
    # pode ser necessário incluir o ID na ordenação.
    processed_results.sort(key=lambda x: (x['ano'], x['faixa_etaria']), reverse=True)

    # --- LÓGICA DE RETORNO CONDICIONAL ---
    if not pagination:
        return processed_results

    # 6. Paginação Manual
    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    
    inicio = (page - 1) * page_size
    fim = inicio + page_size
    paginated_results = processed_results[inicio:fim]

    extra_params = {"ano": ano, "pagination": pagination}
    next_url, prev_url = build_pagination_urls(
        request, page, total_pages, page_size, extra_params
    )

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }
    
@router.get("/grau-instrucao", response_model=Union[PaginatedAnalise[AnaliseGrauInstrucaoRaisResult], List[AnaliseGrauInstrucaoRaisResult]])
def get_analise_grau_instrucao_rais(
    request: Request,
    ano: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True),
    db: Session = Depends(get_db)
):
    # 1. Busca as referências no banco (inclui o -1 como 'Ignorado')
    referencias = db.query(models.GrauDeInstrucaoRaisReferencia).all()
    MAPEAMENTO_INSTRUCAO = {str(ref.codigo): ref.descricao for ref in referencias}

    # 2. Query Principal
    columns = [
        MovimentacoesRais.ano_base.label("ano"),
        MovimentacoesRais.escolaridade_apos_2005.label("instrucao_id"), 
        func.count(MovimentacoesRais.id).label("total")
    ]
    
    query = db.query(*columns)
    
    if ano:
        query = query.filter(MovimentacoesRais.ano_base == ano)
    
    db_results = query.group_by(MovimentacoesRais.ano_base, MovimentacoesRais.escolaridade_apos_2005).all()

    # 3. Totais para percentual
    totais_por_ano = {}
    for row in db_results:
        totais_por_ano[row.ano] = totais_por_ano.get(row.ano, 0) + row.total

    # 4. Processamento com distinção entre Ignorado (-1) e Vazio
    processed_results = []
    for row in db_results:
        total_anual = totais_por_ano[row.ano]
        perc = (row.total / total_anual * 100) if total_anual > 0 else 0
        
        # Valor bruto do banco
        raw_id = row.instrucao_id
        
        # LÓGICA DE DESCRIÇÃO:
        if raw_id is None or str(raw_id).strip() in ["", "nan", "None"]:
            instrucao_codigo = 0  # Ou algum valor padrão inteiro se o Pydantic exigir int
            descricao = "Não informado"
        else:
            # Mantemos o código original (tentando converter para int se possível para o Pydantic)
            try:
                instrucao_codigo = int(raw_id)
            except (ValueError, TypeError):
                instrucao_codigo = 0 # Fallback se o código não for numérico
                
            descricao = MAPEAMENTO_INSTRUCAO.get(str(raw_id), "Não informado")

        # IMPORTANTE: As chaves aqui devem ser EXATAMENTE as que estão no AnaliseGrauInstrucaoRaisResult
        processed_results.append({
            "ano": row.ano,
            "grau_instrucao": instrucao_codigo,         # O ID numérico
            "grau_instrucao_descricao": descricao,    # A descrição textual
            "total_movimentacoes": row.total,
            "percentual": f"{perc:.2f}"
        })


    # 5. Ordenação (Ano desc, Total de movimentações desc)
    processed_results.sort(key=lambda x: (x['ano'], x['total_movimentacoes']), reverse=True)

    # --- LÓGICA DE PAGINAÇÃO ---
    if not pagination:
        return processed_results

    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    
    inicio = (page - 1) * page_size
    fim = inicio + page_size
    paginated_results = processed_results[inicio:fim]

    extra_params = {"ano": ano, "pagination": pagination}
    next_url, prev_url = build_pagination_urls(
        request, page, total_pages, page_size, extra_params
    )

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }


@router.get("/vinculo-cbo", response_model=Union[PaginatedAnalise[AnaliseVinculoCBORaisResult], List[AnaliseVinculoCBORaisResult]])
def get_analise_vinculo_cbo_rais(
    request: Request,
    ano: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True),
    db: Session = Depends(get_db)
):
    # 1. Carregar referências de CBO para o "De-Para" de descrições
    referencias_cbo = db.query(models.Cbo2002OcupacaoReferencia).all()
    mapa_cbo = {str(ref.codigo): ref.descricao for ref in referencias_cbo}
    
    referencias_horas = db.query(models.FaixaHorasContratualRaisReferencia).all()
    mapa_horas = {str(ref.codigo): ref.descricao for ref in referencias_horas}

    # 2. Query Principal agrupando por CBO e Horas
    columns = [
        MovimentacoesRais.ano_base.label("ano"),
        MovimentacoesRais.cbo_ocupacao_2002.label("cbo_id"),
        MovimentacoesRais.qtd_hora_contr.label("horas"),
        MovimentacoesRais.faixa_hora_contrat.label("faixa_id"),
        func.count(MovimentacoesRais.id).label("total")
    ]
    
    query = db.query(*columns)
    
    if ano:
        query = query.filter(MovimentacoesRais.ano_base == ano)
    
    # Agrupamento multi-colunas
    db_results = query.group_by(
        MovimentacoesRais.ano_base, 
        MovimentacoesRais.cbo_ocupacao_2002,
        MovimentacoesRais.qtd_hora_contr,
        MovimentacoesRais.faixa_hora_contrat
    ).all()

    # 3. Totais por ano para cálculo de percentual
    totais_por_ano = {}
    for row in db_results:
        totais_por_ano[row.ano] = totais_por_ano.get(row.ano, 0) + row.total

    # 5. Processamento e De-Para
    processed_results = []
    for row in db_results:
        total_anual = totais_por_ano[row.ano]
        perc = (row.total / total_anual * 100) if total_anual > 0 else 0
        
        cbo_id_str = str(row.cbo_id).strip() if row.cbo_id else "0"
        faixa_id_str = str(row.faixa_id).zfill(2) if row.faixa_id else "00" # zfill garante "01" em vez de "1"

        processed_results.append({
            "ano": row.ano,
            "mes": None, # Conforme seu exemplo
            "total_movimentacoes": row.total,
            "percentual": f"{perc:.2f}",
            "cbo_codigo": cbo_id_str,
            "cbo_descricao": mapa_cbo.get(cbo_id_str, "CBO não identificado"),
            "qtd_hora_contr": row.horas,
            "faixa_hora_contrat": row.faixa_id,
            "faixa_hora_contrat_descricao": mapa_horas.get(faixa_id_str, "Não informado")
        })
        
    
    processed_results.sort(key=lambda x: (x['ano'], x['total_movimentacoes']), reverse=True)

    # --- LÓGICA DE RETORNO (Onde estava o erro) ---
    if not pagination:
        return processed_results

    # 6. Paginação Manual
    total_registros = len(processed_results)
    
    # Tratamento para lista vazia
    if total_registros == 0:
        return {
            "count": 0,
            "total_pages": 0,
            "current_page": page,
            "page_size": page_size,
            "next": None,
            "previous": None,
            "results": []
        }

    total_pages = math.ceil(total_registros / page_size)
    inicio = (page - 1) * page_size
    fim = inicio + page_size
    paginated_results = processed_results[inicio:fim]

    # Parâmetros para os links de próxima/anterior
    extra_params = {"ano": ano, "pagination": pagination}
    next_url, prev_url = build_pagination_urls(
        request, page, total_pages, page_size, extra_params
    )

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results
    }
        
        
@router.get("/salario-ocupacao", response_model=Union[PaginatedAnalise[AnaliseSalarioOcupacaoRaisResult], List[AnaliseSalarioOcupacaoRaisResult]])
def get_analise_salario_ocupacao_rais(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True),
    db: Session = Depends(get_db)
):
    
    referencias = db.query(models.SalarioBaseReferencia).order_by(models.SalarioBaseReferencia.desde.asc()).all()
    # 1. Mapeamento de colunas da RAIS
    meses_map = {
        1: "vl_rem_janeiro_sc", 2: "vl_rem_fevereiro_sc", 3: "vl_rem_marco_sc",
        4: "vl_rem_abril_sc", 5: "vl_rem_maio_sc", 6: "vl_rem_junho_sc",
        7: "vl_rem_julho_sc", 8: "vl_rem_agosto_sc", 9: "vl_rem_setembro_sc",
        10: "vl_rem_outubro_sc", 11: "vl_rem_novembro_sc"
    }

    # 2. Buscar referências de salário mínimo
    referencias = db.query(models.SalarioBaseReferencia).order_by(models.SalarioBaseReferencia.desde.asc()).all()

    def montar_case_minimo_dinamico(mes_num):
        """
        Gera uma expressão CASE SQL que retorna o salário mínimo 
        baseado na coluna MovimentacoesRais.ano_base para um mês específico.
        """
        whens = []
        for ref in referencias:
            ano_ref = int(str(ref.desde)[:4])
            mes_ref = int(str(ref.desde)[4:])
            
            # Condição: Se o ano_base da linha for MAIOR que o ano da ref, 
            # ou se for o MESMO ANO mas o mês analisado for >= ao mês da ref
            condicao = (models.MovimentacoesRais.ano_base > ano_ref) | \
                       ((models.MovimentacoesRais.ano_base == ano_ref) & (mes_num >= mes_ref))
            
            whens.append((condicao, float(ref.valor)))
        
        # Invertemos para pegar sempre a referência mais recente (maior competência)
        return case(*reversed(whens), else_=0.0)

    # 3. Construção dos campos da Query
    lista_meses = [mes] if (mes and agregacao == "mensal") else range(1, 12)
    # Soma dos salários válidos e contador de quantos meses entraram na média
    soma_salarios_validos = literal(0.0)
    qtd_meses_validos = literal(0)
    
    # Contadores de linhas (vínculos) inválidos
    # Uma linha é mov_zero se TODOS os meses analisados forem null/0
    # Uma linha é mov_low se possuir valores > 0 mas TODOS abaixo do mínimo
    condicoes_zero = []
    condicoes_low = []
    condicoes_validas = []

    for m in lista_meses:
        col_obj = getattr(models.MovimentacoesRais, meses_map[m])
        minimo_dinamico = montar_case_minimo_dinamico(m)

        is_valid = (col_obj >= minimo_dinamico)
        
        # IMPORTANTE: Aqui somamos os valores válidos
        # Usamos SUM para que o banco saiba que é uma agregação
        soma_salarios_validos += func.sum(case((is_valid, col_obj), else_=0))
        qtd_meses_validos += func.sum(case((is_valid, 1), else_=0))

        # Para as condições de linha (zero/low), como vamos usar dentro de um SUM global,
        # elas precisam ser avaliadas por registro. 
        # A lógica abaixo deve ser montada como uma expressão booleana para o CASE.
        is_zero = (col_obj == None) | (col_obj == 0)
        is_low = (col_obj > 0) & (col_obj < minimo_dinamico)

        condicoes_zero.append(is_zero)
        condicoes_low.append(is_low)
        condicoes_validas.append(is_valid)

    # Definição de linha inválida (Lógica: se nenhum mês foi válido)
    # mov_zero: todos os meses são zero
    linha_is_zero = and_(*condicoes_zero)
    # mov_low: não tem nenhum válido, e tem pelo menos um 'low'
    linha_is_low = and_(not_(or_(*condicoes_validas)), or_(*condicoes_low))

    # 4. Colunas da Query
    columns = [
        models.MovimentacoesRais.ano_base.label("ano"),
        models.MovimentacoesRais.cbo_ocupacao_2002.label("cbo_codigo"),
        models.Cbo2002OcupacaoReferencia.descricao.label("cbo_descricao"),
        # Média das somas
        (soma_salarios_validos / func.nullif(qtd_meses_validos, 0)).label("salario_medio"),
        func.count(models.MovimentacoesRais.id).label("total_movimentacoes"),
        func.sum(case((linha_is_zero, 1), else_=0)).label("mov_zero"),
        func.sum(case((linha_is_low, 1), else_=0)).label("mov_low")
    ]

    group_by = [
        models.MovimentacoesRais.ano_base,
        models.MovimentacoesRais.cbo_ocupacao_2002,
        models.Cbo2002OcupacaoReferencia.descricao
    ]

    if agregacao == "mensal" and mes:
        columns.append(literal(mes).label("mes"))
        group_by.append(literal(mes))
        # No mensal, a média já é natural pois lista_meses_processar só tem 1 item

    # 5. Execução
    query = db.query(*columns).join(
        models.Cbo2002OcupacaoReferencia,
        models.MovimentacoesRais.cbo_ocupacao_2002 == cast(models.Cbo2002OcupacaoReferencia.codigo, String)
    )

    if ano:
        query = query.filter(models.MovimentacoesRais.ano_base == ano)

    all_results = query.group_by(*group_by).order_by(
        models.MovimentacoesRais.ano_base.desc(),
        desc("salario_medio")
    ).all()

    # 6. Formatação Final
    processed_list = []
    for item in all_results:
        processed_list.append({
            "ano": item.ano,
            "mes": getattr(item, 'mes', None),
            "cbo_codigo": item.cbo_codigo,
            "cbo_descricao": item.cbo_descricao or "Não informado",
            "salario_medio": round(float(item.salario_medio or 0), 2),
            "total_movimentacoes": item.total_movimentacoes,
            "mov_low": int(item.mov_low or 0),
            "mov_zero": int(item.mov_zero or 0),
        })

    if not pagination:
        return processed_list

    # Paginação Manual
    total_registros = len(processed_list)
    total_pages = math.ceil(total_registros / page_size)
    inicio = (page - 1) * page_size
    fim = inicio + page_size
    
    next_url, prev_url = build_pagination_urls(
        request, page, total_pages, page_size,
        {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination}
    )

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": processed_list[inicio:fim],
    }

@router.get("/total-movimentacoes", response_model=Union[PaginatedAnalise[dict], dict])
def get_movimentacoes_rais_detalhadas(
    request: Request,
    db: Session = Depends(get_db),
    detalhes: bool = Query(True, description="Retornar detalhes das movimentações"),
    ano: Optional[int] = Query(None, description="Filtrar por ano base"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    pagination: bool = Query(True)
):
    # 1. Query mínima apenas para contagem e filtros básicos
    query_base = db.query(models.MovimentacoesRais)
    
    if ano:
        query_base = query_base.filter(models.MovimentacoesRais.ano_base == ano)
    
    total_movimentacoes = query_base.count()
    
    # 2. Resposta simplificada se detalhes for False
    response_resumo = {
        "total_movimentacoes": total_movimentacoes,
        "filtros_aplicados": {
            "ano": ano,
            "detalhes": detalhes
        }
    }
    
    if not detalhes:
        return response_resumo

    # 3. Query Detalhada (SÓ EXECUTA SE detalhes=True)
    # Aqui selecionamos as múltiplas tabelas para o JOIN manual
    query_detalhada = db.query(
        models.MovimentacoesRais,
        models.MunicipioReferencia,
        models.Cbo2002OcupacaoReferencia,
        models.SexoReferencia,
        models.RacaCorReferencia,
        models.GrauInstrucaoReferencia
    ).join(
        models.MunicipioReferencia, 
        cast(models.MovimentacoesRais.mun_trab, String) == cast(models.MunicipioReferencia.codigo, String)
    ).join(
        models.Cbo2002OcupacaoReferencia,
        cast(models.MovimentacoesRais.cbo_ocupacao_2002, String) == cast(models.Cbo2002OcupacaoReferencia.codigo, String)
    ).join(
        models.SexoReferencia,
        models.MovimentacoesRais.sexo_trabalhador == models.SexoReferencia.codigo
    ).join(
        models.RacaCorReferencia,
        models.MovimentacoesRais.raca_cor == models.RacaCorReferencia.codigo
    ).join(
        models.GrauInstrucaoReferencia,
        models.MovimentacoesRais.escolaridade_apos_2005 == models.GrauInstrucaoReferencia.codigo
    )

    # Reaplicar filtro de ano na query detalhada
    if ano:
        query_detalhada = query_detalhada.filter(models.MovimentacoesRais.ano_base == ano)

    # 4. Paginação e Execução
    total_pages = math.ceil(total_movimentacoes / page_size)
    offset = (page - 1) * page_size
    registros_tuplas = query_detalhada.offset(offset).limit(page_size).all()
    
    resultados = []
    for reg, mun_ref, cbo_ref, sexo_ref, raca_ref, esc_ref in registros_tuplas:
        resultados.append({
            "id": reg.id,
            "ano_base": reg.ano_base,
            "municipio_codigo": reg.mun_trab,
            "municipio_descricao": mun_ref.descricao if mun_ref else "Não encontrado",
            "cbo_codigo": reg.cbo_ocupacao_2002,
            "cbo_descricao": cbo_ref.descricao if cbo_ref else "Não encontrado",
            "idade": reg.idade,
            "sexo": sexo_ref.descricao if sexo_ref else "Não informado",
            "raca_cor": raca_ref.descricao if raca_ref else "Não informado",
            "escolaridade": esc_ref.descricao if esc_ref else "Não informado",
            "remun_media_nom": float(reg.vl_remun_media_nom or 0),
            "tempo_emprego": float(reg.tempo_emprego or 0),
            "vinculo_ativo_31_12": bool(reg.vinculo_ativo_31_12)
        })

    next_url, prev_url = build_pagination_urls(
        request, page, total_pages, page_size, {"ano": ano, "detalhes": detalhes}
    )

    return {
        **response_resumo,
        "paginacao": {
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "links": {"next": next_url, "previous": prev_url}
        },
        "resultados": resultados
    }