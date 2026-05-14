from pydantic import BaseModel
from datetime import date 

class BaseReferenciaSchema(BaseModel):
    codigo: int
    descricao: str

class SexoReferenciaSchema(BaseReferenciaSchema):
    pass
class SalarioOcupacaoReferenciaSchema(BaseReferenciaSchema):
    pass
class RacaCorReferenciaSchema(BaseReferenciaSchema):
    pass 
class MunicipioReferenciaSchema(BaseReferenciaSchema):
    pass

class Cbo2002OcupacaoReferenciaSchema(BaseReferenciaSchema):
    pass

class GrauInstrucaoReferenciaSchema(BaseReferenciaSchema):
    pass

    pass

class TipoDeficienciaReferenciaSchema(BaseReferenciaSchema):
    pass

class SaldoOcupacaoReferenciaSchema(BaseReferenciaSchema):
    cbo2002_ocupacao_id: int | None
    cbo2002_ocupacao_descricao: str | None
    saldo_movimentacoes: int | None
    total_movimentacoes: int | None
    total_admissoes: int | None
    total_demissoes: int | None
    
class SetorReferenciaSchema(BaseModel):
    secao_inicio: str | None
    secao_fim: str | None
    divisao_inicio: int | None
    divisao_fim: int | None
    denominacao: str | None


class MovimentacoesSchema(BaseModel):
    id: int
    competencia_mov: int | None 
    municipio_id: int | None
    municipio_descricao: str | None 
    saldo_movimentacao: int | None
    cbo2002_ocupacao_id: int | None
    cbo2002_ocupacao_descricao: str | None 
    grau_de_instrucao_id: int | None
    grau_de_instrucao_descricao: str | None
    idade: int | None 
    raca_cor_id: int | None
    raca_cor_descricao: str | None
    sexo_id: int | None
    sexo_descricao: str | None 
    tipo_deficiencia_id: int | None
    tipo_deficiencia_rel: str | None
    salario: float | None 
    criado_em: date
    atualizado_em: date | None
    
    regiao_id: int | None
    uf_id: int | None
    secao_id: str | None
    subclasse_id: int | None
    saldo_movimentacao: int | None
    categoria_id: int | None
    horas_contratuais: int | None
    tipo_empregador_id: int | None
    tipo_estabelecimento_id: int | None
    tipo_movimentacao_id: int | None
    ind_trab_intermitente_id: int | None
    ind_trab_parcial_id: int | None
    tam_estab_jan_id: int | None
    indicador_aprendiz_id: int | None
    origem_informacao_id: int | None
    competencia_dec: int | None
    competencia_exc: int | None
    indicador_exclusao_id: int | None
    indicador_fora_prazo_id: int | None
    unidade_salario_codigo_id: int | None
    valor_salario_fixo: float | None
    