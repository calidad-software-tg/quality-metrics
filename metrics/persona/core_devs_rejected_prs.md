# Core Devs Rejected PRs — Pull Requests Rechazadas de Desarrolladores Principales

## Descripción

Contabiliza las **Pull Requests cerradas sin fusionar** por cada uno de los desarrolladores principales. Mide cuántas contribuciones de los miembros clave del equipo fueron descartadas sin ser integradas al código base.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `{login: conteo}` | Cantidad de PRs cerradas sin fusionar por cada desarrollador principal |
| `total` | Suma total de PRs rechazadas del equipo principal |

## Cómo se calcula

1. Se obtienen **todas las Pull Requests cerradas** del repositorio via API REST de GitHub (con paginación).
2. De cada PR cerrada, se verifica:
   - Que el autor (`pr.user.login`) esté en la lista de desarrolladores principales.
   - Que `merged_at` sea `null` (fue cerrada sin fusionar).
3. Se cuentan las PRs que cumplen ambas condiciones por desarrollador.

## Para qué sirve

- Identificar qué tan seguido se **descartan contribuciones** de desarrolladores clave.
- Analizar la **eficiencia de las propuestas de código**: muchas PRs rechazadas pueden indicar problemas de calidad, mal entendimiento de requerimientos o conflictos de revisión.
- Evaluar la **comunicación y coordinación** del equipo en el proceso de revisión.

## Interpretación

| Patrón | Interpretación |
|---|---|
| Alto número de PRs rechazadas en un developer | Falta de alineación con estándares, o etapa experimental con mucha prueba y error |
| Rechazos distribuidos entre todos | Proceso de revisión estricto aplicado uniformemente |
| 0 rechazos | Muy pocas PRs o proceso sin revisión formal |

## Dimensión

**Persona**

## Implementación

```python
from github_extractor import GitHubExtractor
from base import Metrica


class CoreDevsRejectedPRs(Metrica):
    nombre = "Pull Requests Rechazadas de Desarrolladores Principales"
    descripcion = (
        "Cuenta las Pull Requests cerradas sin fusionar por cada desarrollador principal. "
        "Identifica contribuciones que no fueron integradas al código base."
    )
    dimension = "Persona"
    interpretacion = (
        "Muchas PRs rechazadas pueden indicar falta de alineación con los estándares del proyecto, "
        "problemas de calidad de código o dificultades en el proceso de revisión."
    )

    def __init__(self, extractor: GitHubExtractor, core_developers: list[str]):
        self._extractor = extractor
        self._core_developers = core_developers

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        prs_cerradas = self._extractor.get_pull_requests(owner, repo, state="closed")
        resultado: dict[str, int] = {dev: 0 for dev in self._core_developers}

        for pr in prs_cerradas:
            autor = pr["user"]["login"]
            if autor in resultado and not pr.get("merged_at"):
                resultado[autor] += 1

        resultado["total"] = sum(v for k, v in resultado.items() if k != "total")
        return resultado
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from core_devs_rejected_prs import CoreDevsRejectedPRs

CORE_DEVELOPERS = ["dev1", "dev2", "dev3"]

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
metric = CoreDevsRejectedPRs(extractor, CORE_DEVELOPERS)
print(metric.calcular(GITHUB_ORG, REPO_NAME))
```

## Ejemplo de salida

```json
{
  "dev1": 3,
  "dev2": 1,
  "dev3": 0,
  "total": 4
}
```