# Forks, Issues y Pull Requests

## Descripción

Obtiene métricas de actividad y comunidad del repositorio: cantidad de **forks**, **issues** y **pull requests** en sus distintos estados, usando una sola consulta **GraphQL**.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `forks` | Total de veces que el repositorio fue bifurcado |
| `issues_total` | Cantidad total de issues creados (abiertos + cerrados) |
| `issues_open` | Issues actualmente abiertos |
| `pull_requests_total` | Total de pull requests (todos los estados) |
| `pull_requests_merged` | Pull requests fusionados exitosamente |
| `pull_requests_closed` | Pull requests cerrados sin fusionar |

## Cómo se calcula

Se realiza una única consulta GraphQL a la API de GitHub que obtiene:
- `forks.totalCount`
- `issues.totalCount` y `issues(states: OPEN).totalCount`
- `pullRequests.totalCount`, `pullRequests(states: MERGED).totalCount` y `pullRequests(states: CLOSED).totalCount`

## Interpretación

| Métrica | Interpretación |
|---|---|
| `forks` alto | Alta popularidad o reutilización del código por la comunidad |
| `issues_open` alto | Carga de trabajo pendiente o proyecto muy activo |
| PRs fusionados / PRs totales | Tasa de éxito en la integración de código (idealmente cercana a 1) |
| PRs cerradas sin fusionar | Contribuciones descartadas — pueden indicar problemas de calidad o coordinación |

## Dimensión

**Proceso**

## Implementación

```python
from github_extractor import GitHubExtractor
from base import Metrica

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

    def __init__(self, extractor: GitHubExtractor):
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
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from forks_issues_prs import ForksIssuesPRs

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
forks = ForksIssuesPRs(extractor)
print(forks.calcular(GITHUB_ORG, REPO_NAME))
```

## Última salida

```json
{
  "forks": 5221,
  "issues_total": 1742,
  "issues_open": 229,
  "pull_requests_total": 20651,
  "pull_requests_merged": 18725,
  "pull_requests_closed": 1872
}
```