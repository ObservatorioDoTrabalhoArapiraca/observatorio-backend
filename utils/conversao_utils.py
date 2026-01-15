import pandas as pd
from pathlib import Path

def txt_para_parquet(arquivo_txt, arquivo_parquet=None, sep=None, encoding='utf-8'):
    """
    Converte um arquivo .txt (CSV ou TSV) para Parquet.
    :param arquivo_txt: Caminho do arquivo .txt de entrada.
    :param arquivo_parquet: Caminho do arquivo .parquet de saída (opcional).
    :param sep: Separador do arquivo (.csv=',' ou .tsv='\t'). Se None, tenta detectar.
    :param encoding: Encoding do arquivo de texto.
    :return: Caminho do arquivo Parquet gerado.
    """
    if sep is None:
        # Tenta detectar separador automaticamente
        with open(arquivo_txt, encoding=encoding) as f:
            primeira_linha = f.readline()
            if ';' in primeira_linha:
                sep = ';'
            elif '\t' in primeira_linha:
                sep = '\t'
            else:
                sep = ','

    df = pd.read_csv(arquivo_txt, sep=sep, encoding=encoding)
    if not arquivo_parquet:
        arquivo_parquet = str(Path(arquivo_txt).with_suffix('.parquet'))
    df.to_parquet(arquivo_parquet, index=False)
    return arquivo_parquet