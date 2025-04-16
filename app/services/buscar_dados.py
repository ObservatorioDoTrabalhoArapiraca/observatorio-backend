from app.domain.ports.count_by_year_repository import BigQueryRepository

class BuscarDados:
    def __init__(self, repositorio: BigQueryRepository):
        self.repositorio = repositorio

    def executar(self):
        return self.repositorio.get_dados()
