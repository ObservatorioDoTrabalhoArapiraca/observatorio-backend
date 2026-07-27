import pandas as pd
from pathlib import Path

def filtrar_parquet_por_coluna(
    arquivo_entrada: str,
    coluna: str,
    valor,
    arquivo_saida: str = None
) -> str:
    """
    Filtra um arquivo Parquet por valor em uma coluna e salva o resultado em um novo arquivo Parquet.

    :param arquivo_entrada: Caminho do arquivo Parquet de entrada.
    :param coluna: Nome da coluna para aplicar o filtro.
    :param valor: Valor desejado na coluna.
    :param arquivo_saida: Caminho do arquivo Parquet de saída (opcional).
    :return: Caminho do arquivo Parquet filtrado.
    """
    
    df = pd.read_parquet(arquivo_entrada)
    df_filtrado = df[df[coluna] == valor]

    if not arquivo_saida:
        arquivo_saida = str(Path(arquivo_entrada).with_stem(f"{Path(arquivo_entrada).stem}_{valor}"))

    df_filtrado.to_parquet(arquivo_saida, index=False)
    return arquivo_saida