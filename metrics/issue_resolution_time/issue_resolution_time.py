import statistics
from datetime import datetime

from core.base import Metrica
from core.github_extractor import GitHubExtractor


class IssueResolutionTime(Metrica):
    nombre = "Tiempo Promedio de Resolución de Issues"
    descripcion = (
        "Tiempo promedio (y mediana) en días entre la apertura y el cierre de issues. "
        "Mide la eficiencia del equipo para responder y resolver tareas, bugs o solicitudes."
    )
    dimension = ["Proceso", "Persona"]
    interpretacion = (
        "Valores < 7 días indican alta eficiencia de respuesta. "
        "Valores > 90 días sugieren backlog acumulado o issues abandonados. "
        "La mediana es más representativa que la media cuando la distribución tiene colas pesadas."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._gh = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        url = f"{self._gh._api_base}/repos/{owner}/{repo}/issues"
        params = {"state": "closed", "per_page": 100}

        if limite:
            issues_raw = self._gh.get_paginated(owner, repo, "issues", params={"state": "closed"}, max_items=limite)
        else:
            issues_raw = self._gh._get_paginated(url, params)

        tiempos = []
        for issue in issues_raw:
            if issue.get("pull_request") is not None:
                continue
            t_open = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            t_close = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
            tiempos.append((t_close - t_open).total_seconds() / 86400)

        return {
            "n_issues_cerrados": len(tiempos),
            "issue_resolution_time_dias": round(statistics.mean(tiempos), 2) if tiempos else 0.0,
            "issue_resolution_time_mediana_dias": round(statistics.median(tiempos), 2) if tiempos else 0.0,
        }