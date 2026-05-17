from core.base import Metrica

_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    pullRequests(states: OPEN) { totalCount }
  }
}
"""


class OpenPullRequests(Metrica):
    nombre = "Pull Requests Abiertas"
    descripcion = (
        "Cuenta cuántas Pull Requests están actualmente abiertas "
        "(sin fusionar ni cerrar). Indica el trabajo pendiente de revisión."
    )
    dimension = "Proceso"
    interpretacion = (
        "Un número alto de PRs abiertas puede señalar cuellos de botella en la revisión "
        "o una alta velocidad de desarrollo. Conviene monitorear la tendencia en el tiempo."
    )

    def __init__(self, extractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        data = self._extractor.graphql(_QUERY, {"owner": owner, "name": repo})
        count = data["data"]["repository"]["pullRequests"]["totalCount"]
        return {"open_pull_requests": count}