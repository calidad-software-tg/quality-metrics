# M33 – Development Velocity (Velocidad de Desarrollo)

---

## 1. Descripción

La métrica **Development Velocity** cuantifica la velocidad de avance del proceso de desarrollo, medida como la cantidad de contribuciones completadas e integradas al repositorio por unidad de tiempo.

Su fundamento empírico proviene de Jarczyk et al. (2018), quienes estudian el rendimiento del proceso de desarrollo (**Development Process Performance**) en proyectos OSS de GitHub. El paper identifica el **número de commits** como la medida de "actividad bruta del desarrollador" y "cantidad de trabajo realizado en un proyecto", usándola explícitamente como variable de rendimiento del proceso junto a las tasas de cierre de issues. Los autores demuestran que el número de commits está positivamente influenciado por la estructura de la red social del equipo y la centralización del trabajo (coeficiente Gini), validando que esta métrica captura el ritmo real de producción del equipo.

> **Nota de correspondencia:** La fórmula de la planilla (`completed_tasks_or_story_points / time_period`) no tiene un equivalente directo en tldr-pages, dado que el repositorio no usa sprints, story points ni milestones formales. Se operacionaliza mediante **PRs mergeados por unidad de tiempo** como medida primaria de "tareas completadas", ya que en tldr-pages cada PR mergeado representa una contribución aceptada e integrada al repositorio. Los commits se incluyen como medida secundaria, consistente con la operacionalización de Jarczyk et al. (2018). La métrica relacionada **Commit Frequency** (ID Registro 34) complementa esta especificación con una implementación ya disponible en el repositorio.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | Sí |
| **Producto** | No | No |

Ítem de encuesta asociado: **C4 – La velocidad de desarrollo** (ID Consigna: 4).

La relación con el ítem es **directa**: la velocidad de desarrollo se mide por la cantidad de trabajo completado por unidad de tiempo. Los PRs mergeados son el indicador más preciso de "tarea completada" en tldr-pages, mientras que los commits representan la actividad bruta de desarrollo.

---

## 3. Fórmula de cálculo

### Fórmula primaria — PRs mergeados por unidad de tiempo

$$\text{Development Velocity}_{PR} = \frac{\text{merged\_prs}}{\Delta t}$$

Donde:
- **merged\_prs**: cantidad de pull requests mergeados en el período analizado.
- **Δt**: período de tiempo en días, semanas o meses.

**Por qué PRs mergeados como fórmula primaria para tldr-pages:**
En tldr-pages, el flujo de trabajo es estrictamente basado en PRs: cada nueva página o corrección se integra exclusivamente a través de un PR revisado y mergeado por un maintainer. Un PR mergeado representa una contribución completa, revisada y aceptada — el equivalente más fiel a una "tarea completada" en este repositorio.

### Fórmula secundaria — Commits por unidad de tiempo

$$\text{Development Velocity}_{commit} = \frac{\text{num\_commits}}{\Delta t}$$

Esta es la operacionalización directa de Jarczyk et al. (2018) y está ya implementada en el repositorio como `commit_frequency` (ID Registro 34). Incluye commits de merge automáticos, por lo que puede sobreestimar la actividad real en comparación con la fórmula primaria.

> **Decisión metodológica:** Se propone reportar ambas variantes. La fórmula de PRs mergeados es más precisa para tldr-pages; la de commits permite comparación con otros proyectos y con la literatura existente. El **Riesgo de Sesgo Computacional es Alto** (según planilla) porque ambas métricas pueden verse infladas por eventos como Hacktoberfest (octubre) o reducidas en períodos de baja actividad voluntaria.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `merged_prs` | PRs mergeados en el período | entero ≥ 0 | GraphQL `pullRequests(states: MERGED)` con filtro de fecha |
| `num_commits` | Total de commits en el período | entero ≥ 0 | REST `GET /repos/{owner}/{repo}/commits` con filtro `since`/`until` |
| `delta_t` | Período de tiempo analizado | días | Definido en la configuración de extracción |
| `velocity_prs_per_week` | PRs mergeados por semana | ratio ≥ 0 | `merged_prs / (delta_t / 7)` |
| `velocity_commits_per_week` | Commits por semana | ratio ≥ 0 | `num_commits / (delta_t / 7)` |
| `repo_created_at` | Fecha de creación del repositorio | timestamp ISO 8601 | GraphQL `repository { createdAt }` |

---

## 5. Fuente de datos

Esta métrica usa exclusivamente la **API de GitHub**, sin necesidad del historial local de commits para la fórmula primaria. Para la fórmula secundaria puede usarse `GitExtractor` (ya implementado en el repo).

| Llamada | Método | Dato obtenido |
|---------|--------|---------------|
| GraphQL `pullRequests(states: MERGED, first: N)` con filtros de fecha | `extractor.graphql(query, vars)` | `merged_prs` por período |
| REST `GET /repos/{owner}/{repo}/commits?since=&until=` | `extractor.get_paginated(endpoint)` | `num_commits` por período |
| GraphQL `repository { createdAt }` | `extractor.graphql(query, vars)` | `repo_created_at` |

> **Nota:** La fórmula secundaria (commits) ya está implementada en `metrics/commit_frequency/commit_frequency.py`. No es necesario reimplementarla; puede reutilizarse directamente.

