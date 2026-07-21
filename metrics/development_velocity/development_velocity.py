"""
Métrica M33 - Development Velocity (Velocidad de Desarrollo)

Velocidad de avance del proceso de desarrollo: trabajo completado e integrado por
unidad de tiempo. Según la ficha (metrics/development_velocity):

  - Fórmula primaria (tldr-pages): PRs mergeados / tiempo. En tldr cada PR mergeado
    equivale a una "tarea completada" (todo cambio entra vía PR revisado y mergeado).
  - Fórmula secundaria: commits / tiempo (operacionalización de Jarczyk et al. 2018).
    El detalle por período ya vive en metrics/commit_frequency; acá solo se toma el
    total de commits del default branch para la cifra global.

Salida:
  repo_created_at, delta_t_days, merged_prs_total, velocity_prs_per_week,
  num_commits_total, velocity_commits_per_week, velocity_by_year.

Extracción:
  - Una query GraphQL para createdAt + pullRequests(states: MERGED).totalCount +
    history.totalCount del default branch (3 datos en un request).
  - Para el desglose anual, REST Search (extractor.search_issues) con
    `is:pr is:merged merged:AAAA-01-01..AAAA-12-31` -> total_count por año.

Sesgo conocido (ficha): Hacktoberfest (octubre) puede triplicar la velocidad
mensual; por eso se reporta el desglose anual junto al global. En tldr commits y
PRs mergeados casi coinciden por el uso de squash merge.

Referencia teórica: Jarczyk et al. (2018) - Development Process Performance.
"""

from datetime import date, datetime, timezone

from core.base import Metrica


_QUERY_TOTALS = """
query($owner: String!, $repo: String!) {
  repository(owner: $owner, name: $repo) {
    createdAt
    mergedPRs: pullRequests(states: MERGED) { totalCount }
    defaultBranchRef {
      target {
        ... on Commit {
          history { totalCount }
        }
      }
    }
  }
}
"""


class DevelopmentVelocity(Metrica):
    nombre = "Development Velocity"
    descripcion = (
        "Velocidad de desarrollo medida como PRs mergeados por unidad de tiempo "
        "(fórmula primaria) y commits por unidad de tiempo (secundaria). Incluye el "
        "desglose anual para visibilizar estacionalidad (p. ej. Hacktoberfest)."
    )
    dimension = ["Proceso", "Persona"]
    interpretacion = (
        "Más PRs mergeados por semana indica mayor ritmo de integración de trabajo "
        "completado. El valor mensual/anual puede inflarse en octubre por "
        "Hacktoberfest, por eso se reporta el desglose temporal junto al global."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        """
        Calcula la velocidad global (PRs y commits por semana) más el desglose por
        año calendario. `limite` no aplica (la métrica son conteos agregados, no
        paginación); se acepta por compatibilidad con la interfaz Metrica.
        """
        data = self._extractor.graphql(
            _QUERY_TOTALS, {"owner": owner, "repo": repo}
        )
        if "errors" in data:
            raise RuntimeError(f"GraphQL devolvió errores: {data['errors']}")

        repo_data = (data.get("data") or {}).get("repository")
        if repo_data is None:
            raise RuntimeError(
                f"No se encontró el repositorio {owner}/{repo} "
                "(¿nombre incorrecto o sin permisos?)."
            )

        created_at_str = repo_data["createdAt"]
        merged_prs_total = repo_data["mergedPRs"]["totalCount"]

        ref = repo_data.get("defaultBranchRef") or {}
        target = ref.get("target") or {}
        num_commits_total = (target.get("history") or {}).get("totalCount", 0)

        created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        ahora = datetime.now(timezone.utc)
        delta_t_days = (ahora - created_at).days

        return {
            "repo_created_at": created_at_str,
            "delta_t_days": delta_t_days,
            "merged_prs_total": merged_prs_total,
            "velocity_prs_per_week": self._por_semana(merged_prs_total, delta_t_days),
            "num_commits_total": num_commits_total,
            "velocity_commits_per_week": self._por_semana(num_commits_total, delta_t_days),
            "velocity_by_year": self._por_anio(owner, repo, created_at, ahora),
        }

    def _por_anio(self, owner: str, repo: str,
                  created_at: datetime, ahora: datetime) -> dict:
        """PRs mergeados por año calendario (vía Search API), recortando los años
        parciales (el de creación y el actual) a su ventana real."""
        resultado = {}
        for anio in range(created_at.year, ahora.year + 1):
            inicio = max(date(anio, 1, 1), created_at.date())
            fin = min(date(anio, 12, 31), ahora.date())
            dias = (fin - inicio).days + 1
            if dias <= 0:
                continue
            query = (
                f"repo:{owner}/{repo} is:pr is:merged "
                f"merged:{inicio.isoformat()}..{fin.isoformat()}"
            )
            total = self._extractor.search_issues(query).get("total_count", 0)
            resultado[str(anio)] = {
                "merged_prs": total,
                "prs_per_week": self._por_semana(total, dias),
            }
        return resultado

    @staticmethod
    def _por_semana(cantidad: int, dias: int) -> float:
        """Convierte un conteo en una tasa semanal: cantidad / (dias / 7)."""
        if dias <= 0:
            return 0.0
        return round(cantidad / (dias / 7), 1)