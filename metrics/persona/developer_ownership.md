# Developer Ownership — Propiedad del Código por Desarrollador

## Descripción

Determina qué **porcentaje del código** en un repositorio ha sido escrito por cada desarrollador, basándose en la información de `git blame`. Indica quién fue el último autor en modificar cada línea de cada archivo.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `{login: porcentaje}` | Diccionario con el login de GitHub de cada autor y el porcentaje de líneas que le corresponden |

## Cómo se calcula

1. Se obtiene la lista completa de archivos del repositorio via API REST (`git/trees` recursivo).
2. Para cada archivo, se consulta la API **GraphQL** de GitHub para obtener los rangos de `blame` (quién escribió cada bloque de líneas).
3. Se acumulan las líneas atribuidas a cada autor en todos los archivos.
4. Se calcula el porcentaje de cada autor sobre el total de líneas.

> **Nota**: esta métrica realiza una solicitud GraphQL por cada archivo del repositorio. En repositorios grandes puede ser lenta y consumir cuota de API.

## Interpretación

| Patrón | Significado |
|---|---|
| Un autor con >80% | Concentración alta — riesgo si ese desarrollador abandona el proyecto |
| Distribución equilibrada | Responsabilidad compartida sobre el código |
| Muchos autores con <5% | Contribuciones externas pequeñas o repositorio muy activo |

## Dimensión

**Persona**

## Implementación

```python
from collections import defaultdict

from github_extractor import GitHubExtractor
from base import Metrica

_BLAME_QUERY = """
query($owner: String!, $name: String!, $path: String!) {
  repository(owner: $owner, name: $name) {
    object(expression: "HEAD") {
      ... on Commit {
        blame(path: $path) {
          ranges {
            startingLine
            endingLine
            commit {
              author {
                user { login }
              }
            }
          }
        }
      }
    }
  }
}
"""


class DeveloperOwnership(Metrica):
    nombre = "Propiedad del Código por Desarrollador"
    descripcion = (
        "Calcula el porcentaje de líneas de código atribuidas a cada autor "
        "usando git blame sobre todos los archivos del repositorio (API GraphQL)."
    )
    dimension = "Persona"
    interpretacion = (
        "Un desarrollador con alta propiedad es el principal responsable de esa base de código. "
        "Concentración alta en un solo autor puede ser un riesgo si ese desarrollador abandona el proyecto."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        tree = self._extractor.get_repo_tree(owner, repo)
        archivos = [item["path"] for item in tree if item["type"] == "blob"]
        if limite:
            archivos = archivos[:limite]

        propiedad: dict[str, int] = defaultdict(int)
        total_lineas = 0

        for path in archivos:
            data = self._extractor.graphql(_BLAME_QUERY, {"owner": owner, "name": repo, "path": path})
            ranges = (
                data.get("data", {})
                    .get("repository", {})
                    .get("object", {})
                    .get("blame", {})
                    .get("ranges", [])
            )
            for rango in ranges:
                usuario = rango["commit"]["author"].get("user")
                if usuario:
                    lineas = rango["endingLine"] - rango["startingLine"] + 1
                    propiedad[usuario["login"]] += lineas
                    total_lineas += lineas

        if total_lineas == 0:
            return {}
        return {autor: round((l / total_lineas) * 100, 2) for autor, l in propiedad.items()}
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from developer_ownership import DeveloperOwnership

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
ownership = DeveloperOwnership(extractor)
print(ownership.calcular(GITHUB_ORG, REPO_NAME))
```

## Ejemplo de salida

```json
{
  "mariag": 62.4,
  "juanl": 28.1,
  "anam": 9.5
}
```