from core.base import Metrica


class CoreDevsRejectedPRs(Metrica):
    nombre = "Pull Requests Rechazadas de Desarrolladores Principales"
    descripcion = (
        "Cuenta las Pull Requests cerradas sin fusionar por cada desarrollador principal. "
        "Identifica contribuciones que no fueron integradas al código base."
    )
    dimension = "Persona"
    interpretacion = (
        "Muchas PRs rechazadas pueden indicar falta de alineación con los estándares del proyecto, "
        "problemas de calidad de código o dificultades en el proceso de revisión."
    )

    def __init__(self, extractor, core_developers: list[str]):
        self._extractor = extractor
        self._core_developers = core_developers

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        prs_cerradas = self._extractor.get_pull_requests(owner, repo, state="closed")
        resultado: dict[str, int] = {dev: 0 for dev in self._core_developers}

        for pr in prs_cerradas:
            autor = pr["user"]["login"]
            if autor in resultado and not pr.get("merged_at"):
                resultado[autor] += 1

        resultado["total"] = sum(v for k, v in resultado.items() if k != "total")
        return resultado