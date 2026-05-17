# Repo Stats — Número de Colaboradores, Líneas de Código y Branches

## Descripción

Calcula tres métricas estructurales del repositorio en una sola consulta **GraphQL**: la cantidad de ramas activas, el número de colaboradores con acceso directo y una estimación de las líneas de código en los archivos de la raíz.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `branches` | Cantidad total de ramas activas (`refs/heads/`) |
| `collaborators` | Cantidad de usuarios con acceso directo al repositorio |
| `estimated_lines_of_code` | Estimación del total de líneas de código en archivos de la raíz del repo |

## Cómo se calcula

1. **Ramas**: se consulta el campo `refs(refPrefix: "refs/heads/")` y su `totalCount`.
2. **Colaboradores**: se consulta el campo `collaborators` y su `totalCount`.
3. **Líneas de código**: se accede al árbol de archivos (`object(expression: "HEAD:")`) y se suman las líneas (conteo de `\n + 1`) de cada archivo de tipo `blob` en la raíz.

> **Nota**: la estimación de líneas sólo cubre archivos en la raíz del repositorio (no subdirectorios), por limitación de la consulta GraphQL usada.

## Interpretación

| Métrica | Interpretación |
|---|---|
| `branches` alto | Desarrollo paralelo activo con múltiples features en curso |
| `branches` bajo | Desarrollo más lineal o centralizado |
| `collaborators` | Refleja el tamaño del equipo con acceso directo |
| `estimated_lines_of_code` | Indicador de la magnitud del proyecto |

## Dimensión

**Producto**

## Implementación

```python
from github_extractor import GitHubExtractor
from base import Metrica

_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    refs(refPrefix: "refs/heads/") { totalCount }
    collaborators { totalCount }
    object(expression: "HEAD:") {
      ... on Tree {
        entries {
          type
          object {
            ... on Blob { text }
          }
        }
      }
    }
  }
}
"""


class RepoStats(Metrica):
    nombre = "Estadísticas del Repositorio"
    descripcion = (
        "Calcula el número de ramas activas, colaboradores con acceso "
        "y líneas de código estimadas en los archivos raíz del repositorio."
    )
    dimension = "Producto"
    interpretacion = (
        "Más ramas activas sugieren desarrollo paralelo intenso. "
        "El conteo de colaboradores refleja el tamaño del equipo. "
        "Las líneas de código estiman la magnitud del proyecto."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        data = self._extractor.graphql(_QUERY, {"owner": owner, "name": repo})
        r = data["data"]["repository"]

        branches = r["refs"]["totalCount"]
        collaborators = r["collaborators"]["totalCount"]

        entries = r.get("object", {}).get("entries", [])
        lines = sum(
            e["object"]["text"].count("\n") + 1
            for e in entries
            if e["type"] == "blob" and e.get("object") and e["object"].get("text")
        )
        return {
            "branches": branches,
            "collaborators": collaborators,
            "estimated_lines_of_code": lines,
        }
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from repo_stats import RepoStats

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
stats = RepoStats(extractor)
print(stats.calcular(GITHUB_ORG, REPO_NAME))
```

## Ejemplo de salida

```json
{
  "branches": 12,
  "collaborators": 5,
  "estimated_lines_of_code": 3840
}
```