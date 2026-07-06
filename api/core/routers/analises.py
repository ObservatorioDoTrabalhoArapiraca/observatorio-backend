from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, case, func, cast, String, desc, literal
from typing import List, Optional, Union
import math
from ..analisesSchemas import AnaliseGrauInstrucaoResult, AnaliseIdadeResult, AnaliseOcupacaoResult, AnaliseRacaCorResult, AnaliseSalarioOcupacaoResult, AnaliseSaldoOcupacaoResult, AnaliseSaldoOcupacaoResult, AnaliseSetorResult, AnaliseTipoDeficienciaResult, MovimentacoesResponse, PaginatedAnalise, AnaliseSexoResult
from ..database import get_db
from ..models import Cbo2002OcupacaoReferencia, GrauInstrucaoReferencia, Movimentacoes, RacaCorReferencia, SetorAgregado, SexoReferencia, TipoDeficienciaReferencia, SalarioBaseReferencia, MovimentacoesRais

router = APIRouter(prefix="/analises")

def get_saldo_columns():
    return [
        func.count(Movimentacoes.id).label('total_movimentacoes'),
        func.sum(Movimentacoes.saldo_movimentacao).label('saldo_movimentacoes'),
        func.sum(case((Movimentacoes.saldo_movimentacao > 0, Movimentacoes.saldo_movimentacao), else_=0)).label('total_admissoes'),
        func.sum(case((Movimentacoes.saldo_movimentacao < 0, func.abs(Movimentacoes.saldo_movimentacao)), else_=0)).label('total_demissoes'),
    ]

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

@router.get("/sexo", response_model=Union[PaginatedAnalise[AnaliseSexoResult], List[AnaliseSexoResult]])
def get_analise_sexo(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Base da Query com Join para pegar a descrição
    # Assumindo que no modelo Movimentacao a coluna de data/competencia permita extrair ano/mes
    # Se 'competencia' for 202501 (int), tratamos como tal:
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100

    # Campos que vamos selecionar
    columns = [
        col_ano.label("ano"),
        cast(Movimentacoes.sexo_id, String).label("sexo"),
        SexoReferencia.descricao.label("sexo_descricao"),
        *get_saldo_columns()
    ]

    group_by = [col_ano, Movimentacoes.sexo_id, SexoReferencia.descricao]

    if agregacao == "mensal":
        columns.insert(1, col_mes.label("mes"))
        group_by.insert(1, col_mes)

    # 2. Query Principal com Agrupamento
    query = db.query(*columns).join(
        SexoReferencia, Movimentacoes.sexo_id == SexoReferencia.codigo
    )

    # 3. Filtros
    if ano:
        query = query.filter(col_ano == ano)
    if mes:
        query = query.filter(col_mes == mes)
    
    all_db_results = query.group_by(*group_by).order_by(col_ano.desc()).all()
    
    processed_results = []
    for item in all_db_results:
        # Cálculo da soma do grupo (ano ou ano/mês) para o percentual
        soma_grupo = sum(
            r.total_movimentacoes for r in all_db_results
            if r.ano == item.ano and (agregacao == "anual" or r.mes == item.mes)
        )
        
        perc = (item.total_movimentacoes / soma_grupo * 100) if soma_grupo > 0 else 0
        
        res = {
            "ano": item.ano,
            "sexo": item.sexo,
            "sexo_descricao": "Masculino" if item.sexo_descricao == "Homem" else "Feminino" if item.sexo_descricao == "Mulher" else item.sexo_descricao,
            "total_movimentacoes": int(item.total_movimentacoes or 0),
            "saldo_movimentacoes": int(item.saldo_movimentacoes or 0),
            "total_admissoes": int(item.total_admissoes or 0),
            "total_demissoes": int(item.total_demissoes or 0),
            "percentual": f"{perc:.2f}",
            
        }
        
        if hasattr(item, 'mes'):
            res["mes"] = item.mes
            
        processed_results.append(res)

    # --- LÓGICA DE RETORNO CONDICIONAL ---
    
    if not pagination:
        return processed_results

    # Paginação manual da lista processada
    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    paginated_results = processed_results[(page - 1) * page_size: page * page_size]
    next_url, prev_url = build_pagination_urls(request, page, total_pages, page_size, {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination})


    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }


# FAIXAS_ETARIAS = [
#     (0, 14, '10 A 14 anos'),
#     (15, 17, '15 A 17 anos'),
#     (18, 24, '18 A 24 anos'),
#     (25, 29, '25 A 29 anos'),
#     (30, 39, '30 A 39 anos'),
#     (40, 49, '40 A 49 anos'),
#     (50, 64, '50 A 64 anos'),
#     (65, 999, '65 anos ou mais'),
# ]

    
# def get_faixa_etaria(idade):
#     """Retorna a faixa etária de uma idade"""
#     if idade is None:
#         return None
    