---

## 6. Calculabilidad en tldr-pages/tldr

**Sí, calculable.**

tldr-pages/tldr tiene un workflow 100% basado en PRs. Todos los cambios al repositorio pasan por un PR revisado y mergeado, lo que hace que `merged_prs` sea una medida especialmente representativa de la velocidad de desarrollo para este proyecto específico.

El repositorio tiene miles de PRs mergeados históricamente (el badge del repositorio muestra el conteo actualizado), y tanto PRs como commits son accesibles via GitHub API para repositorios públicos.

> **Consideración de sesgo:** Octubre es significativamente más activo por Hacktoberfest. Se recomienda calcular la velocidad excluyendo octubre o reportarla por mes para identificar esta estacionalidad.

---

## 7. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | `total_merged_prs / días_desde_creación`. Valor de referencia histórico. |
| **Anual** | PRs mergeados y commits por año calendario. **Recomendada** para capturar evolución y estacionalidad. |
| **Mensual** | Permite detectar picos (Hacktoberfest) y períodos de baja actividad. |

---

## 8. Rangos de interpretación

Orientativos para la **tasa semanal de PRs mergeados** en un repositorio de documentación colaborativa:

| Rango (PRs/semana) | Interpretación |
|---|---|
| **< 5** | Velocidad baja. Actividad esporádica o equipo de maintainers con poca disponibilidad. |
| **5 – 20** | Velocidad moderada. Proyecto activo con contribuciones regulares. |
| **20 – 60** | Velocidad alta. Comunidad activa, posiblemente con eventos de contribución. |
| **> 60** | Velocidad muy alta. Típico de períodos Hacktoberfest o campañas de contribución masiva. |

Jarczyk et al. (2018) muestran que el número de commits (velocidad bruta) está positivamente influenciado por la densidad de la red de discusión del equipo y la similitud de habilidades entre desarrolladores, lo que sugiere que equipos más cohesivos alcanzan mayor velocidad de desarrollo sostenida.

---

## 9. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, API_BASE
from core.github_extractor import GitHubExtractor
from metrics.development_velocity.development_velocity import DevelopmentVelocity

extractor = GitHubExtractor(token=GITHUB_TOKEN, api_base=API_BASE)
metrica = DevelopmentVelocity(extractor)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")
```

Salida esperada (valores orientativos para tldr-pages/tldr):

```python
{
    "repo_created_at": "2013-12-15T00:00:00Z",
    "delta_t_days": 4556,
    "merged_prs_total": 21739,
    "velocity_prs_per_week": 33.4,
    "num_commits_total": 21739,
    "velocity_commits_per_week": 33.4,
    "velocity_by_year": {
        "2021": {"merged_prs": 2841, "prs_per_week": 54.6},
        "2022": {"merged_prs": 3102, "prs_per_week": 59.7},
        "2023": {"merged_prs": 2987, "prs_per_week": 57.4},
        "2024": {"merged_prs": 2654, "prs_per_week": 51.0},
        "2025": {"merged_prs": 1543, "prs_per_week": 29.7}
    }
}
```

$$\text{Development Velocity}_{PR} = \frac{21739}{4556} \times 7 \approx 33.4 \text{ PRs/semana}$$

> **Nota:** En tldr-pages, el número de commits y PRs mergeados coincide aproximadamente porque cada PR suele ser squashed a un único commit al mergearse.

---

## 10. Relación con el ítem de encuesta

> **C4 – La velocidad de desarrollo**

La relación es **directa**: los PRs mergeados por unidad de tiempo miden exactamente la velocidad a la que el equipo integra trabajo completado al repositorio. Jarczyk et al. (2018) validan empíricamente que el número de commits — medida equivalente — es el indicador más directo de la actividad de desarrollo en proyectos OSS de GitHub.

---

## 11. Relación con métricas del mismo grupo

La consigna C4 tiene dos registros asociados en la planilla:

| ID Registro | Métrica | Relación |
|---|---|---|
| **33** | Development Velocity (este MD) | Concepto amplio: `completed_tasks / time_period` operacionalizado como PRs mergeados/semana |
| **34** | Commit Frequency | Métrica relacionada: `count(commits) / time_period`, ya implementada en `metrics/commit_frequency/` |

Ambas son complementarias. Se recomienda reportar las dos para dar una imagen completa de la velocidad de desarrollo.

---

## 12. Observaciones metodológicas

- **Riesgo de Sesgo Computacional Alto** (según planilla): Hacktoberfest (octubre) puede triplicar la velocidad mensual. Los commits de merge automáticos pueden inflar la métrica secundaria. Se recomienda reportar la distribución mensual junto al valor global.
- En tldr-pages, commits y PRs mergeados son prácticamente equivalentes por el uso de squash merge, lo que simplifica la interpretación.
- La fórmula secundaria (commits) ya está implementada en el repo — no reimplementar.

---

## 13. Referencias

- Jarczyk, O., Jaroszewicz, S., Wierzbicki, A., Pawlak, K., & Jankowski-Lorek, M. (2018). Surgical teams on GitHub: Modeling performance of GitHub project development processes. *Information and Software Technology*, 100, 130–143. https://doi.org/10.1016/j.infsof.2018.03.010

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.