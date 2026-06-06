# M28 – Number of Open Issues (Cantidad de Issues Abiertos)

---

## 1. Descripción

La métrica **Number of Open Issues** cuantifica la cantidad total de issues que se encuentran en estado abierto en un repositorio de GitHub en un momento dado. Representa el backlog de problemas, solicitudes de funcionalidades o tareas pendientes de resolución reportadas por usuarios y colaboradores del proyecto.

Su fundamento empírico proviene de dos estudios del mismo grupo de investigación. Jarczyk et al. (2014) identifican la gestión de issues como uno de los dos indicadores clave de calidad en proyectos GitHub, definiendo la *quality of support* en función del tiempo de cierre de issues. Jarczyk et al. (2018) incluyen explícitamente `Number of Open Issues` en su catálogo de 209 métricas de proyectos OSS en GitHub, utilizándola como variable de referencia en los modelos de performance de procesos de desarrollo. Complementariamente, Gyimesi et al. (2015) utilizan el número de issues abiertos como una de las métricas extraídas desde GitHub para caracterizar defectos en proyectos Java de código abierto, validando su extractabilidad directa desde la API.

> **Nota:** La métrica tiene correspondencia directa y literal con la consigna C43 — "Cantidad de problemas (issues) abiertos en su repositorio" — sin requerir transformación conceptual.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | No |
| **Producto** | Sí | Sí |

Ítem de encuesta asociado: **C43 – Cantidad de problemas (issues) abiertos en su repositorio** (ID Consigna: 43).

La relación con el ítem es **directa**: la consigna reproduce prácticamente sin transformación la definición de la métrica original, solicitando el conteo de issues abiertos en el repositorio principal.

---

## 3. Fórmula de cálculo

$$\text{Number of Open Issues} = \text{count}(\text{issues con estado} = \text{open})$$

Donde:
- Se cuentan únicamente issues en estado `open` al momento de la extracción.
- Se excluyen pull requests (GitHub los incluye en el mismo endpoint por defecto; deben filtrarse explícitamente).
- No se incluyen issues cerrados ni issues de repositorios forks.

El resultado es un **conteo absoluto** ∈ ℕ₀.

> **Decisión metodológica:** GitHub retorna pull requests junto a issues en el endpoint general. Es necesario filtrar por `is:issue` para obtener solo issues reales. Los bots (e.g., `github-actions[bot]`, `dependabot[bot]`) pueden abrir issues automáticamente; se recomienda registrar si se incluyen o no para transparencia metodológica.

### Implementación Python

Sigue el mismo patrón que `WorkflowEfficiency` y `ForksIssuesPRs`: clase que extiende `Metrica`, recibe `GitHubExtractor` en el constructor y expone `calcular(owner, repo)`. Requiere una sola llamada:

1. **GraphQL** — `repository { openIssues: issues(states: OPEN) { totalCount } }` → `open_issues_count`

O alternativamente:

1. **REST** — `GET /repos/{owner}/{repo}` → campo `open_issues_count` (incluye PRs, requiere corrección)
2. **REST Search** — `search_issues(f"repo:{owner}/{repo} is:issue state:open")` → `total_count`

> **Alternativa recomendada:** GraphQL con `states: OPEN` filtra correctamente issues sin incluir PRs, en una sola query sin paginación.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `open_issues_count` | Total de issues en estado open al momento de la extracción | entero ≥ 0 | GraphQL `issues(states: OPEN) { totalCount }` o REST Search API |
| `extraction_date` | Fecha y hora de la extracción (el valor es puntual) | timestamp ISO 8601 | Registrado en el momento de ejecución |

---

## 5. Fuente de datos

Esta métrica usa exclusivamente la **API de GitHub**, sin necesidad del historial local de commits. Utiliza `GitHubExtractor` igual que `WorkflowEfficiency` y `ForksIssuesPRs`.

| Llamada | Método en `GitHubExtractor` | Dato obtenido |
|---------|-----------------------------|---------------|
| GraphQL `issues(states: OPEN) { totalCount }` | `extractor.graphql(query, vars)` | `open_issues_count` |
| REST Search `is:issue state:open` | `extractor.search_issues(query)` | `open_issues_count` (alternativa) |

---

## 6. Calculabilidad en tldr-pages/tldr

**Sí, calculable.**

El repositorio tldr-pages/tldr tiene issues habilitados y activos. Al momento de la verificación (junio 2026) el repositorio contaba con aproximadamente **203 issues abiertos**, confirmando que la métrica es directamente extraíble.

El cálculo es trivial: una sola llamada a la API de GitHub retorna el valor exacto. No hay ambigüedad metodológica, no requiere preprocesamiento ni decisiones de modelado.

