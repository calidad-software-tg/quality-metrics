from abc import ABC, abstractmethod
from .github_extractor import GitHubExtractor

class Metrica(ABC):
    nombre: str
    descripcion: str
    dimension: str
    interpretacion: str
    extractor: GitHubExtractor

    @abstractmethod
    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        ...