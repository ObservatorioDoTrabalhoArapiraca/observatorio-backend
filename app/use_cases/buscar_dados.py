from app.domain.buscar_dados import BuscarDados
from app.infra.bigquery_repo import BigQueryRepositorio

def buscar_dados():
    repositorio = BigQueryRepositorio()
    caso_de_uso = BuscarDados(repositorio)
    return caso_de_uso.executar()