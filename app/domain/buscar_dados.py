class BuscarDados:
    def __init__(self, repository):
        self.repository = repository

    def executar(self):
        return self.repository.buscar_dados()