#     for min_idade, max_idade, descricao in FAIXAS_ETARIAS:
#         if min_idade <= idade <= max_idade:
#             return descricao
#     return None

@router.get("/idade", response_model=Union[PaginatedAnalise[AnaliseIdadeResult], List[AnaliseIdadeResult]])
def get_distribuicao_idade(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Extrair ano e mês da competência
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100

    # 2. Criar a expressão CASE para faixas etárias
    faixa_etaria = case(
        (Movimentacoes.idade.between(0, 14), '10 A 14 anos'),
        (Movimentacoes.idade.between(15, 17), '15 A 17 anos'),
        (Movimentacoes.idade.between(18, 24), '18 A 24 anos'),
        (Movimentacoes.idade.between(25, 29), '25 A 29 anos'),
        (Movimentacoes.idade.between(30, 39), '30 A 39 anos'),
        (Movimentacoes.idade.between(40, 49), '40 A 49 anos'),
        (Movimentacoes.idade.between(50, 64), '50 A 64 anos'),
        (Movimentacoes.idade >= 65, '65 anos ou mais'),
        else_='Não informado'
    ).label("faixa_etaria")

    # 3. Campos que vamos selecionar
    columns = [
        col_ano.label("ano"),
        faixa_etaria,
        *get_saldo_columns()
    ]

    group_by = [col_ano, faixa_etaria]

    if agregacao == "mensal":
        columns.insert(1, col_mes.label("mes"))
        group_by.insert(1, col_mes)

    # 4. Query Principal com Agrupamento
    query = db.query(*columns).filter(Movimentacoes.idade.isnot(None))

    # 5. Filtros
    if ano:
        query = query.filter(col_ano == ano)
    if mes:
        query = query.filter(col_mes == mes)
    
    all_db_results = query.group_by(*group_by).order_by(col_ano.desc()).all()
    
    processed_results = []
    for item in all_db_results:
        # Soma do grupo para o percentual (Total de movimentações no ano ou ano/mês específico)
        soma_grupo = sum(
            r.total_movimentacoes for r in all_db_results
            if r.ano == item.ano and (agregacao == "anual" or r.mes == item.mes)
        )
        
        perc = (item.total_movimentacoes / soma_grupo * 100) if soma_grupo > 0 else 0
        
        res = {
            "ano": item.ano,
            "faixa_etaria": item.faixa_etaria,
            "total_movimentacoes": int(item.total_movimentacoes or 0),
            "saldo_movimentacoes": int(item.saldo_movimentacoes or 0),
            "total_admissoes": int(item.total_admissoes or 0),
            "total_demissoes": int(item.total_demissoes or 0),
            "percentual": f"{perc:.2f}",
        }
        
        if hasattr(item, 'mes'):
            res["mes"] = item.mes
            
        processed_results.append(res)

    # --- LÓGICA DE RETORNO CONDICIONAL ---

    if not pagination:
        return processed_results

    # Paginação manual da lista processada
    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    paginated_results = processed_results[(page - 1) * page_size: page * page_size]
    next_url, prev_url = build_pagination_urls(request, page, total_pages, page_size, {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination})

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }
    
