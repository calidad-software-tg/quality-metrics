from core.base import Metrica


class CoreDevsPRs(Metrica):
    nombre = "Pull Requests de Desarrolladores Principales"
    descripcion = (
        "Cuenta cuántos Pull Requests creó cada uno de los desarrolladores principales "
        "definidos en la configuración, usando la API de búsqueda de GitHub."
    )
    dimension = "Persona"
    interpretacion = (
        "Permite evaluar el nivel de participación individual de los desarrolladores clave "
        "y detectar desigualdades en la distribución de tareas. "
        "Un número bajo conjunto puede reflejar un equipo pequeño o una fase temprana del proyecto."
    )

    def __init__(self, extractor, core_developers: list[str]):
        self._extractor = extractor
        self._core_developers = core_developers

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        resultado: dict[str, int] = {}
        for dev in self._core_developers:
            query = f"repo:{owner}/{repo}+type:pr+author:{dev}"
            data = self._extractor.search_issues(query)
            resultado[dev] = data.get("total_count", 0)
        resultado["total"] = sum(resultado.values())
        return resultado