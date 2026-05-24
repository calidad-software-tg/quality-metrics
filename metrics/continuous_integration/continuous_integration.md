# Continuous Integration — Presencia de Integración Continua

## Descripción

Verifica si el repositorio contiene **archivos o directorios de configuración de CI** (Integración Continua). La presencia de estos archivos indica que el proyecto automatiza pruebas, compilaciones y despliegues.

## Métricas calculadas

| Métrica | Descripción |
|---|---|
| `has_ci` | `true` si se encontró al menos un archivo de configuración de CI |
| `ci_files_found` | Lista de archivos/directorios de CI detectados en la raíz del repositorio |

## Archivos detectados

| Archivo / Directorio | Sistema de CI |
|---|---|
| `.travis.yml` | Travis CI |
| `.gitlab-ci.yml` | GitLab CI |
| `Jenkinsfile` | Jenkins |
| `.circleci` | CircleCI |
| `.github` | GitHub Actions |

## Cómo se calcula

1. Se obtiene el listado de archivos y directorios en la raíz del repositorio via API REST de GitHub (`/contents`).
2. Se compara cada nombre con el conjunto de identificadores de CI conocidos.
3. Se retorna si se encontró al menos uno y cuáles fueron detectados.

## Interpretación

- **`has_ci: true`**: el proyecto usa CI, lo cual es un indicador positivo de madurez y calidad del proceso de desarrollo.
- **`has_ci: false`**: no se detectó configuración de CI en la raíz. El proyecto podría igualmente tener CI en subdirectorios, o directamente no usarlo.

## Dimensión

**Proceso**

## Implementación

```python
from github_extractor import GitHubExtractor
from base import Metrica

CI_FILES = {".travis.yml", ".gitlab-ci.yml", "Jenkinsfile", ".circleci", ".github"}


class ContinuousIntegration(Metrica):
    nombre = "Integración Continua"
    descripcion = (
        "Verifica si el repositorio contiene archivos de configuración de CI "
        "(Travis CI, GitHub Actions, GitLab CI, CircleCI, Jenkins)."
    )
    dimension = "Proceso"
    interpretacion = (
        "La presencia de CI es un indicador positivo de madurez en el proceso de desarrollo: "
        "automatiza pruebas, compilaciones y despliegues, reduciendo errores manuales."
    )

    def __init__(self, extractor: GitHubExtractor):
        self._extractor = extractor

    def calcular(self, owner: str, repo: str, limite: int = None) -> dict:
        contents = self._extractor.get_repo_contents(owner, repo)
        names = {item["name"] for item in contents}
        found = sorted(CI_FILES & names)
        return {
            "has_ci": bool(found),
            "ci_files_found": found,
        }
```

## Uso

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE, GITHUB_ORG, REPO_NAME
from github_extractor import GitHubExtractor
from continuous_integration import ContinuousIntegration

extractor = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
ci = ContinuousIntegration(extractor)
print(ci.calcular(GITHUB_ORG, REPO_NAME))
```

## Última salida

```json
{
  "has_ci": true,
  "ci_files_found": [".github"]
}
```