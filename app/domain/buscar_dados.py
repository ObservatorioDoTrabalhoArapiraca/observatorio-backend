class BuscarDados:
    def __init__(self, repository):
        self.repository = repository

    def executar(self):
        # Chama o repositório para buscar os dados
        return self.repository.buscar_dados()