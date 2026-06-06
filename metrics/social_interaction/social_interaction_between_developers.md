# M19 – Social Interaction between Developers (Interacción Social entre Desarrolladores)

---

## 1. Descripción

La métrica **Social Interaction between Developers** cuantifica el nivel de interacción y comunicación entre los desarrolladores de un proyecto, medido a través de la cantidad de eventos de interacción explícita registrados en GitHub: comentarios en issues, comentarios en pull requests y revisiones de pull requests.

Su fundamento teórico proviene de Foucault et al. (2015), quienes estudian la movilidad de desarrolladores en proyectos open source y señalan que el turnover —entendido como el flujo continuo de entrada y salida de colaboradores— impacta en las interacciones sociales del equipo. En particular, el estudio cita a Dabbish et al. (2012) para sostener que el turnover puede "aumentar las interacciones sociales" dentro de la comunidad, y a Dess & Shaw (2001) para argumentar que las salidas de miembros disrumpen la red social y el entorno de quienes permanecen. Esta base teórica posiciona la interacción social como un atributo relevante de la dinámica colaborativa de un equipo de desarrollo.

> **Nota de correspondencia:** El paper de Foucault et al. (2015) no define formalmente una métrica denominada "Social Interaction between Developers". La métrica pertenece al catálogo ISL/JAIIO 2022 (orden 91), y este paper constituye la fuente bibliográfica de referencia más cercana según el mapeo realizado en la planilla de trazabilidad. La operacionalización propuesta aquí es propia, basada en los canales de interacción disponibles en GitHub y en la definición conceptual del catálogo ISL.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | No | Sí |
| **Persona** | Sí | Sí |
| **Producto** | No | No |

Ítem de encuesta asociado: **C9 – La frecuencia de participación en discusiones técnicas** (ID Consigna: 9).

La relación con el ítem es **relacionada** (no directa): la métrica mide interacciones sociales observables entre desarrolladores, que son el canal a través del cual se materializan las discusiones técnicas, aunque no distingue si el contenido de cada interacción es técnico o no.

---

## 3. Fórmula de cálculo

$$\text{Social Interaction} = \sum(\text{issue\_comments} + \text{pr\_comments} + \text{pr\_reviews})$$

Donde:
- **issue\_comments**: total de comentarios realizados en issues del repositorio.
- **pr\_comments**: total de comentarios realizados en pull requests (review comments + general comments).
- **pr\_reviews**: total de revisiones formales (aprobaciones, cambios solicitados, comentarios de revisión) sobre pull requests.

El resultado es un **conteo absoluto** de interacciones ∈ ℕ₀.

> **Decisión metodológica:** Se consideran estos tres canales porque son los mecanismos formales de comunicación entre desarrolladores registrados en GitHub y directamente extraíbles via API. Los commits sin comentarios no se contabilizan como interacción social. Las reacciones (👍, ❤️, etc.) tampoco se incluyen por ser interacciones pasivas.

### Variante por desarrollador

Para analizar la distribución de interacciones entre colaboradores:

$$\text{Social Interaction}_d = \text{comentarios\_totales}_{d} \quad \forall d \in \text{Developers}$$

Esta variante permite identificar qué desarrolladores concentran mayor actividad de interacción, complementando el análisis del valor global.

### Implementación Python

Sigue el mismo patrón que `WorkflowEfficiency` y `ForksIssuesPRs`: clase que extiende `Metrica`, recibe `GitHubExtractor` en el constructor y expone `calcular(owner, repo)`. Requiere múltiples llamadas a la GitHub REST API:

1. **REST** — `GET /repos/{owner}/{repo}` → campo `open_issues_count` (orientativo).
2. **REST paginado** — `GET /repos/{owner}/{repo}/issues/comments` → suma total de comentarios en issues.
3. **REST paginado** — `GET /repos/{owner}/{repo}/pulls/comments` → suma total de review comments en PRs.
4. **REST paginado** — `GET /repos/{owner}/{repo}/pulls/reviews` (por PR) → suma total de revisiones formales.

> **Alternativa recomendada:** Usar la **GraphQL API** de GitHub para obtener los tres conteos en una sola query, evitando la paginación múltiple y reduciendo el consumo de rate limit.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `issue_comments` | Total de comentarios en issues (abiertos + cerrados) | entero ≥ 0 | REST `GET /repos/{owner}/{repo}/issues/comments` |
| `pr_comments` | Total de comentarios en pull requests | entero ≥ 0 | REST `GET /repos/{owner}/{repo}/pulls/comments` |
| `pr_reviews` | Total de revisiones formales en pull requests | entero ≥ 0 | REST `GET /repos/{owner}/{repo}/pulls/{pull_number}/reviews` |
| `social_interaction_total` | Suma de los tres canales | entero ≥ 0 | Calculado |
| `interactions_per_developer` | Dict desarrollador → total de interacciones | entero ≥ 0 por dev | Calculado desde los tres canales filtrando por autor |

---

## 5. Fuente de datos

Esta métrica usa exclusivamente la **API de GitHub**, sin necesidad del historial local de commits. Utiliza `GitHubExtractor` igual que `WorkflowEfficiency` y `ForksIssuesPRs`.

| Llamada | Método en `GitHubExtractor` | Dato obtenido |
|---------|-----------------------------|---------------|
| GraphQL o REST paginado | `extractor.graphql(query, vars)` o `extractor.get_paginated(endpoint)` | `issue_comments` |
| GraphQL o REST paginado | `extractor.graphql(query, vars)` o `extractor.get_paginated(endpoint)` | `pr_comments` |
| REST por PR (paginado) | `extractor.get_paginated(endpoint)` | `pr_reviews` |

