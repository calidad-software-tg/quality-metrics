# Core Devs PRs — Pull Requests de Desarrolladores Principales

## Descripción

Cuenta cuántos **Pull Requests creó cada uno de los desarrolladores principales** del proyecto. Los desarrolladores principales se definen en la configuración (`CORE_DEVELOPERS`).

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `{login: conteo}` | Cantidad de PRs creadas por cada desarrollador principal |
| `total` | Suma total de PRs de todos los desarrolladores principales |

## Cómo se calcula

Para cada desarrollador en la lista:
1. Se consulta la **API de búsqueda de GitHub** con el filtro `repo:<owner>/<repo>+type:pr+author:<login>`.
2. Se obtiene el `total_count` de la respuesta.
3. Se suman los resultados individuales para calcular el total del equipo.

## Para qué sirve

- Medir el **nivel de participación individual** de los miembros clave en el desarrollo.
- Evaluar la **carga de trabajo** o compromiso de cada desarrollador.
- Identificar **patrones de colaboración** y posibles desequilibrios en la distribución de tareas.

## Interpretación

| Patrón | Interpretación |
|---|---|
| Un developer con muchas más PRs que otros | Podría estar asumiendo mayor responsabilidad o estar sobrecargado |
| Distribución similar entre developers | Equipo bien balanceado en términos de contribuciones |
| Total bajo del equipo | Equipo pequeño, fase temprana del proyecto, o uso de otro flujo de trabajo |

## Dimensión

**Persona**

## Implementación

```python
from github_extractor import GitHubExtractor
from base import Metrica


class CoreDevsPRs(Metrica):
    nombre = "Pull Requests de Desarrolladores Principales"
    descripcion = (
        "Cuenta cuántos Pull Requests creó cada uno de los desarrolladores principales "
        "definidos en la configuración, usando la API de búsqueda de GitHub."
    )
    dimension = "Persona"
    interpretacion = (
        "Permite evaluar el nivel de participación individual de los desarrolladores clave "
        "y detectar desigualdades en la distribución de tareas."
    )

    def __init__(self, extractor: GitHubExtractor, core_developers: list[str]):
        self._extractor = extractor
        self._core_developers = core_developers

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        resultado: dict[str, int] = {}
        for dev in self._core_developers:
            query = f"repo:{owner}/{repo}+type:pr+author:{dev}"
            data = self._extractor.search_issues(query)
            resultado[dev] = data.get("total_count", 0)
        resultado["total"] = sum(resultado.values())
        return resultado
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from core_devs_prs import CoreDevsPRs

CORE_DEVELOPERS = ["dev1", "dev2", "dev3"]

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
metric = CoreDevsPRs(extractor, CORE_DEVELOPERS)
print(metric.calcular(GITHUB_ORG, REPO_NAME))
```

## Ejemplo de salida

```json
{
  "dev1": 24,
  "dev2": 31,
  "dev3": 9,
  "total": 64
}
```