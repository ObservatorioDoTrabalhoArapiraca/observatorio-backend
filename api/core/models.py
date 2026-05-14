from typing import Optional

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Numeric
from .database import Base
from sqlalchemy.orm import  relationship

from sqlalchemy import Date

class ReferenciaMixin:
    codigo = Column(Integer, primary_key=True)
    descricao = Column(String(255))
    
class GrauDeInstrucaoRaisReferencia(Base):
    __tablename__ = "referenciais_graudeinstrucaoraisreferencia"
    codigo = Column(String(20), primary_key=True)
    descricao = Column(String(100))
class FaixaHorasContratualRaisReferencia(Base):
    __tablename__ = "referenciais_faixahorascontratualraisreferencia"
    codigo = Column(String(20), primary_key=True)
    descricao = Column(String(100))
    

class SalarioBaseReferencia(Base):
    __tablename__ = "referenciais_salariobasereferencia"
    desde = Column(Integer, primary_key=True)
    valor = Column(Float)
    legislacao = Column(String(255))
    reajuste = Column(Float)
    
class SetorAgregado(Base):
    __tablename__ = "ref_setores_agregados"

    id = Column(Integer, primary_key=True, index=True)
    denominacao = Column(String, nullable=False)
    # Se na sua tabela a coluna que liga com Movimentacoes.secao_id 
    # se chamar 'secao_id', mantenha assim:
    secao_inicio = Column(String,  nullable=True)
    secao_fim = Column(String, nullable=True)
    divisao_inicio = Column(Integer, nullable=True)
    divisao_fim = Column(Integer, nullable=True)
    
class SexoReferencia(Base, ReferenciaMixin):
    __tablename__ = "referenciais_sexoreferencia"  
class RacaCorReferencia(Base, ReferenciaMixin):
    __tablename__ = "referenciais_racacorreferencia"  
class MunicipioReferencia(Base, ReferenciaMixin):
    __tablename__ = "referenciais_municipioreferencia"
    
class Cbo2002OcupacaoReferencia(Base, ReferenciaMixin):
    __tablename__ = "referenciais_cbo2002ocupacaoreferencia"
    
class GrauInstrucaoReferencia(Base, ReferenciaMixin):
    __tablename__ = "referenciais_graudeinstrucaoreferencia"
    
class TipoDeficienciaReferencia(Base, ReferenciaMixin):
    __tablename__ = "referenciais_tipodeficienciareferencia"

class Movimentacoes(Base):
    __tablename__ = "movimentacoes" # Nome da tabela que o Django criou
    id = Column(Integer, primary_key=True, index=True)
    competencia_mov = Column(Integer)
    saldo_movimentacao = Column(Integer)
    idade = Column(Integer) 
    salario = Column(Float)
    criado_em = Column(Date,  name="criado_em")
    atualizado_em = Column(Date, name="atualizado_em")
    secao_id = Column(String, name="secao_id")

    municipio_id = Column(Integer, ForeignKey("referenciais_municipioreferencia.codigo"))
    municipio_rel = relationship("MunicipioReferencia", foreign_keys=[municipio_id])

    cbo2002_ocupacao_id = Column(Integer, ForeignKey("referenciais_cbo2002ocupacaoreferencia.codigo"))
    cbo2002_ocupacao_rel = relationship("Cbo2002OcupacaoReferencia", foreign_keys=[cbo2002_ocupacao_id])

    grau_instrucao_id = Column(Integer, ForeignKey("referenciais_graudeinstrucaoreferencia.codigo"))
    grau_instrucao_rel = relationship("GrauInstrucaoReferencia", foreign_keys=[grau_instrucao_id])
    
    raca_cor_id = Column(Integer, ForeignKey("referenciais_racacorreferencia.codigo"))
    raca_cor_rel = relationship("RacaCorReferencia", foreign_keys=[raca_cor_id])
    
    sexo_id = Column(Integer, ForeignKey("referenciais_sexoreferencia.codigo"))
    sexo_rel = relationship("SexoReferencia", foreign_keys=[sexo_id])

    tipo_deficiencia_id = Column(Integer, ForeignKey("referenciais_tipodeficienciareferencia.codigo"))
    tipo_deficiencia_rel = relationship("TipoDeficienciaReferencia", foreign_keys=[tipo_deficiencia_id])
    

    class Config:
        from_attributes = True


