from core.base import Metrica
from core.github_extractor import GitHubExtractor

_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    issues { totalCount }
  }
}
"""


class WorkflowEfficiency(Metrica):
    nombre = "Eficiencia de Flujo de Trabajo"
    descripcion = (
        "Porcentaje de issues con al menos un assignee explícito sobre el total de issues. "
        "Mide el uso de mecanismos formales de asignación de trabajo."
    )
    dimension = ["Proceso", "Persona"]
    interpretacion = (
        "0–10%: gestión informal o reactiva. "
        "11–40%: asignación parcial, no sistemática. "
        "41–70%: uso activo del workflow formal. "
        "> 70%: uso intensivo; correlaciona con mayor tasa de cierre de issues (Jarczyk et al., 2018)."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        data = self._extractor.graphql(_QUERY, {"owner": owner, "name": repo})
        total_issues = data["data"]["repository"]["issues"]["totalCount"]

        search_result = self._extractor.search_issues(f"repo:{owner}/{repo} is:issue is:assigned")
        assigned_issues = search_result.get("total_count", 0)

        efficiency = round(assigned_issues / total_issues * 100, 2) if total_issues else 0.0

        return {
            "total_issues": total_issues,
            "assigned_issues": assigned_issues,
            "workflow_efficiency": efficiency,
        }