# M12 – Workflow Efficiency (Eficiencia de Flujo de Trabajo)

---

## 1. Descripción

La métrica **Workflow Efficiency** cuantifica el grado en que un proyecto hace uso de mecanismos formales de gestión de issues, específicamente la práctica de asignar issues a desarrolladores concretos. Se calcula como el porcentaje de issues con al menos un *assignee* explícito sobre el total de issues reportados en el repositorio.

Su relevancia fue demostrada empíricamente por Jarczyk et al. (2018) mediante la variable sintética `A_D_issue_rep_assign` ("Activity in issue handling infrastructure"), que resultó ser el predictor con mayor peso estadístico en los modelos de cierre de issues del estudio: coeficientes estandarizados de 0.229 (cierre a 3 días) y 0.422 (cierre a 365 días), ambos con p-valor < 1×10⁻¹⁶.

La métrica se enmarca en el concepto del *surgical team* de Brooks: un grupo reducido de desarrolladores líderes que distribuye y asigna el trabajo al resto del equipo mediante mecanismos formales.

> **Nota:** `A_D_issue_rep_assign` es una variable sintética construida con PCA; la fórmula propuesta aquí es una operacionalización propia inspirada en ella, no una transcripción directa.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | Sí |
| **Producto** | No | No |

Ítem de encuesta asociado: **C53 – La eficacia en la asignación de tareas** (orden ISL: 22).

---

## 3. Fórmula de cálculo

$$\text{Workflow Efficiency} = \frac{\text{assigned_issues}}{\text{total_issues}} \times 100$$

Donde:
- **assigned\_issues**: issues con al menos un *assignee* registrado en GitHub.
- **total\_issues**: total de issues del repositorio (abiertos + cerrados).

Resultado: porcentaje ∈ [0, 100].

### Implementación Python

Sigue el mismo patrón que `ForksIssuesPRs`: clase que extiende `Metrica`, recibe `GitHubExtractor` en el constructor y expone `calcular(owner, repo)`. Requiere **2 requests fijos**:

1. **GraphQL** — `issues { totalCount }` → `total_issues`
2. **REST Search API** — `search_issues(f"repo:{owner}/{repo} is:issue is:assigned")` → campo `total_count`

El método `search_issues` ya existe en `core/github_extractor.py:34`.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `total_issues` | Total de issues (abiertos + cerrados) | entero ≥ 0 | GraphQL `issues { totalCount }` |
| `assigned_issues` | Issues con al menos un *assignee* | entero ≥ 0 | REST Search `is:issue is:assigned` → `total_count` |
| `workflow_efficiency` | Resultado de la fórmula | % ∈ [0, 100] | Calculado |

---

## 5. Fuente de datos en el historial Git

Esta métrica no usa el historial de commits sino la API de GitHub, igual que `ForksIssuesPRs` y `ContinuousIntegration`.

| Llamada | Método en `GitHubExtractor` | Dato obtenido |
|---------|-----------------------------|---------------|
| GraphQL `issues { totalCount }` | `extractor.graphql(query, vars)` | `total_issues` |
| REST Search `is:issue is:assigned` | `extractor.search_issues(query)` | `assigned_issues` |

---

## 6. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | Sin filtro de fecha. Es la granularidad de Jarczyk et al. (2018). **Recomendada como valor primario.** |
| **Anual** | Agregar `created:YYYY-01-01..YYYY-12-31` a ambas queries para capturar evolución temporal. |
| **Por release** | Usar `created:fecha_tag_anterior..fecha_tag_nuevo`. |

Para tldr-pages/tldr se recomienda calcular el valor global más una serie anual desde la creación del repositorio.

---

## 7. Rangos de interpretación

Orientativos; no existen umbrales formales en la literatura.

| Rango | Interpretación |
|-------|---------------|
| **0% – 10%** | Uso muy escaso del workflow formal. Gestión informal o reactiva de issues. |
| **11% – 40%** | Uso moderado. Existe alguna práctica de asignación pero no es sistemática. |
| **41% – 70%** | Uso activo. La mayoría de los issues relevantes tienen asignado un responsable. |
| **71% – 100%** | Uso intensivo. Correlaciona positivamente con tasas de cierre a corto y largo plazo (Jarczyk et al., 2018). |

---

## 8. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, API_BASE
from core.github_extractor import GitHubExtractor
from metrics.workflow_efficiency.workflow_efficiency import WorkflowEfficiency

extractor = GitHubExtractor(token=GITHUB_TOKEN, api_base=API_BASE)
metrica = WorkflowEfficiency(extractor)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")
```

Salida esperada (valores orientativos):

```python
{
    "total_issues": 3842,
    "assigned_issues": 312,
    "workflow_efficiency": 8.12
}
```

$$\text{Workflow Efficiency} = \frac{312}{3842} \times 100 \approx 8.12\%$$

Un valor en el rango 0–10% es esperable para tldr-pages/tldr dado su modelo de contribución open source distribuido, donde la mayoría de los issues son resueltos por contribuciones voluntarias sin asignación explícita previa.

---

## 9. Relación con el ítem de encuesta

> **C53 – La eficacia en la asignación de tareas**

La operacionalización propuesta (porcentaje de issues asignados) mide directamente la práctica que el ítem evalúa: cuán sistemáticamente el equipo asigna responsabilidades formales sobre los issues reportados. La dimensión Persona se agrega en la encuesta porque la asignación de issues implica decisiones sobre las personas responsables de cada tarea.

---

## 10. Referencias

- Jarczyk, O., Jaroszewicz, S., Wierzbicki, A., Pawlak, K., & Jankowski-Lorek, M. (2018). Surgical teams on GitHub: Modeling performance of GitHub project development processes. *Information and Software Technology*, 100, 130–143. https://doi.org/10.1016/j.infsof.2018.03.010

- Chengalur-Smith, I., Sidorova, A., & Daniel, S. (2010). Sustainability of free/libre open source projects: a longitudinal study. *Journal of the Association for Information Systems*, 11(11), 657.

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.