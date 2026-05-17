# Commit Frequency — Frecuencia de Commits por Día

## Descripción

Representa la **cantidad de commits realizados por día** en el repositorio. Es útil para analizar la actividad del proyecto a lo largo del tiempo y detectar patrones de desarrollo, períodos de alta actividad o inactividad.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `{fecha: conteo}` | Diccionario con cada fecha (`YYYY-MM-DD`) y la cantidad de commits realizados ese día |

## Cómo se calcula

1. Se obtienen todos los commits del repositorio via API REST de GitHub.
2. Por cada commit, se extrae la fecha de autoría (`commit.author.date`) en formato `YYYY-MM-DD`.
3. Se cuentan los commits agrupados por fecha usando un `Counter`.

## Interpretación

- **Días con muchos commits**: alta actividad, posiblemente previo a un release o sprint.
- **Días con cero commits**: inactividad, fines de semana, feriados o pausas del proyecto.
- **Distribución uniforme**: desarrollo constante y sostenido.
- **Picos aislados**: posible trabajo acumulado o fechas límite.

## Dimensión

**Proceso**

## Implementación

```python
from collections import Counter

import matplotlib.pyplot as plt

from github_extractor import GitHubExtractor
from base import Metrica


class CommitFrequency(Metrica):
    nombre = "Frecuencia de Commits"
    descripcion = (
        "Cantidad de commits realizados por día en el repositorio. "
        "Permite analizar la distribución temporal de la actividad de desarrollo."
    )
    dimension = "Proceso"
    interpretacion = (
        "Picos de actividad pueden coincidir con releases o deadlines. "
        "Una distribución uniforme refleja un ritmo de desarrollo sostenido."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        commits = self._extractor.get_commits(owner, repo, limite=limite)
        fechas = [c["commit"]["author"]["date"][:10] for c in commits]
        return dict(Counter(fechas))

    def graficar(self, frecuencia: dict, titulo: str = "Frecuencia de Commits por Día"):
        fechas, conteos = zip(*sorted(frecuencia.items()))
        plt.figure(figsize=(10, 6))
        plt.bar(fechas, conteos)
        plt.xlabel("Fecha")
        plt.ylabel("Número de Commits")
        plt.title(titulo)
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from commit_frequency import CommitFrequency

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
freq = CommitFrequency(extractor)
resultado = freq.calcular(GITHUB_ORG, REPO_NAME)
freq.graficar(resultado)
```

## Ejemplo de salida

```json
{
  "2024-01-15": 3,
  "2024-01-16": 7,
  "2024-01-17": 1,
  "2024-01-20": 5
}
```