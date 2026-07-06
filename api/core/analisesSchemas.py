from pydantic import BaseModel
from typing import List, Optional, TypeVar, Generic
from datetime import datetime
from decimal import Decimal

T = TypeVar("T")

class MovimentacaoDetalhadaResult(BaseModel):
    id: int
    competencia_movimentacao: int
    
    municipio_codigo: int
    municipio_descricao: str
    secao_id: str
    
    cbo2002_ocupacao_codigo: int
    cbo2002_ocupacao_descricao: str
    
    grau_instrucao_codigo: int
    grau_instrucao_descricao: str
    raca_cor_codigo: int
    raca_cor_descricao: str
    sexo_codigo: int
    sexo_descricao: str
    
    tipo_deficiencia_codigo: int
    tipo_deficiencia_descricao: str
    saldo_movimentacao: int
    idade: Optional[int]
   
    salario: Optional[str]
    
    criado_em: datetime
    atualizado_em: datetime
    
    class Config:
        from_attributes = True

class FiltrosAplicados(BaseModel):
    agregacao: str
    ano: Optional[int] = None
    mes: Optional[int] = None


class PaginacaoLinks(BaseModel):
    next: Optional[str] = None
    previous: Optional[str] = None


class PaginacaoInfo(BaseModel):
    page: int
    page_size: int
    total_pages: int
    links: PaginacaoLinks


class MovimentacoesResponse(BaseModel):
    total_movimentacoes: int
    filtros_aplicados: FiltrosAplicados
    paginacao: Optional[PaginacaoInfo] = None
    resultados: Optional[List[MovimentacaoDetalhadaResult]] = None


class AnaliseBaseResult(BaseModel):
    ano: int
    mes: Optional[int] = None
    saldo_movimentacoes: int
    total_movimentacoes: int
    total_admissoes: int
    total_demissoes: int
    percentual: str
    
    class Config:
      from_attributes = True
      
class AnaliseSexoResult(AnaliseBaseResult):
    sexo: int
    sexo_descricao: str
class AnaliseMunicipioResult(AnaliseBaseResult):
    municipio: int
    municipio_descricao: str
class AnaliseIdadeResult(AnaliseBaseResult):
    faixa_etaria: str
class AnaliseRacaCorResult(AnaliseBaseResult):
    raca_cor: int
    raca_cor_descricao: str
class AnaliseSalarioOcupacaoResult(BaseModel):
    cbo_codigo: int
    cbo_descricao: str
    salario_medio: float
    ano: int
    mes: Optional[int] = None
    total_movimentacoes: int
    saldo_movimentacoes: int
    total_admissoes: int
    total_demissoes: int
    mov_low: int
    mov_zero: int
    
class AnaliseSaldoOcupacaoResult(BaseModel):
    ano: int
    mes: Optional[int] = None
    cbo_codigo: int
    cbo_descricao: str
    saldo_movimentacoes: int
    total_movimentacoes: int
    total_admissoes: int
    total_demissoes: int
    percentual: float
    pagination: Optional[bool] = None
    
class AnaliseSetorResult(AnaliseBaseResult):
    secao: str | None
    setor_denominacao: str | None
    
class AnaliseOcupacaoResult(AnaliseBaseResult):
   cbo_codigo: int
   cbo_descricao: str

class AnaliseGrauInstrucaoResult(AnaliseBaseResult):
    escolaridade: int
    escolaridade_descricao: str
class AnaliseGrauInstrucaoRaisResult(AnaliseBaseResult):
    grau_instrucao: int
    grau_instrucao_descricao: str
    
class AnaliseVinculoCBORaisResult(AnaliseBaseResult):
    cbo_codigo: str
    cbo_descricao: str
    qtd_hora_contr: Optional[int]
    faixa_hora_contrat: Optional[int]
    faixa_hora_contrat_descricao: str
    
class AnaliseSalarioOcupacaoRaisResult(BaseModel):
    ano: int
    mes: Optional[int] = None
    total_movimentacoes: int
    cbo_codigo: str
    cbo_descricao: str
    salario_medio: float
    total_admissoes: int
    total_demissoes: int
    mov_low: int
    mov_zero: int
    

class AnaliseTipoDeficienciaResult(AnaliseBaseResult):
    tipo_deficiencia: int
    tipo_deficiencia_descricao: str
    
class AnaliseTipoDeficienciaResult(AnaliseBaseResult):
    tipo_deficiencia: int
    tipo_deficiencia_descricao: str

class PaginatedAnalise(BaseModel, Generic[T]):
    count: int
    total_pages: int
    current_page: int
    page_size: int
    next: Optional[str]
    previous: Optional[str]
    results: List[T]