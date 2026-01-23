import logging

logger = logging.getLogger(__name__)


def carregar_mapeamento_referencia(model_class, campo_codigo='codigo', campo_descricao='descricao'):
    """
    Carrega mapeamento de códigos de uma tabela de referência.
    
    Args:
        model_class: Classe do modelo Django (ex: RacaCorReferencia)
        campo_codigo: Nome do campo que contém o código (padrão: 'codigo')
        campo_descricao: Nome do campo que contém a descrição (padrão: 'descricao')
    
    Returns:
        dict: Dicionário {codigo: descricao}
    
    Exemplo:
        >>> from apps.referenciais.models import RacaCorReferencia
        >>> mapa = carregar_mapeamento_referencia(RacaCorReferencia)
        >>> print(mapa)
        {1: 'Branca', 2: 'Preta', 3: 'Parda', ...}
    """
    mapeamento = {}
    
    try:
        # Busca todos os registros da tabela
        registros = model_class.objects.values(campo_codigo, campo_descricao)
        
        # Cria o dicionário
        for registro in registros:
            codigo = registro[campo_codigo]
            descricao = registro[campo_descricao]
            mapeamento[codigo] = descricao
        
        logger.info(f"✅ Carregado mapeamento de {model_class.__name__}: {len(mapeamento)} registros")
        logger.debug(f"   Mapeamento: {mapeamento}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar mapeamento de {model_class.__name__}: {e}")
        raise
    
    return mapeamento