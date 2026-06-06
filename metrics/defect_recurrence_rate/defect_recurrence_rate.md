# M32 – Defect Recurrence Rate (Tasa de Defectos Recurrentes)

---

## 1. Descripción

La métrica **Defect Recurrence Rate** cuantifica la proporción de defectos que reaparecen o se manifiestan nuevamente después de haber sido corregidos, medida como el ratio entre issues reabiertos y el total de issues cerrados en el repositorio.

Su fundamento empírico proviene de Colakoglu et al. (2021), quienes en su estudio sistemático de métricas de calidad de producto de software identifican **Customer-Found Defects and Regressions** como una métrica de nivel de sistema asociada al atributo de calidad de **confiabilidad** (reliability) del modelo ISO 25010. En ese marco, las regresiones — defectos que reaparecen tras haber sido corregidos — son el fenómeno más directamente relacionado con la recurrencia de errores. La métrica propuesta aquí operacionaliza ese concepto a través de los mecanismos de reapertura de issues disponibles en GitHub.

> **Nota de correspondencia:** La métrica canónica "Customer-Found Defects and Regressions" del catálogo ISL/JAIIO 2022 (referencia [21] en Colakoglu et al., 2021) se relaciona con la consigna C7 de forma **indirecta**: mide defectos detectados por usuarios y regresiones, mientras que la Defect Recurrence Rate operacionaliza específicamente la recurrencia mediante el conteo de issues reabiertos en GitHub. La correspondencia es la más cercana disponible en el catálogo canónico para el concepto de error recurrente.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | No | Sí |
| **Persona** | No | No |
| **Producto** | Sí | Sí |

Ítem de encuesta asociado: **C7 – La tasa de errores recurrentes** (ID Consigna: 7).

La relación con el ítem es **directa**: la consigna mide exactamente la reincidencia de defectos, y la operacionalización propuesta (ratio de issues reabiertos) captura este fenómeno de forma observable en GitHub.

---

## 3. Fórmula de cálculo

$$\text{Defect Recurrence Rate} = \frac{\text{reopened\_issues}}{\text{total\_closed\_issues}} \times 100$$

Donde:
- **reopened\_issues**: issues que fueron cerrados y posteriormente reabiertos al menos una vez (estado actual puede ser open o closed).
- **total\_closed\_issues**: total de issues que han sido cerrados al menos una vez en el historial del repositorio.

El resultado es un **porcentaje** ∈ [0, 100].

> **Decisión metodológica:** Un issue reabierto en GitHub es el proxy más directo de un defecto recurrente: indica que la corrección aplicada no fue suficiente y el problema volvió a manifestarse. Se excluyen pull requests del conteo. Los issues reabiertos por razones administrativas (e.g., reapertura accidental) representan un sesgo menor aceptable dada la dificultad de distinguirlos automáticamente.

### Variante alternativa

Si se dispone de etiquetas (`labels`) en el repositorio, puede refinarse como:

$$\text{Defect Recurrence Rate}_{bug} = \frac{\text{reopened\_issues con label bug}}{\text{total\_closed\_issues con label bug}} \times 100$$

Esta variante es más precisa pero depende de que el repositorio use labels de forma consistente.

### Implementación Python

Sigue el mismo patrón que `WorkflowEfficiency` y `NumberOfOpenIssues`: clase que extiende `Metrica`, recibe `GitHubExtractor` en el constructor y expone `calcular(owner, repo)`. Requiere:

1. **REST paginado** — `GET /repos/{owner}/{repo}/issues?state=closed` → lista de issues cerrados con sus eventos.
2. **REST paginado** — `GET /repos/{owner}/{repo}/issues/{issue_number}/events` → detectar eventos de tipo `reopened` por issue.

> **Alternativa recomendada:** GraphQL permite obtener issues con sus eventos de estado en una sola query, reduciendo el número de llamadas necesarias.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `total_closed_issues` | Total de issues cerrados al menos una vez | entero ≥ 0 | REST `GET /repos/{owner}/{repo}/issues?state=closed` → `total_count` |
| `reopened_issues` | Issues que tienen al menos un evento `reopened` en su historial | entero ≥ 0 | REST `GET /repos/{owner}/{repo}/issues/{n}/events` filtrando `event == "reopened"` |
| `defect_recurrence_rate` | Ratio de issues reabiertos sobre total cerrados | % ∈ [0, 100] | Calculado |

---

## 5. Fuente de datos

Esta métrica usa exclusivamente la **API de GitHub**, sin necesidad del historial local de commits. Utiliza `GitHubExtractor` igual que `WorkflowEfficiency` y `NumberOfOpenIssues`.

