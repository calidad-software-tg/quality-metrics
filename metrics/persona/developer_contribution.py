from collections import Counter

from core.base import Metrica


class DeveloperContribution(Metrica):
    nombre = "Contribución por Desarrollador"
    descripcion = (
        "Cuenta cuántos commits realizó cada autor en el repositorio. "
        "Permite analizar la distribución del trabajo entre colaboradores."
    )
    dimension = "Persona"
    interpretacion = (
        "Una distribución muy desigual puede indicar dependencia de pocos autores (bus factor alto). "
        "Una distribución uniforme refleja colaboración balanceada entre el equipo."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        commits = self._extractor.get_commits(owner, repo, limite=limite)
        autores = [c["commit"]["author"]["name"] for c in commits]
        return dict(Counter(autores))