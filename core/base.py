from abc import ABC, abstractmethod


class Metrica(ABC):
    nombre: str
    descripcion: str
    dimension: list[str]
    interpretacion: str

    @abstractmethod
    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        ...