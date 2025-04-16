from abc import ABC, abstractmethod

class BigQueryRepository(ABC):
    @abstractmethod
    def get_dados(self, query: str) -> list[dict]:
        pass