| Llamada | Método en `GitHubExtractor` | Dato obtenido |
|---------|-----------------------------|---------------|
| REST paginado issues cerrados | `extractor.get_paginated(endpoint)` | `total_closed_issues` |
| REST eventos por issue | `extractor.get_paginated(endpoint)` por issue | eventos `reopened` |

> **Advertencia de performance:** Este cálculo requiere consultar los eventos de cada issue cerrado individualmente, lo que puede resultar en un número elevado de llamadas a la API para repositorios con muchos issues. Se recomienda implementar caché y paginación eficiente.

---

## 6. Calculabilidad en tldr-pages/tldr

**Sí, calculable.**

GitHub registra el evento `reopened` en el historial de eventos de cada issue, y este dato es accesible via API para repositorios públicos. tldr-pages/tldr tiene issues habilitados con historial de actividad. El cálculo es técnicamente posible, aunque requiere múltiples llamadas a la API dada la cantidad de issues cerrados históricos del repositorio.

> **Consideración:** En un repositorio de documentación como tldr-pages, los issues reabiertos suelen corresponder a páginas que fueron marcadas como completadas pero luego requirieron corrección o actualización. La tasa esperada es baja, dado el modelo de contribución simple (agregar o corregir páginas Markdown).

---

## 7. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | Sobre todos los issues cerrados desde la creación del repositorio. **Recomendada como valor primario.** |
| **Anual** | Filtrar issues cerrados por año para observar evolución de la tasa de recurrencia. |
| **Por release** | Issues cerrados entre dos tags consecutivos. |

---

## 8. Rangos de interpretación

No existen umbrales formales en la literatura para esta métrica sobre repositorios GitHub. Los siguientes rangos son orientativos:

| Rango | Interpretación |
|-------|---------------|
| **0% – 2%** | Tasa de recurrencia muy baja. Las correcciones aplicadas son estables y efectivas. |
| **3% – 10%** | Tasa de recurrencia baja-moderada. Algunos defectos requieren múltiples iteraciones para resolverse. Normal en proyectos activos. |
| **11% – 25%** | Tasa de recurrencia moderada-alta. Puede indicar correcciones incompletas o regresiones frecuentes. |
| **> 25%** | Tasa de recurrencia alta. Señal de inestabilidad en las correcciones o falta de tests de regresión. |

Colakoglu et al. (2021) señalan que la confiabilidad del software — de la que Customer-Found Defects and Regressions es un indicador — es la segunda característica de calidad más medida en la literatura de métricas de producto, lo que confirma la relevancia de esta métrica.

---

## 9. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, API_BASE
from core.github_extractor import GitHubExtractor
from metrics.defect_recurrence_rate.defect_recurrence_rate import DefectRecurrenceRate

extractor = GitHubExtractor(token=GITHUB_TOKEN, api_base=API_BASE)
metrica = DefectRecurrenceRate(extractor)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")
```

Salida esperada (valores orientativos para tldr-pages/tldr):

```python
{
    "total_closed_issues": 8432,
    "reopened_issues": 127,
    "defect_recurrence_rate": 1.51
}
```

$$\text{Defect Recurrence Rate} = \frac{127}{8432} \times 100 \approx 1.51\%$$

Una tasa de ~1.5% es esperable para tldr-pages/tldr dado su modelo de contribución basado en documentación Markdown, donde las correcciones son simples y las regresiones poco frecuentes.

---

## 10. Relación con el ítem de encuesta

> **C7 – La tasa de errores recurrentes**

La relación es **directa**: el ratio de issues reabiertos sobre issues cerrados es la operacionalización más precisa del concepto de error recurrente disponible en GitHub. Un issue reabierto indica explícitamente que el problema no quedó resuelto y tuvo que ser retomado.

---

## 11. Observaciones metodológicas

- La métrica es un **proxy** de la recurrencia real de defectos: un issue reabierto no siempre implica que el defecto original reapareció (puede reabrirse por razones administrativas), y un defecto recurrente puede reportarse como un issue nuevo en lugar de reabrirse el original.
- En tldr-pages, la distinción entre "defecto" y "mejora" es difusa — muchos issues son solicitudes de nuevas páginas, no bugs técnicos. Esto puede inflar el denominador y subestimar la tasa real de recurrencia de defectos propiamente dichos.
- **Pendiente de validación:** evaluar si conviene filtrar por label `bug` o equivalente en el repositorio para una medición más precisa. Requiere verificar qué labels usa tldr-pages para clasificar sus issues.

---

## 12. Referencias

- Colakoglu, F. N., Yazici, A., & Mishra, A. (2021). Software Product Quality Metrics: A Systematic Mapping Study. *IEEE Access*, 9, 44647–44670. https://doi.org/10.1109/ACCESS.2021.3054730

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.