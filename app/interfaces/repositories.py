from abc import ABC, abstractmethod

class BigQueryRepository(ABC):
    @abstractmethod
    def buscar_dados(self, query: str) -> list[dict]:
        pass
