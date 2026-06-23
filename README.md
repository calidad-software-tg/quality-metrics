# Índice de Métricas de Calidad

Documentación de las métricas implementadas en `quality-metrics`. Cada métrica extiende la clase base `Metrica` y expone un método `calcular(owner, repo, limite)` que retorna un diccionario con los resultados.

## Estructura general

Cada métrica tiene su `.py` de implementación y su `.md` de documentación en la misma carpeta:

```
quality-metrics/
├── README.md
├── main.py                        # Punto de entrada — ejecuta las 11 métricas
├── core/
│   ├── base.py                    # Clase abstracta Metrica
│   └── github_extractor.py        # Cliente GitHub REST + GraphQL
├── config/
│   └── settings.py                # Variables de entorno (.env)
└── metrics/
    ├── producto/
    │   ├── churn.py / churn.md
    │   └── repo_stats.py / repo_stats.md
    ├── proceso/
    │   ├── commit_frequency.py / commit_frequency.md
    │   ├── commit_entropy.py / commit_entropy.md
    │   ├── continuous_integration.py / continuous_integration.md
    │   ├── forks_issues_prs.py / forks_issues_prs.md
    │   └── open_pull_requests.py / open_pull_requests.md
    └── persona/
        ├── developer_contribution.py / developer_contribution.md
        ├── developer_ownership.py / developer_ownership.md
        ├── core_devs_prs.py / core_devs_prs.md
        └── core_devs_rejected_prs.py / core_devs_rejected_prs.md
```

## Métricas por dimensión

### Producto

| Métrica | Archivo | Documentación |
|---|---|---|
| Churn (líneas añadidas/eliminadas/cambiadas) | `churn.py` | [churn.md](churn.md) |
| Estadísticas del repositorio (branches, colaboradores, LOC) | `repo_stats.py` | [repo_stats.md](repo_stats.md) |

### Proceso

| Métrica | Archivo | Documentación |
|---|---|---|
| Frecuencia de commits por día | `commit_frequency.py` | [commit_frequency.md](commit_frequency.md) |
| Entropía de commits | `commit_entropy.py` | [commit_entropy.md](commit_entropy.md) |
| Presencia de integración continua | `continuous_integration.py` | [continuous_integration.md](continuous_integration.md) |
| Forks, issues y pull requests | `forks_issues_prs.py` | [forks_issues_prs.md](forks_issues_prs.md) |
| Pull requests abiertas | `open_pull_requests.py` | [open_pull_requests.md](open_pull_requests.md) |
| Centralización del trabajo (Gini) | `centralization_of_work.py` | [centralization_of_work.md](metrics/centralization_of_work/centralization_of_work.md) |
| Tiempo promedio de resolución de issues | `issue_resolution_time.py` | [issue_resolution_time.md](metrics/issue_resolution_time/issue_resolution_time.md) |
| Eficiencia de flujo de trabajo | `workflow_efficiency.py` | [workflow_efficiency.md](metrics/workflow_efficiency/workflow_efficiency.md) |

### Persona

| Métrica | Archivo | Documentación |
|---|---|---|
| Contribución por desarrollador (commits) | `developer_contribution.py` | [developer_contribution.md](developer_contribution.md) |
| Propiedad del código por desarrollador | `developer_ownership.py` | [developer_ownership.md](developer_ownership.md) |
| PRs de desarrolladores principales | `core_devs_prs.py` | [core_devs_prs.md](core_devs_prs.md) |
| PRs rechazadas de desarrolladores principales | `core_devs_rejected_prs.py` | [core_devs_rejected_prs.md](core_devs_rejected_prs.md) |

## API del extractor (`GitHubExtractor`)

| Método | Descripción |
|---|---|
| `get_commits(owner, repo, limite)` | Lista de commits (REST, paginado) |
| `get_commit_files(commit_url)` | Archivos modificados en un commit |
| `get_repo_contents(owner, repo, path)` | Contenido de un directorio del repo |
| `get_pull_requests(owner, repo, state)` | Lista de PRs (REST, paginado) |
| `get_repo_tree(owner, repo, sha)` | Árbol recursivo de archivos del repo |
| `search_issues(query)` | Búsqueda de issues/PRs via API de búsqueda |
| `graphql(query, variables)` | Ejecutar consulta GraphQL arbitraria |

## Configuración

Las credenciales y parámetros del repositorio se leen desde `.env`:

```
GITHUB_TOKEN=ghp_...
GITHUB_ORG=nombre-de-la-org
REPO_NAME=nombre-del-repo
```

Para métricas de desarrolladores principales, se define la lista `CORE_DEVELOPERS` directamente en `main.py` o se agrega como variable de entorno.

## Últimas ejecuciones reales (tldr-pages/tldr, junio 2026)

| Métrica | Resultado |
|---|---|
| Centralización del trabajo (M13) | `{"n_contributors": 3279, "gini_commits": 0.7916}` |
| Tiempo promedio de resolución de issues (C35) | `{"n_issues_cerrados": 1531, "issue_resolution_time_dias": 156.94, "issue_resolution_time_mediana_dias": 11.97}` |
| Eficiencia de flujo de trabajo (M12) | `{"total_issues": 1758, "assigned_issues": 0, "workflow_efficiency": 0.0}` |