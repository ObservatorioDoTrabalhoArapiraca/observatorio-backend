class BuscarDadosUseCase:
    def __init__(self, repo):
        self.repo = repo

    def execute(self, query):
        return self.repo.buscar_dados(query)