@router.get("/escolaridade", response_model=Union[PaginatedAnalise[AnaliseGrauInstrucaoResult], List[AnaliseGrauInstrucaoResult]])
def get_analise_escolaridade(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Extrair ano e mês da competência
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100

    # 2. Campos que vamos selecionar
    columns = [
        col_ano.label("ano"),
        cast(Movimentacoes.grau_instrucao_id, String).label("escolaridade"),
        GrauInstrucaoReferencia.descricao.label("escolaridade_descricao"),
        *get_saldo_columns()
    ]

    group_by = [col_ano, Movimentacoes.grau_instrucao_id, GrauInstrucaoReferencia.descricao]

    if agregacao == "mensal":
        columns.insert(1, col_mes.label("mes"))
        group_by.insert(1, col_mes)

    # 3. Query Principal com Agrupamento e Join
    query = db.query(*columns).join(
        GrauInstrucaoReferencia, 
        Movimentacoes.grau_instrucao_id == GrauInstrucaoReferencia.codigo
    )

    # 4. Filtros
    if ano:
        query = query.filter(col_ano == ano)
    if mes:
        query = query.filter(col_mes == mes)
    
    all_db_results = query.group_by(*group_by).order_by(col_ano.desc()).all()
    
    processed_results = []
    for item in all_db_results:
        # Soma do grupo (ano ou ano/mês) para o cálculo do percentual
        soma_grupo = sum(
            r.total_movimentacoes for r in all_db_results
            if r.ano == item.ano and (agregacao == "anual" or r.mes == item.mes)
        )
        
        perc = (item.total_movimentacoes / soma_grupo * 100) if soma_grupo > 0 else 0
        
        res = {
            "ano": item.ano,
            "escolaridade": item.escolaridade,
            "escolaridade_descricao": item.escolaridade_descricao,
            "total_movimentacoes": int(item.total_movimentacoes or 0),
            "saldo_movimentacoes": int(item.saldo_movimentacoes or 0),
            "total_admissoes": int(item.total_admissoes or 0),
            "total_demissoes": int(item.total_demissoes or 0),
            "percentual": f"{perc:.2f}",
        }
        
        if hasattr(item, 'mes'):
            res["mes"] = item.mes
            
        processed_results.append(res)

    # --- LÓGICA DE RETORNO CONDICIONAL ---

    if not pagination:
        return processed_results

    # Paginação manual da lista processada para a tabela
    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    
    inicio = (page - 1) * page_size
    fim = inicio + page_size
    paginated_results = processed_results[(page - 1) * page_size: page * page_size]
    next_url, prev_url = build_pagination_urls(request, page, total_pages, page_size, {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination})

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }
    

@router.get("/raca-cor", response_model=Union[PaginatedAnalise[AnaliseRacaCorResult], List[AnaliseRacaCorResult]])
def get_analise_raca_cor(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Extrair ano e mês da competência
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100

    # 2. Campos que vamos selecionar
    columns = [
        col_ano.label("ano"),
        cast(Movimentacoes.raca_cor_id, String).label("raca_cor"),
        RacaCorReferencia.descricao.label("raca_cor_descricao"),
        *get_saldo_columns()
    ]

    group_by = [col_ano, Movimentacoes.raca_cor_id, RacaCorReferencia.descricao]

    if agregacao == "mensal":
        columns.insert(1, col_mes.label("mes"))
        group_by.insert(1, col_mes)

    # 3. Query Principal com Agrupamento e Join
    query = db.query(*columns).join(
        RacaCorReferencia, 
        Movimentacoes.raca_cor_id == RacaCorReferencia.codigo
    )

    # 4. Filtros
    if ano:
        query = query.filter(col_ano == ano)
    if mes:
        query = query.filter(col_mes == mes)
    
    all_db_results = query.group_by(*group_by).order_by(col_ano.desc()).all()
    
    # 5. Processamento dos resultados
    processed_results = []
    for item in all_db_results:
        # Cálculo da soma do grupo para o percentual correto
        soma_grupo = sum(
            r.total_movimentacoes for r in all_db_results
            if r.ano == item.ano and (agregacao == "anual" or r.mes == item.mes)
        )
        
        perc = (item.total_movimentacoes / soma_grupo * 100) if soma_grupo > 0 else 0
        
        res = {
            "ano": item.ano,
            "raca_cor": item.raca_cor,
            "raca_cor_descricao": item.raca_cor_descricao or "Não informado",
            "total_movimentacoes": int(item.total_movimentacoes or 0),
            "saldo_movimentacoes": int(item.saldo_movimentacoes or 0),
            "total_admissoes": int(item.total_admissoes or 0),
            "total_demissoes": int(item.total_demissoes or 0),
            "percentual": f"{perc:.2f}",
        }
        
        if hasattr(item, 'mes'):
            res["mes"] = item.mes
            
        processed_results.append(res)

    # --- LÓGICA DE RETORNO CONDICIONAL ---

    if not pagination:
        return processed_results

    # Paginação manual da lista processada
    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    
    paginated_results = processed_results[(page - 1) * page_size: page * page_size]
    next_url, prev_url = build_pagination_urls(request, page, total_pages, page_size, {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination})

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }
    