---

## 6. Calculabilidad en tldr-pages/tldr

**Parcialmente calculable.**

tldr-pages/tldr es un repositorio de documentación colaborativa con un workflow basado principalmente en pull requests. Los comentarios en PRs e issues son el canal principal de comunicación entre contributors y maintainers. Sin embargo:

- El repositorio tiene **alta rotación de contributors** (consistente con los patrones de turnover descritos por Foucault et al., 2015).
- Los issues son mayoritariamente reportes de comandos faltantes o errores de documentación, por lo que los comentarios pueden ser breves y de naturaleza no técnica.
- No existe un sistema de revisiones formales tan estructurado como en proyectos de software con código fuente complejo.

Esto implica que el valor calculado será **representativo de la actividad de interacción** del repositorio, aunque no discrimina si las interacciones son de naturaleza técnica profunda o administrativa.

---

## 7. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | Sin filtro de fecha. Suma histórica de todas las interacciones desde la creación del repositorio. **Recomendada como valor primario.** |
| **Anual** | Agregar filtro `since` / `until` a las queries para calcular interacciones por año calendario y observar evolución temporal. |
| **Por release** | Interacciones registradas entre dos tags consecutivos. |

Para tldr-pages/tldr se recomienda el valor global más una serie anual para capturar el crecimiento de la comunidad a lo largo del tiempo.

---

## 8. Rangos de interpretación

No existen umbrales formales en la literatura para esta métrica. Los siguientes rangos son orientativos:

| Rango | Interpretación |
|-------|---------------|
| **0 – 500** | Interacción muy baja. Repositorio con poca actividad colaborativa o comunicación informal fuera de GitHub. |
| **501 – 5.000** | Interacción moderada. Comunidad activa con comunicación regular entre contributors. |
| **5.001 – 50.000** | Interacción alta. Proyecto maduro con debate activo en issues y revisiones de PRs. |
| **> 50.000** | Interacción muy alta. Ecosistema con gran cantidad de contributors y comunicación intensa. Esperable en proyectos como tldr-pages dada su base de contributors distribuida globalmente. |

---

## 9. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, API_BASE
from core.github_extractor import GitHubExtractor
from metrics.social_interaction.social_interaction import SocialInteractionBetweenDevelopers

extractor = GitHubExtractor(token=GITHUB_TOKEN, api_base=API_BASE)
metrica = SocialInteractionBetweenDevelopers(extractor)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")
```

Salida esperada (valores orientativos para tldr-pages/tldr):

```python
{
    "issue_comments": 18432,
    "pr_comments": 31205,
    "pr_reviews": 9871,
    "social_interaction_total": 59508,
    "top_interactors": {
        "contributor_a": 3241,
        "contributor_b": 2108,
        "contributor_c": 1874,
        ...
    }
}
```

$$\text{Social Interaction} = 18432 + 31205 + 9871 = 59508 \text{ interacciones}$$

Un valor en el rango > 50.000 es esperable para tldr-pages/tldr dado su modelo de contribución distribuida con miles de contributors globales y un proceso de revisión activo de pull requests.

---

## 10. Relación con el ítem de encuesta

> **C9 – La frecuencia de participación en discusiones técnicas**

La relación es **relacionada** (proxy): la métrica mide interacciones registradas en los canales formales de GitHub (comentarios en issues y PRs, revisiones), que son los mecanismos a través de los cuales se materializan las discusiones técnicas. Sin embargo, no distingue si el contenido de cada interacción es técnico o administrativo, ni mide frecuencia individual de participación de forma directa.

Para aproximarse mejor a "frecuencia de participación", se recomienda complementar con la variante por desarrollador (`interactions_per_developer`) y calcular métricas estadísticas sobre esa distribución (media, mediana, percentiles).

---

## 11. Observaciones metodológicas

- La métrica es un **proxy** de la interacción social real: captura únicamente las interacciones registradas en GitHub y no contempla comunicación fuera de la plataforma (Slack, Discord, listas de correo, etc.), lo cual es una limitación reconocida por Foucault et al. (2015) en sus amenazas a la validez interna.
- El paper de referencia (Foucault et al., 2015) no define formalmente esta métrica sino que la aborda como fenómeno teórico. La operacionalización propuesta es propia y debe ser validada con Esteban antes de su cálculo definitivo.
- **Pendiente de validación:** definir si se incluyen o no los bots (e.g., `github-actions[bot]`, `dependabot`) en el conteo de interacciones. Se recomienda excluirlos para medir únicamente interacciones humanas.

---

## 12. Referencias

- Foucault, M., Palyart, M., Blanc, X., Murphy, G. C., & Falleri, J. R. (2015). Impact of developer turnover on quality in open-source software. *Proceedings of the 2015 10th Joint Meeting on Foundations of Software Engineering (ESEC/FSE 2015)*, 829–841. ACM. https://doi.org/10.1145/2786805.2786870

- Dabbish, L., Farzan, R., Kraut, R., & Postmes, T. (2012). Fresh faces in the crowd: Turnover, identity, and commitment in online groups. *Proceedings of the ACM 2012 Conference on Computer Supported Cooperative Work (CSCW '12)*, 245–248. ACM. [Citado en Foucault et al., 2015]

- Dess, G. G., & Shaw, J. D. (2001). Voluntary turnover, social capital, and organizational performance. *Academy of Management Review*, 26(3), 446–456. [Citado en Foucault et al., 2015]

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.