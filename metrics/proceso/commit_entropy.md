# Commit Entropy — Entropía de los Commits

## Descripción

Mide la **dispersión de los cambios en los commits** del repositorio, basándose en cuántos archivos son modificados por commit. Utiliza la **entropía de Shannon** para cuantificar la variabilidad: a mayor entropía, más heterogéneo es el tamaño de los commits en términos de archivos tocados.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `entropy` | Entropía de Shannon (base 2) de la distribución de archivos modificados por commit |

## Cómo se calcula

1. Se obtienen todos los commits del repositorio via API REST de GitHub.
2. Para cada commit, se consultan sus archivos modificados y se cuenta cuántos son.
3. Se construye la distribución de frecuencias de esos conteos.
4. Se aplica la fórmula de entropía de Shannon:

```
H = -Σ p(x) · log₂(p(x))
```

donde `p(x)` es la probabilidad de que un commit haya modificado `x` archivos.

## Interpretación

| Valor | Significado |
|---|---|
| Entropía baja | Commits consistentes: la mayoría toca un número similar de archivos (mayor cohesión) |
| Entropía alta | Commits muy variados: algunos tocan 1 archivo, otros decenas (menor cohesión) |

## Dimensión

**Proceso**

## Implementación

```python
from math import log2
from collections import Counter

from github_extractor import GitHubExtractor
from base import Metrica


class CommitEntropy(Metrica):
    nombre = "Entropía de Commits"
    descripcion = (
        "Mide la dispersión de los cambios en los commits usando la entropía de Shannon. "
        "Cuantifica la variabilidad en la cantidad de archivos modificados por commit."
    )
    dimension = "Proceso"
    interpretacion = (
        "Entropía baja: commits específicos y cohesivos que afectan pocos archivos. "
        "Entropía alta: commits dispersos que tocan muchos archivos distintos."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        commits = self._extractor.get_commits(owner, repo, limite=limite)
        file_counts = [
            len(self._extractor.get_commit_files(c["url"]))
            for c in commits
        ]
        if not file_counts:
            return {"entropy": 0.0}

        total = len(file_counts)
        freq = Counter(file_counts)
        entropy = -sum((c / total) * log2(c / total) for c in freq.values())
        return {"entropy": round(entropy, 4)}
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from commit_entropy import CommitEntropy

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
entropy = CommitEntropy(extractor)
print(entropy.calcular(GITHUB_ORG, REPO_NAME))
```

## Ejemplo de salida

```json
{
  "entropy": 2.3471
}
```