class MovimentacoesRais(Base):
    __tablename__ = "movimentacoes_rais" # Nome da tabela que o Django criou
    id = Column(Integer, primary_key=True, index=True)
    # Localização e Bairros
    bairros_sp = Column(String(50))
    bairros_fortaleza = Column(String(50))
    bairros_rj = Column(String(50))
    distritos_sp = Column(String(50))
    regioes_adm_df = Column(Integer)
    mun_trab = Column(String(10), index=True)
    municipio = Column(String(10), index=True)

    # Identificadores e CNAE
    cbo_ocupacao_2002 = Column(String(15), index=True)
    cnae_2_0_classe = Column(String(15))
    cnae_95_classe = Column(String(15))
    cnae_2_0_subclasse = Column(String(15))
    ibge_subsetor = Column(Integer)
    natureza_juridica = Column(String(10))

    # Perfil do Trabalhador
    idade = Column(Integer)
    faixa_etaria = Column(Integer)
    sexo_trabalhador = Column(Integer)
    raca_cor = Column(Integer)
    escolaridade_apos_2005 = Column(Integer)
    nacionalidade = Column(Integer)
    ind_portador_defic = Column(Integer)
    tipo_defic = Column(Integer)
    ano_chegada_brasil = Column(Integer)

    # Vínculo e Contrato
    vinculo_ativo_31_12 = Column(Integer)
    faixa_hora_contrat = Column(Integer)
    qtd_hora_contr = Column(Integer)
    faixa_tempo_emprego = Column(Integer)
    tempo_emprego = Column(Numeric(10, 1))
    tipo_admissao = Column(Integer)
    tipo_estab = Column(Integer)
    tipo_estab_1 = Column(String(20))
    tipo_vinculo = Column(Integer)
    tamanho_estabelecimento = Column(Integer)
    ind_cei_vinculado = Column(Integer)
    ind_simples = Column(Integer)
    ind_trab_intermitente = Column(Integer)
    ind_trab_parcial = Column(Integer)

    # Afastamento e Desligamento
    causa_afastamento_1 = Column(Integer)
    causa_afastamento_2 = Column(Integer)
    causa_afastamento_3 = Column(Integer)
    motivo_desligamento = Column(Integer)
    mes_admissao = Column(Integer)
    mes_desligamento = Column(String(10))
    qtd_dias_afastamento = Column(Integer)

    # Remunerações (Numeric para precisão decimal)
    vl_remun_dezembro_nom = Column(Numeric(15, 2))
    vl_remun_dezembro_sm = Column(Numeric(15, 2))
    vl_remun_media_nom = Column(Numeric(15, 2))
    vl_remun_media_sm = Column(Numeric(15, 2))
    faixa_remun_dezem_sm = Column(Integer)
    faixa_remun_media_sm = Column(Integer)

    # Remunerações Mensais
    vl_rem_janeiro_sc = Column(Numeric(15, 2))
    vl_rem_fevereiro_sc = Column(Numeric(15, 2))
    vl_rem_marco_sc = Column(Numeric(15, 2))
    vl_rem_abril_sc = Column(Numeric(15, 2))
    vl_rem_maio_sc = Column(Numeric(15, 2))
    vl_rem_junho_sc = Column(Numeric(15, 2))
    vl_rem_julho_sc = Column(Numeric(15, 2))
    vl_rem_agosto_sc = Column(Numeric(15, 2))
    vl_rem_setembro_sc = Column(Numeric(15, 2))
    vl_rem_outubro_sc = Column(Numeric(15, 2))
    vl_rem_novembro_sc = Column(Numeric(15, 2))

    # Ano Base (Obrigatório)
    ano_base = Column(Integer, nullable=False, index=True)