@router.get("/pcd", response_model=Union[PaginatedAnalise[AnaliseTipoDeficienciaResult], List[AnaliseTipoDeficienciaResult]])
def get_analise_pcd(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Extrair ano e mês da competência
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100

    # 2. Campos que vamos selecionar
    columns = [
        col_ano.label("ano"),
        cast(Movimentacoes.tipo_deficiencia_id, String).label("tipo_deficiencia"),
        TipoDeficienciaReferencia.descricao.label("tipo_deficiencia_descricao"),
        *get_saldo_columns()
    ]

    group_by = [col_ano, Movimentacoes.tipo_deficiencia_id, TipoDeficienciaReferencia.descricao]

    if agregacao == "mensal":
        columns.insert(1, col_mes.label("mes"))
        group_by.insert(1, col_mes)

    # 3. Query Principal com Agrupamento e Join
    query = db.query(*columns).join(
        TipoDeficienciaReferencia, 
        Movimentacoes.tipo_deficiencia_id == TipoDeficienciaReferencia.codigo
    )

    # 4. Filtros
    if ano:
        query = query.filter(col_ano == ano)
    if mes:
        query = query.filter(col_mes == mes)
    
    all_db_results = query.group_by(*group_by).order_by(col_ano.desc()).all()
    
    # 5. Processamento dos resultados (Calculando percentuais sobre a base total)
    processed_results = []
    for item in all_db_results:
        # Soma do grupo (ano ou ano/mês) para o cálculo do percentual
        soma_grupo = sum(
            r.total_movimentacoes for r in all_db_results
            if r.ano == item.ano and (agregacao == "anual" or r.mes == item.mes)
        )
        
        perc = (item.total_movimentacoes / soma_grupo * 100) if soma_grupo > 0 else 0
        
        res = {
            "ano": item.ano,
            "tipo_deficiencia": item.tipo_deficiencia,
            "tipo_deficiencia_descricao": item.tipo_deficiencia_descricao or "Não informado",
            "total_movimentacoes": int(item.total_movimentacoes or 0),
            "saldo_movimentacoes": int(item.saldo_movimentacoes or 0),
            "total_admissoes": int(item.total_admissoes or 0),
            "total_demissoes": int(item.total_demissoes or 0),
            "percentual": f"{perc:.2f}",
        }
        
        if hasattr(item, 'mes'):
            res["mes"] = item.mes
            
        processed_results.append(res)

    # --- LÓGICA DE RETORNO CONDICIONAL ---

    if not pagination:
        return processed_results

    # Paginação manual para uso em tabelas
    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    
    paginated_results = processed_results[(page - 1) * page_size: page * page_size]
    next_url, prev_url = build_pagination_urls(request, page, total_pages, page_size, {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination})

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }
    
