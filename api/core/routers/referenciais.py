from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Cbo2002OcupacaoReferencia, GrauInstrucaoReferencia, Movimentacoes, SalarioBaseReferencia, SetorAgregado, SexoReferencia, RacaCorReferencia, TipoDeficienciaReferencia
from ..referenciaisSchemas import Cbo2002OcupacaoReferenciaSchema, GrauInstrucaoReferenciaSchema, MovimentacoesSchema, RacaCorReferenciaSchema, SalarioOcupacaoReferenciaSchema, SetorReferenciaSchema, SexoReferenciaSchema, TipoDeficienciaReferenciaSchema, SaldoOcupacaoReferenciaSchema

router = APIRouter()

@router.get("/versao-teste")
def teste_versao():
    return {"status": "codigo_novo_online_v2"}

@router.get("/sexo", response_model=list[SexoReferenciaSchema])
def get_sexos(db: Session = Depends(get_db)):
    return db.query(SexoReferencia).all()

@router.get("/escolaridade", response_model=list[GrauInstrucaoReferenciaSchema])
def get_escolaridades(db: Session = Depends(get_db)):
    return db.query(GrauInstrucaoReferencia).all()

@router.get("/raca_cor", response_model=list[RacaCorReferenciaSchema])
def get_racas(db: Session = Depends(get_db)):
    return db.query(RacaCorReferencia).all()

@router.get("/pcd", response_model=list[TipoDeficienciaReferenciaSchema])
def get_pcd(db: Session = Depends(get_db)):
    return db.query(TipoDeficienciaReferencia).all()

@router.get("/ocupacao", response_model=list[Cbo2002OcupacaoReferenciaSchema])
def get_ocupacao(db: Session = Depends(get_db)):
    return db.query(Cbo2002OcupacaoReferencia).all()

@router.get("/salario-ocupacao", response_model=list[SalarioOcupacaoReferenciaSchema])
def get_salario_ocupacao(db: Session = Depends(get_db)):
    return db.query(Cbo2002OcupacaoReferencia).all()

@router.get("/setor", response_model=list[SetorReferenciaSchema])
def get_setor(db: Session = Depends(get_db)):
    return db.query(SetorAgregado).all()

# @router.get("/saldo-ocupacao", response_model=list[SaldoOcupacaoReferenciaSchema])
# def get_saldo_ocupacao(db: Session = Depends(get_db)):
#     return db.query(SaldoOcupacaoReferencia).all()

@router.get("/salario-base", response_model=List[Any])
def get_referencias_salario_base(db: Session = Depends(get_db)):
    """
    Retorna a lista de salários mínimos de referência históricos.
    Tabela: referenciais_salariobasereferencia
    """
    try:
        results = db.query(SalarioBaseReferencia).order_by(SalarioBaseReferencia.desde.desc()).all()
        return [
            {
                "desde": r.desde,
                "valor": float(r.valor) if r.valor else 0.0,
                "legislacao": r.legislacao,
                "reajuste": float(r.reajuste) if r.reajuste else 0.0,
                # Adicione outros campos que existam na sua tabela aqui
            } 
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar referências de salário: {str(e)}")


@router.get("/setores-agregados", response_model=List[Any])
def get_referencias_setores_agregados(db: Session = Depends(get_db)):
    """
    Retorna a lista de setores agregados e suas divisões CNAE correspondentes.
    Tabela: ref_setores_agregados
    """
    try:
        # Ordena pela denominação do setor para facilitar a leitura na tabela
        results = db.query(SetorAgregado).order_by(SetorAgregado.denominacao.asc()).all()
        return [
          {
                "id": r.id,
                "denominacao": r.denominacao,
                "secao_inicio": r.secao_inicio,
                "secao_fim": r.secao_fim,
                "divisao_inicio": r.divisao_inicio,
                "divisao_fim": r.divisao_fim,
                # Adicione outros campos conforme sua tabela
            } 
            for r in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar referências de setores: {str(e)}")

@router.get("/movimentacoes", response_model=list[MovimentacoesSchema])
def get_movimentacoes(db: Session = Depends(get_db)):
    return db.query(Movimentacoes).all()

# @router.get("/totalmovimentacoes", response_model=list[TotalMovimentacoesSchema])
# def get_total_movimentacoes(db: Session = Depends(get_db)):
#     return db.query(TotalMovimentacoes).all()