> **Consideración:** El valor es dinámico — varía a lo largo del tiempo a medida que se abren y cierran issues. Se recomienda registrar la fecha exacta de extracción junto al valor calculado para garantizar reproducibilidad.

---

## 7. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Puntual (snapshot)** | Valor al momento de la extracción. Es la granularidad natural de esta métrica. **Recomendada como valor primario.** |
| **Serie temporal** | Registrar el valor en diferentes fechas (e.g., mensualmente) para observar la evolución del backlog. Requiere múltiples extracciones o consulta a la GitHub Archive API. |

Para tldr-pages/tldr se recomienda registrar el valor en el momento de extracción del dataset, junto con la fecha, para permitir comparaciones futuras.

---

## 8. Rangos de interpretación

No existen umbrales formales en la literatura para esta métrica de forma aislada. Los siguientes rangos son orientativos y deben interpretarse en relación al tamaño y actividad del proyecto:

| Rango | Interpretación |
|-------|---------------|
| **0 – 10** | Backlog muy bajo. Proyecto con alta capacidad de resolución o baja actividad de reporte. |
| **11 – 100** | Backlog moderado. Común en proyectos activos con equipo de mantenimiento pequeño. |
| **101 – 500** | Backlog alto. Proyecto popular con más reportes de los que el equipo puede resolver en el corto plazo. |
| **> 500** | Backlog muy alto. Proyectos de gran escala o con recursos de mantenimiento limitados respecto al volumen de reportes. |

Jarczyk et al. (2014) señalan que proyectos con alta tasa de cierre de issues tienen mejor calidad de soporte, lo que implica que un backlog elevado puede indicar dificultades en la gestión de issues, aunque no necesariamente baja calidad del producto.

---

## 9. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, API_BASE
from core.github_extractor import GitHubExtractor
from metrics.number_of_open_issues.number_of_open_issues import NumberOfOpenIssues

extractor = GitHubExtractor(token=GITHUB_TOKEN, api_base=API_BASE)
metrica = NumberOfOpenIssues(extractor)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")
```

Salida esperada (valores reales aproximados para tldr-pages/tldr, junio 2026):

```python
{
    "open_issues_count": 203,
    "extraction_date": "2026-06-06T19:00:00Z"
}
```

$$\text{Number of Open Issues} = 203$$

Un valor de ~200 issues abiertos es consistente con un proyecto open source maduro y activo, donde la comunidad reporta activamente nuevas páginas faltantes y mejoras, pero el volumen de contributors voluntarios limita la velocidad de resolución.

---

## 10. Relación con el ítem de encuesta

> **C43 – Cantidad de problemas (issues) abiertos en su repositorio**

La relación es **directa**: el ítem de encuesta reproduce prácticamente sin transformación la definición de la métrica. No hay brecha semántica entre lo que pregunta la consigna y lo que mide la métrica. Es uno de los casos de mayor fidelidad operacional en el catálogo.

---

## 11. Observaciones metodológicas

- La métrica tiene **Fidelidad Operacional Alta** según la clasificación de la planilla: la consigna conserva prácticamente sin transformación una métrica objetiva y observable.
- El campo `open_issues_count` de la API REST de GitHub **incluye pull requests** en su conteo. Es imprescindible usar GraphQL con `states: OPEN` o la Search API con `is:issue` para obtener el valor correcto.
- El valor es **puntual en el tiempo**. Para análisis longitudinales, se recomienda complementar con datos históricos de la GitHub Archive.
- Gyimesi et al. (2015) utilizan `number of opened issues` como una de sus métricas de caracterización extraídas desde GitHub, validando la operacionalización propuesta aquí.

---

## 12. Referencias

- Jarczyk, O., Jaroszewicz, S., Wierzbicki, A., Pawlak, K., & Jankowski-Lorek, M. (2018). Surgical teams on GitHub: Modeling performance of GitHub project development processes. *Information and Software Technology*, 100, 130–143. https://doi.org/10.1016/j.infsof.2018.03.010

- Jarczyk, O., Gruszka, B., Jaroszewicz, S., Bukowski, L., & Wierzbicki, A. (2014). GitHub Projects. Quality Analysis of Open-Source Software. In L. M. Aiello & D. McFarland (Eds.), *Social Informatics* (Vol. 8851, pp. 80–94). Springer. https://doi.org/10.1007/978-3-319-13734-6_6

- Gyimesi, P., Gyimesi, G., Tóth, Z., & Ferenc, R. (2015). Characterization of Source Code Defects by Data Mining Conducted on GitHub. In O. Gervasi et al. (Eds.), *Computational Science and Its Applications – ICCSA 2015* (Vol. 9159, pp. 47–62). Springer. https://doi.org/10.1007/978-3-319-21413-9_4

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.