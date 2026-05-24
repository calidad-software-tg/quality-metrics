# Churn — Líneas Añadidas, Cambiadas y Eliminadas

## Descripción

Mide el **máximo volumen de cambio** introducido en un solo commit, considerando las líneas añadidas, eliminadas y modificadas por archivo. Permite identificar commits con grandes modificaciones que podrían requerir revisión más detallada.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `max_lines_added` | Mayor cantidad de líneas nuevas introducidas en un solo archivo en cualquier commit |
| `max_lines_deleted` | Mayor cantidad de líneas eliminadas en un solo archivo en cualquier commit |
| `max_lines_changed` | Suma máxima de añadidas + eliminadas (mayor volumen de cambio) |

## Cómo se calcula

1. Se obtienen todos los commits del repositorio via API REST de GitHub.
2. Por cada commit, se consultan los archivos modificados y sus estadísticas (`additions`, `deletions`).
3. Se recorren todos los archivos de todos los commits, actualizando los máximos acumulados.

## Interpretación

- **Valores bajos**: los cambios están distribuidos en commits pequeños y enfocados (buena práctica).
- **Valores altos**: existen commits con grandes volúmenes de cambio que pueden dificultar la revisión de código y aumentar el riesgo de introducir errores.

## Dimensión

**Producto**

## Implementación

```python
from github_extractor import GitHubExtractor
from base import Metrica


class Churn(Metrica):
    nombre = "Churn"
    descripcion = (
        "Máximo de líneas añadidas, eliminadas y modificadas en un único commit. "
        "Mide el volumen máximo de cambio introducido de una sola vez en el repositorio."
    )
    dimension = "Producto"
    interpretacion = (
        "Valores altos indican commits con grandes volúmenes de cambio que podrían "
        "requerir revisión más exhaustiva o señalar refactorizaciones masivas."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        commits = self._extractor.get_commits(owner, repo, limite=limite)
        max_added = max_deleted = max_changed = 0

        for commit in commits:
            for file in self._extractor.get_commit_files(commit["url"]):
                added = file.get("additions", 0)
                deleted = file.get("deletions", 0)
                max_added = max(max_added, added)
                max_deleted = max(max_deleted, deleted)
                max_changed = max(max_changed, added + deleted)

        return {
            "max_lines_added": max_added,
            "max_lines_deleted": max_deleted,
            "max_lines_changed": max_changed,
        }
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from churn import Churn

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
churn = Churn(extractor)
print(churn.calcular(GITHUB_ORG, REPO_NAME))
```

## Última salida

```json
{
  "max_lines_added": 835,
  "max_lines_deleted": 584,
  "max_lines_changed": 945
}
```
