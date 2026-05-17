# Developer Contribution — Contribución por Desarrollador

## Descripción

Cuantifica la **cantidad de commits realizados por cada autor** en el repositorio. Permite analizar la distribución del trabajo entre colaboradores y entender la dinámica del equipo de desarrollo.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `{autor: conteo}` | Diccionario con el nombre de cada autor y la cantidad de commits que realizó |

## Cómo se calcula

1. Se obtienen todos los commits del repositorio via API REST de GitHub.
2. Por cada commit, se extrae el nombre del autor desde `commit.author.name`.
3. Se cuentan los commits agrupados por autor usando un `Counter`.

## Interpretación

| Patrón | Significado |
|---|---|
| Distribución muy desigual | Dependencia de pocos autores — bus factor alto, riesgo si esos desarrolladores no están disponibles |
| Distribución uniforme | Colaboración balanceada entre el equipo |
| Un único autor | Proyecto individual o contribuciones externas muy bajas |

## Dimensión

**Persona**

## Implementación

```python
from collections import Counter

from github_extractor import GitHubExtractor
from base import Metrica


class DeveloperContribution(Metrica):
    nombre = "Contribución por Desarrollador"
    descripcion = (
        "Cuenta cuántos commits realizó cada autor en el repositorio. "
        "Permite analizar la distribución del trabajo entre colaboradores."
    )
    dimension = "Persona"
    interpretacion = (
        "Una distribución muy desigual puede indicar dependencia de pocos autores (bus factor alto). "
        "Una distribución uniforme refleja colaboración balanceada entre el equipo."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        commits = self._extractor.get_commits(owner, repo, limite=limite)
        autores = [c["commit"]["author"]["name"] for c in commits]
        return dict(Counter(autores))
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from developer_contribution import DeveloperContribution

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
contrib = DeveloperContribution(extractor)
print(contrib.calcular(GITHUB_ORG, REPO_NAME))
```

## Ejemplo de salida

```json
{
  "María García": 87,
  "Juan López": 43,
  "Ana Martínez": 12
}
```