from core.base import Metrica

_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    forks { totalCount }
    issues { totalCount }
    issuesOpen: issues(states: OPEN) { totalCount }
    pullRequests { totalCount }
    pullRequestsMerged: pullRequests(states: MERGED) { totalCount }
    pullRequestsClosed: pullRequests(states: CLOSED) { totalCount }
  }
}
"""


class ForksIssuesPRs(Metrica):
    nombre = "Forks, Issues y Pull Requests"
    descripcion = (
        "Obtiene el total de forks, issues (totales y abiertos) y pull requests "
        "(totales, fusionados y cerrados sin fusionar) del repositorio via GraphQL."
    )
    dimension = "Proceso"
    interpretacion = (
        "Muchos forks indican popularidad o reutilización. Issues abiertos reflejan trabajo pendiente. "
        "La relación PRs fusionados / cerrados indica la eficiencia en la integración de código."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        data = self._extractor.graphql(_QUERY, {"owner": owner, "name": repo})
        r = data["data"]["repository"]
        return {
            "forks": r["forks"]["totalCount"],
            "issues_total": r["issues"]["totalCount"],
            "issues_open": r["issuesOpen"]["totalCount"],
            "pull_requests_total": r["pullRequests"]["totalCount"],
            "pull_requests_merged": r["pullRequestsMerged"]["totalCount"],
            "pull_requests_closed": r["pullRequestsClosed"]["totalCount"],
        }