@router.get("/salario-ocupacao", response_model=Union[PaginatedAnalise[AnaliseSalarioOcupacaoResult], List[AnaliseSalarioOcupacaoResult]])
def get_analise_salario_ocupacao(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    
    # 1. Extrair ano e mês da competência
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = func.nullif(Movimentacoes.competencia_mov % 100, None)
    # 2. Campos que vamos selecionar
    columns = [
        col_ano.label("ano"),
        Movimentacoes.cbo2002_ocupacao_id.label("cbo_codigo"),
        Cbo2002OcupacaoReferencia.descricao.label("cbo_descricao"),
        func.avg(case((Movimentacoes.salario > 0, Movimentacoes.salario))).label("salario_medio"),
        func.coalesce(func.sum(case((Movimentacoes.salario == 0, 1), else_=0)), 0).label("mov_zero"),
        *get_saldo_columns()
        # col_mes.label("mes")
    ]

    referencias = db.query(SalarioBaseReferencia).order_by(SalarioBaseReferencia.desde.asc()).all()
    print(f"DEBUG: Encontradas {len(referencias)} referências de salário mínimo.")

# calculo da media

    whens = []
    for i in range(len(referencias)):
        inicio = int(referencias[i].desde)
        # Se for o último registro, o fim é um futuro distante
        fim = int(referencias[i+1].desde if i+1 < len(referencias) else 209999) 
        valor_minimo = float(referencias[i].valor)
        
        # A condição lógica: período correto E salário > 0 E salário < mínimo
        condicao = (
            (Movimentacoes.competencia_mov >= inicio) & 
            (Movimentacoes.competencia_mov < fim) & 
            (Movimentacoes.salario > 0) & 
            (Movimentacoes.salario < valor_minimo)
        )
        whens.append((condicao, 1))

    # 3. Adicionar à lista de colunas usando um único CASE
    if whens:
        # O *whens desempacota a lista de tuplas [(cond1, 1), (cond2, 1), ...]
        columns.append(
            func.coalesce(func.sum(case(*whens, else_=0)), 0).label("mov_low")
        )
    else:
        from sqlalchemy import literal
        columns.append(literal(0).label("mov_low"))


    group_by = [col_ano, Movimentacoes.cbo2002_ocupacao_id, Cbo2002OcupacaoReferencia.descricao]

    if agregacao == "mensal":
        columns.append(col_mes.label("mes"))
        group_by.append(col_mes)

    # 3. Query Principal com Agrupamento e Join
    query = db.query(*columns).join(
        Cbo2002OcupacaoReferencia, 
        Movimentacoes.cbo2002_ocupacao_id == Cbo2002OcupacaoReferencia.codigo
    ).filter(
        Movimentacoes.cbo2002_ocupacao_id.isnot(None)
    )

    # 4. Filtros
    if ano:
        query = query.filter(col_ano == ano)
    if mes:
        query = query.filter(col_mes == mes)
    
    # query = query.filter(Movimentacoes.salario > 0)
    
    all_results = query.group_by(*group_by).order_by(
        col_ano.desc(),
        func.avg(Movimentacoes.salario).desc()
    ).all()
    
    processed_list = []
    for item in all_results:
        res = {
            "ano": int(item.ano),
            "cbo_codigo": int(item.cbo_codigo),
            "cbo_descricao": item.cbo_descricao or "Não informado",
            "salario_medio": round(float(item.salario_medio or 0), 2),
            "total_movimentacoes": int(item.total_movimentacoes),
            "saldo_movimentacoes": int(item.saldo_movimentacoes or 0),
            "total_admissoes": int(item.total_admissoes or 0),
            "total_demissoes": int(item.total_demissoes or 0),
            "mov_low": int(item.mov_low or 0),
            "mov_zero": int(item.mov_zero or 0),
        }
        if hasattr(item, 'mes') and item.mes is not None:
            res["mes"] = int(item.mes)
        processed_list.append(res)

    # --- LÓGICA DE RETORNO CONDICIONAL ---

    if not pagination:
        return processed_list

    # Paginação manual da lista processada
    total_registros = len(processed_list)
    total_pages = math.ceil(total_registros / page_size)
    
    inicio = (page - 1) * page_size
    fim = inicio + page_size
    paginated_results = processed_list[inicio:fim]

    next_url, prev_url = build_pagination_urls(
        request, page, total_pages, page_size,
        {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination},
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
    
@router.get("/ocupacao", response_model=Union[PaginatedAnalise[AnaliseOcupacaoResult], List[AnaliseOcupacaoResult]])
def get_analise_ocupacao(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Extrair ano e mês da competência
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100

    # 2. Campos que vamos selecionar
    columns = [
        col_ano.label("ano"),
        cast(Movimentacoes.cbo2002_ocupacao_id, String).label("cbo_codigo"),
        Cbo2002OcupacaoReferencia.descricao.label("cbo_descricao"),
        *get_saldo_columns()
    ]

    group_by = [col_ano, Movimentacoes.cbo2002_ocupacao_id, Cbo2002OcupacaoReferencia.descricao]

    if agregacao == "mensal":
        columns.insert(1, col_mes.label("mes"))
        group_by.insert(1, col_mes)

    # 3. Query Principal com Agrupamento e Join
    query = db.query(*columns).join(
        Cbo2002OcupacaoReferencia, 
        Movimentacoes.cbo2002_ocupacao_id == Cbo2002OcupacaoReferencia.codigo
    )

    # 4. Filtros
    if ano:
        query = query.filter(col_ano == ano)
    if mes:
        query = query.filter(col_mes == mes)
    
    all_db_results = query.group_by(*group_by).order_by(col_ano.desc(), func.count(Movimentacoes.id).desc()).all()
    
    # 5. Processamento da lista completa
    processed_results = []
    for item in all_db_results:
        # Soma do grupo para cálculo do percentual (total do ano ou total do mês/ano)
        soma_grupo = sum(
            r.total_movimentacoes for r in all_db_results
            if r.ano == item.ano and (agregacao == "anual" or r.mes == item.mes)
        )
        
        perc = (item.total_movimentacoes / soma_grupo * 100) if soma_grupo > 0 else 0
        
        res = {
            "ano": item.ano,
            "cbo_codigo": item.cbo_codigo,
            "cbo_descricao": item.cbo_descricao or "CBO não identificado",
            "total_movimentacoes": int(item.total_movimentacoes or 0),
            "saldo_movimentacoes": int(item.saldo_movimentacoes or 0),
            "total_admissoes": int(item.total_admissoes or 0),
            "total_demissoes": int(item.total_demissoes or 0),
            "percentual": f"{perc:.2f}",
        }
        
        if hasattr(item, 'mes'):
            res["mes"] = item.mes
            
        processed_results.append(res)

    # --- LÓGICA DE RETORNO CONDICIONAL ---

    if not pagination:
        return processed_results

    # Paginação manual da lista formatada
    total_registros = len(processed_results)
    total_pages = math.ceil(total_registros / page_size)
    
    paginated_results = processed_results[(page - 1) * page_size: page * page_size]
    next_url, prev_url = build_pagination_urls(request, page, total_pages, page_size, {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination})

    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results,
    }
    
@router.get("/saldo-ocupacao", response_model=Union[PaginatedAnalise[AnaliseSaldoOcupacaoResult], List[AnaliseSaldoOcupacaoResult]])
def get_analise_saldo_ocupacao(
    request: Request,
    db: Session = Depends(get_db),
    ano: Optional[int] = Query(None, description="Ano para filtro"),
    mes: Optional[int] = Query(None, description="Mês para filtro (1-12)"),
    agregacao: str = Query("anual", description="Tipo de agregação: anual ou mensal"),
    top: Optional[int] = Query(None, description="Número de ocupações com maior saldo (ex: 5, 10)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    pagination: bool = Query(True, description="Se falso, retorna todos os dados sem paginação")
):
    """
    Retorna análise de saldo de movimentações por ocupação (CBO).
    Calcula saldo médio, total de admissões, demissões e percentuais.
    """
    
    # Validação de agregação
    if agregacao not in ["anual", "mensal"]:
        raise HTTPException(status_code=400, detail="Agregação deve ser 'anual' ou 'mensal'")
    
    # # Se agregação for mensal, mês é obrigatório
    # if agregacao == "mensal" and mes is None:
    #     raise HTTPException(status_code=400, detail="Para agregação mensal, o parâmetro 'mes' é obrigatório")
    
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100
    
    columns = [
        col_ano.label('ano'),
        Movimentacoes.cbo2002_ocupacao_id.label('cbo_codigo'),
        Cbo2002OcupacaoReferencia.descricao.label('cbo_descricao'),
        *get_saldo_columns()
    ]
    
    group_by = [col_ano, Movimentacoes.cbo2002_ocupacao_id, Cbo2002OcupacaoReferencia.descricao]

    # 2. Adicionar mês se a agregação for mensal ou se o filtro de mês existir
    if agregacao == "mensal" or mes is not None:
        columns.insert(1, col_mes.label("mes"))
        group_by.insert(1, col_mes)

    query = db.query(*columns).join(
        Cbo2002OcupacaoReferencia,
        Movimentacoes.cbo2002_ocupacao_id == Cbo2002OcupacaoReferencia.codigo
    )
    
    if ano:
        query = query.filter(col_ano == ano)
    if mes:
        query = query.filter(col_mes == mes)
    
    query = query.group_by(*group_by).order_by(desc('saldo_movimentacoes'))
    
    # Executar query
    all_results = query.all()
    total_geral = sum(abs(r.saldo_movimentacoes) for r in all_results if r.saldo_movimentacoes)
    
    
    results_list = []
    for row in all_results:
        percentual = (abs(row.saldo_movimentacoes) / total_geral * 100) if total_geral > 0 else 0
        item = {
            "cbo_codigo": row.cbo_codigo,
            "cbo_descricao": row.cbo_descricao or "Não informado",
            "ano": row.ano,
            "saldo_movimentacoes": int(row.saldo_movimentacoes or 0),
            "total_movimentacoes": int(row.total_movimentacoes),
            "total_admissoes": int(row.total_admissoes or 0),
            "total_demissoes": int(row.total_demissoes or 0),
            "percentual": round(percentual, 2)
        }
        if hasattr(row, 'mes'):
            item["mes"] = row.mes
        results_list.append(item)

    # --- LÓGICA DE PAGINAÇÃO CONDICIONAL ---
    if not pagination:
        # Se for para gráfico, retorna a lista bruta (respeitando o 'top' se existir)
        return results_list
    # Lógica para TOP ou Paginação
   

    # Retorno paginado
    # Se for para tabela (padrão), aplica a paginação normal
    total_registros = len(results_list)
    total_pages = math.ceil(total_registros / page_size)
    
    # Fatiamos a lista processada
    paginated_results = results_list[(page - 1) * page_size: page * page_size]
    next_url, prev_url = build_pagination_urls(request, page, total_pages, page_size, {"agregacao": agregacao, "ano": ano, "mes": mes, "pagination": pagination})
    return {
        "count": total_registros,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "next": next_url,
        "previous": prev_url,
        "results": paginated_results
    }
    
@router.get("/movimentacoes", response_model=MovimentacoesResponse)
def get_movimentacoes_detalhadas(
    request: Request,
    db: Session = Depends(get_db),
    detalhes: bool = Query(True, description="Retornar detalhes das movimentações"),
    ano: Optional[int] = Query(None, description="Filtrar por ano"),
    mes: Optional[int] = Query(None, ge=1, le=12, description="Filtrar por mês"),
    agregacao: str = Query("mensal", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Tamanho da página")
):
    """
    Retorna as movimentações com todos os detalhes ou apenas o total
    """
    # Extrair ano e mês da competência
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100
    
    # Query base
    query = db.query(Movimentacoes)
    
    # Aplicar filtros
    if ano:
        query = query.filter(col_ano == ano)
    if mes and agregacao == "mensal":
        query = query.filter(col_mes == mes)
    
    # Contar total de movimentações
    total_movimentacoes = query.count()
    
    # Preparar resposta básica
    response = {
        "total_movimentacoes": total_movimentacoes,
        "filtros_aplicados": {
            "agregacao": agregacao,
            "ano": ano,
            "mes": mes if agregacao == "mensal" else None
        }
    }
    
    # Se detalhes=false, retornar apenas o total
    if not detalhes:
        return response
    
    # Se detalhes=true, buscar todos os dados com joins
    from ..models import (
       MunicipioReferencia,
      
    )
    
    query_detalhada = query.join(
        MunicipioReferencia, Movimentacoes.municipio_id == MunicipioReferencia.codigo 
    ).join(
        Cbo2002OcupacaoReferencia, Movimentacoes.cbo2002_ocupacao_id == Cbo2002OcupacaoReferencia.codigo 
    ).join(
        GrauInstrucaoReferencia, Movimentacoes.grau_instrucao_id == GrauInstrucaoReferencia.codigo
    ).join(
        RacaCorReferencia, Movimentacoes.raca_cor_id == RacaCorReferencia.codigo
    ).join(
        SexoReferencia, Movimentacoes.sexo_id == SexoReferencia.codigo 
    ).join(
        TipoDeficienciaReferencia, Movimentacoes.tipo_deficiencia_id == TipoDeficienciaReferencia.codigo
    )
    
    # Aplicar paginação
    total_pages = math.ceil(total_movimentacoes / page_size)
    offset = (page - 1) * page_size
    movimentacoes = query_detalhada.offset(offset).limit(page_size).all()
    
    # Formatar resultados
    resultados = []
    for mov in movimentacoes:
        resultados.append({
            "id": mov.id,
            "competencia_mov": mov.competencia_mov,
            "municipio_codigo": mov.municipio_id,
            "municipio_descricao": mov.municipio_rel.descricao,
            
            "cbo2002_ocupacao_codigo": mov.cbo2002_ocupacao_id,
            "cbo2002_ocupacao_descricao": mov.cbo2002_ocupacao_rel.descricao, 
            "grau_instrucao_codigo": mov.grau_instrucao_id,
            "grau_instrucao_descricao": mov.grau_instrucao_rel.descricao,
            "raca_cor_codigo": mov.raca_cor_id,
            "raca_cor_descricao": mov.raca_cor_rel.descricao,
            "sexo_codigo": mov.sexo_id,
            "sexo_descricao": mov.sexo_rel.descricao,
            
            "tipo_deficiencia_codigo": mov.tipo_deficiencia_id,
            "tipo_deficiencia_descricao": mov.tipo_deficiencia_rel.descricao,
            "saldo_movimentacao": mov.saldo_movimentacao,
            "idade": mov.idade,
            
            "salario": str(mov.salario) if mov.salario else None,
         
            "criado_em": mov.criado_em,
            "atualizado_em": mov.atualizado_em
        })
    
    # Gerar URLs de paginação
    next_url, prev_url = build_pagination_urls(
        request, page, total_pages, page_size,
        {"detalhes": detalhes, "agregacao": agregacao, "ano": ano, "mes": mes}
    )
    
    response["paginacao"] = {
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "links": {
            "next": next_url,
            "previous": prev_url
        }
    }
    response["resultados"] = resultados
    
    return response

def obter_nome_setor(secao_alvo: str, referencas: list) -> str:
    secao_alvo = secao_alvo.upper()
    for ref in referencas:
        # Se for um intervalo (Ex: A até C)
        if ref.secao_inicio and ref.secao_fim:
            if ref.secao_inicio <= secao_alvo <= ref.secao_fim:
                return ref.denominacao
        # Se for seção única
        elif ref.secao_inicio == secao_alvo:
            return ref.denominacao
    return "Outros / Não Identificado"

@router.get("/setor-caged", response_model=Union[PaginatedAnalise[AnaliseSetorResult], List[AnaliseSetorResult]])
def get_analise_setor_caged(
    request: Request,
    ano: Optional[int] = None,
    mes: Optional[int] = None,
    agregacao: str = Query("anual", enum=["anual", "mensal"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    pagination: bool = Query(True, description="Se falso, retorna a lista completa sem paginação"),
    db: Session = Depends(get_db)
):
    # 1. Busca referências de setores
    referencias = db.query(SetorAgregado).all()

    # 2. Query SEM PAGINAÇÃO no banco (Precisamos de TUDO para somar os setores)
    col_ano = func.floor(Movimentacoes.competencia_mov / 100)
    col_mes = Movimentacoes.competencia_mov % 100
    
    columns = [
        col_ano.label("ano"),
        Movimentacoes.secao_id.label("secao"),
        func.count(Movimentacoes.id).label("total"),
        *get_saldo_columns()
        
    ]
    group_by = [col_ano, Movimentacoes.secao_id]
    
    if agregacao == "mensal":
        columns.insert(1, col_mes.label("mes"))
        group_by.insert(1, col_mes)

    query = db.query(*columns)
    if ano: query = query.filter(col_ano == ano)
    if mes: query = query.filter(col_mes == mes)
    
    # Executa a query completa
    dados_brutos = query.group_by(*group_by).all()

    print("--- DEBUG DADOS BRUTOS DO BANCO ---")
    for r in dados_brutos[:5]: # Mostra apenas os 5 primeiros
        print(f"Ano: {r.ano}, Seção original: {r.secao}, Total Mov: {r.total_movimentacoes}, Adm: {r.total_admissoes}, Dem: {r.total_demissoes}")
    print("-----------------------------------")
    # 3. AGRUPAMENTO REAL EM MEMÓRIA
    # Chave: (ano, mes, nome_setor)
    consolidado = {}

    for row in dados_brutos:
        nome_setor = obter_nome_setor(row.secao, referencias) or "Outros/Não Informado"
        mes_val = row.mes if agregacao == "mensal" else None
        
        chave = (row.ano, mes_val, nome_setor)
        
        if chave not in consolidado:
            consolidado[chave] = {
                "total_movimentacoes": 0,
                "total_admissoes": 0,
                "total_demissoes": 0,
                "saldo_movimentacoes": 0
            }
        
        # Acumula os valores de saldo trazidos pelo get_saldo_columns()
        consolidado[chave]["total_movimentacoes"] += int(row.total_movimentacoes or 0)
        consolidado[chave]["total_admissoes"] += int(row.total_admissoes or 0)
        consolidado[chave]["total_demissoes"] += int(row.total_demissoes or 0)
        consolidado[chave]["saldo_movimentacoes"] += int(row.saldo_movimentacoes or 0)

    # 4. Cálculo de percentuais e montagem da lista final
    lista_processada = []
    
    # Calculamos os totais por período para o percentual
    totais_por_periodo = {}
    for (a, m, s), valores in consolidado.items():
        periodo = (a, m)
        totais_por_periodo[periodo] = totais_por_periodo.get(periodo, 0) + valores["total_movimentacoes"]

    for (a, m, s), valores in consolidado.items():
        total_geral = totais_por_periodo[(a, m)]
        total_mov = valores["total_movimentacoes"]
        perc = (total_mov / total_geral * 100) if total_geral > 0 else 0
        
        item = {
            "ano": int(a),
            "setor_denominacao": s,
            "total_movimentacoes": int(total_mov),
            "total_admissoes": int(valores["total_admissoes"]),
            "total_demissoes": int(valores["total_demissoes"]),
            "saldo_movimentacoes": int(valores["saldo_movimentacoes"]),
            "percentual": f"{perc:.2f}",
            "secao": "Consolidado"
        }
        if agregacao == "mensal":
            item["mes"] = m
        lista_processada.append(item)

    # 5. Ordenação (Ano desc, Mês desc, Total desc)
    lista_processada.sort(key=lambda x: (x['ano'], x.get('mes', 0), x['total_movimentacoes']), reverse=True)

    if not pagination:
        return lista_processada
    # 6. PAGINAÇÃO MANUAL (O pulo do gato)
    total_registros = len(lista_processada)
    total_pages = math.ceil(total_registros / page_size)
    
    # Fatia a lista conforme a página pedida
    inicio = (page - 1) * page_size
    fim = inicio + page_size
    dados_paginados = lista_processada[inicio:fim]

    # 7. Links de paginação
    extra_params = {"agregacao": agregacao, "ano": ano, "mes": mes}
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

@router.get("/setor-rais", response_model=Union[PaginatedAnalise[AnaliseSetorResult], List[AnaliseSetorResult]])
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