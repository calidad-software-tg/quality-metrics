# Open Pull Requests — Pull Requests sin Fusionar

## Descripción

Cuenta cuántas **Pull Requests están actualmente abiertas** en el repositorio: aquellas que aún no fueron revisadas, cerradas ni fusionadas a la rama principal.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `open_pull_requests` | Cantidad de Pull Requests con estado `OPEN` al momento de la consulta |

## Cómo se calcula

Se realiza una consulta **GraphQL** a la API de GitHub que obtiene el `totalCount` de pull requests con estado `OPEN`.

## Para qué sirve

- Detectar **tareas pendientes de revisión**.
- Identificar posibles **cuellos de botella** en el flujo de trabajo de integración.
- Evaluar la **velocidad de integración** del equipo: cuánto tiempo permanecen abiertas las PRs.

## Interpretación

| Valor | Interpretación |
|---|---|
| 0 | El equipo integra código con mucha rapidez o hay poca actividad |
| Bajo (1–5) | Flujo de trabajo saludable y ágil |
| Alto (>10) | Posible cuello de botella en revisión de código o alta velocidad de desarrollo |

Conviene monitorear la tendencia en el tiempo, no sólo el valor instantáneo.

## Dimensión

**Proceso**

## Implementación

```python
from github_extractor import GitHubExtractor
from base import Metrica

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

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        data = self._extractor.graphql(_QUERY, {"owner": owner, "name": repo})
        count = data["data"]["repository"]["pullRequests"]["totalCount"]
        return {"open_pull_requests": count}
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from open_pull_requests import OpenPullRequests

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
open_prs = OpenPullRequests(extractor)
print(open_prs.calcular(GITHUB_ORG, REPO_NAME))
```

## Última salida

```json
{
  "open_pull_requests": 54
}
```