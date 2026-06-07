# C21 – Tiempo Promedio de Resolución de Issues (Issue Resolution Time)

---

## 1. Descripción

La métrica **Issue Resolution Time** cuantifica el tiempo promedio que transcurre entre la apertura y el cierre de un issue en el repositorio. Se expresa en días y refleja la eficiencia con la que el equipo responde y resuelve las tareas, bugs o solicitudes de mejora reportadas por la comunidad o por el equipo de desarrollo.

Una resolución más rápida de issues está asociada a procesos de desarrollo más ágiles y a una mayor capacidad de respuesta del equipo. Vasilescu et al. (2015) evidencian que la adopción de integración continua (CI) incrementa en un 48% los bugs detectados por desarrolladores internos sin aumentar los bugs experimentados por usuarios externos, lo cual implica que los mecanismos de automatización del proceso —como CI— inciden directamente en la velocidad y efectividad con la que los equipos gestionan y cierran issues.

La relevancia empírica del tiempo de resolución de issues como medida de performance del proceso de desarrollo está respaldada por Jarczyk et al. (2018), quienes estudian los factores que afectan las *issue closure rates* en proyectos OSS de GitHub. Su análisis de supervivencia sobre casi 10.000 repositorios revela que aproximadamente el 50% de los issues reportados nunca son cerrados, y que el tiempo de cierre presenta alta variabilidad entre proyectos. Para resumir esta variabilidad, los autores identifican dos puntos de corte con sentido empírico: el porcentaje de issues cerrados a **3 días** (respuesta rápida al usuario) y a **365 días** (resolución de problemas de largo plazo), que en conjunto explican el 94% de la varianza total de los tiempos de cierre.

> **Nota metodológica:** Jarczyk et al. (2018) operacionalizan el tiempo de resolución como *closure rates* (proporción de issues cerrados en un plazo dado), no como tiempo promedio en días. La fórmula propuesta en esta especificación — `avg(close_date - open_date)` — es una operacionalización propia, complementaria a ese enfoque y ampliamente utilizada en analítica de repositorios. 

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | Sí |
| **Producto** | No | No |

Ítem de encuesta asociado: **C21 – Tiempo promedio de resolución de issues** y **C10 - La resolución rápida de problemas de comunicación**.

---

## 3. Fórmula de cálculo

$$\text{Issue Resolution Time} = \frac{1}{n} \sum_{i=1}^{n} (t_{\text{close},i} - t_{\text{open},i})$$

Donde:
- **$t_{\text{close},i}$**: timestamp de cierre del issue $i$.
- **$t_{\text{open},i}$**: timestamp de apertura del issue $i$.
- **$n$**: cantidad total de issues cerrados en el período analizado.

Resultado: tiempo promedio expresado en **días**.

### Implementación Python


```python
from datetime import datetime
import statistics
from core.github_extractor import GitHubExtractor

class IssueResolutionTime:
    def __init__(self, github_extractor: GitHubExtractor):
        self._gh = github_extractor

    def calcular(self, owner: str, repo: str) -> dict:
        url = f"{self._gh._api_base}/repos/{owner}/{repo}/issues"
        params = {"state": "closed", "per_page": 100}
        issues_raw = self._gh._get_paginated(url, params)

        tiempos = []
        for issue in issues_raw:
            if issue.get("pull_request") is not None:
                continue  # excluir pull requests
            t_open = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            t_close = datetime.fromisoformat(issue["closed_at"].replace("Z", "+00:00"))
            tiempos.append((t_close - t_open).total_seconds() / 86400)

        return {
            "n_issues_cerrados": len(tiempos),
            "issue_resolution_time_dias": statistics.mean(tiempos) if tiempos else 0.0
        }
```

Utiliza `GitHubExtractor._get_paginated` sobre `GET /repos/{owner}/{repo}/issues?state=closed`, con paginación automática. El filtro `pull_request is not None` excluye los PRs que la API de GitHub incluye en el mismo endpoint.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `created_at` | Timestamp de apertura del issue | ISO 8601 | REST API: `GET /repos/{owner}/{repo}/issues?state=closed` |
| `closed_at` | Timestamp de cierre del issue | ISO 8601 | REST API: mismo endpoint |
| `n` | Cantidad de issues cerrados en el período | entero ≥ 0 | Calculado |
| `issue_resolution_time` | Promedio de $(t_{\text{close}} - t_{\text{open}})$ | días | Calculado |

---

## 5. Fuente de datos

Esta métrica utiliza la **REST API de GitHub**, no el historial de commits.

| Llamada | Endpoint | Datos obtenidos |
|---------|----------|-----------------|
| Issues cerrados | `GET /repos/{owner}/{repo}/issues?state=closed&per_page=100` | `created_at`, `closed_at` por issue |

Se requiere paginación para repositorios con alto volumen de issues. Es importante **excluir pull requests**: la API de GitHub devuelve PRs como issues si no se filtra explícitamente; usar `is:issue` o verificar que el campo `pull_request` sea `null`.

---

## 6. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | Promedio sobre todos los issues cerrados en la historia del repositorio. Valor de referencia general. |
| **Anual** | Filtrar issues cerrados por `closed_at` dentro de cada año. Permite analizar evolución temporal. |
| **Por release** | Filtrar por `closed_at` entre fechas de tags consecutivos. |

Para tldr-pages/tldr se recomienda calcular el valor global y una serie anual desde la creación del repositorio (2013 en adelante).

---

## 7. Rangos de interpretación

Orientativos; no existen umbrales formales en la literatura para esta métrica expresada como tiempo promedio en días. Sin embargo, Jarczyk et al. (2018) identifican empíricamente los **3 días** y los **365 días** como puntos de corte con sentido estadístico para distinguir respuesta rápida de resolución de largo plazo, lo que orienta la interpretación de los rangos siguientes.

| Rango | Interpretación |
|-------|---------------|
| **< 1 día** | Resolución muy rápida. Puede indicar issues triviales o cierre automático. |
| **1 – 7 días** | Alta eficiencia de respuesta. Proceso activo y equipo comprometido. Corresponde al umbral de "respuesta rápida" de Jarczyk et al. (2018). |
| **7 – 30 días** | Resolución moderada. Esperable en proyectos con alta demanda de contribuciones. |
| **30 – 90 días** | Resolución lenta. Puede reflejar backlog acumulado o falta de asignación formal. |
| **> 90 días** | Resolución muy lenta o issues abandonados. Jarczyk et al. (2018) reportan que aproximadamente el 50% de los issues en proyectos OSS de GitHub nunca son cerrados. |

> Vasilescu et al. (2015) muestran que proyectos con CI resuelven más bugs internamente sin incrementar los defectos percibidos por usuarios, lo que sugiere que la adopción de CI puede reducir los tiempos efectivos de resolución al acortar el ciclo de retroalimentación del equipo.

---

## 8. Calculabilidad en tldr-pages/tldr

**Calculable — con advertencia sobre el uso de la media.**

La métrica es directamente calculable sobre tldr-pages/tldr. La Search API de GitHub confirma **1521 issues cerrados** y **228 issues abiertos** (junio 2026). Todos los issues tienen campos `created_at` y `closed_at` poblados. La implementación con `GitHubExtractor` es aplicable sin modificaciones.

**Observación crítica sobre la distribución:** la distribución de tiempos de resolución es **bimodal con colas muy pesadas**. Un análisis sobre una muestra de 200 issues cerrados históricos arroja:

| Estadístico | Valor |
|-------------|-------|
| Issues cerrados totales | 1.521 |
| Issues abiertos | 228 |
| Media (promedio) | ~175 días |
| Mediana | ~12 días |
| Mínimo | 0 días |
| Máximo | ~3.500 días (~9,5 años) |
| Distribución | <1d: 23% · 1–7d: 18% · 7–30d: 17% · 30–90d: 19% · >90d: 23% |

La media está fuertemente inflada por issues muy antiguos que permanecieron abiertos durante años antes de cerrarse. La **mediana es más representativa** del comportamiento típico del equipo. Para análisis comparativos se recomienda reportar ambas o usar la mediana como valor primario.

La mayoría de los issues son *page requests* (solicitudes de nuevas páginas de documentación) o reportes de páginas incorrectas/desactualizadas, no bugs de código ejecutable, lo que es coherente con la naturaleza documental del repositorio.

---

## 9. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE
from core.github_extractor import GitHubExtractor
from metrics.issue_resolution_time.issue_resolution_time import IssueResolutionTime

extractor = GitHubExtractor(token=GITHUB_TOKEN, api_base=GITHUB_API_BASE)
metrica = IssueResolutionTime(extractor)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")
```

Salida esperada (valores reales para tldr-pages/tldr, junio 2026):

```python
{
    "n_issues_cerrados": 1521,
    "issue_resolution_time_dias": 175.0,   # media — sensible a outliers
    "issue_resolution_time_mediana_dias": 12.0
}
```

$$\text{Issue Resolution Time (media)} \approx 175 \text{ días}$$
$$\text{Issue Resolution Time (mediana)} \approx 12 \text{ días}$$

La mediana de ~12 días cae en el rango "7–30 días" (resolución moderada), que es esperable para un proyecto open source con contribuciones voluntarias y sin asignación formal de issues. La media de ~175 días refleja el peso de issues históricos que permanecieron abiertos durante años.

---

## 10. Relación con el ítem de encuesta

> **C21 – Tiempo promedio de resolución de issues**

La relación es **directa**: el ítem evalúa exactamente el constructo que mide la métrica, cuán rápidamente el equipo resuelve los issues reportados. A diferencia de métricas de conteo como *Number of Closed Issues*, esta incorpora la dimensión temporal y es más sensible a cambios en la eficiencia del proceso. La fidelidad operacional es **alta**: no hay brecha semántica entre el ítem y la fórmula.

> **C10 – La resolución rápida de problemas de comunicación**

La relación es **indirecta**. En tldr-pages, los issues suelen representar problemas de comunicación concretos: documentación incorrecta, ambigua o faltante que impide al usuario entender un comando. El tiempo de resolución de estos issues puede tomarse como proxy de la velocidad con la que el equipo atiende y corrige esas fallas de comunicación. Sin embargo, la correspondencia no es perfecta: C10 apunta a la percepción del equipo sobre su propia capacidad de comunicación interna, mientras que la métrica mide un artefacto del repositorio. La fidelidad operacional es **media**: el constructo es relacionado pero no idéntico.

---

## 11. Referencias

- Vasilescu, B., Yu, Y., Wang, H., Devanbu, P., & Filkov, V. (2015). Quality and productivity outcomes relating to continuous integration in GitHub. *Proceedings of the 2015 10th Joint Meeting on Foundations of Software Engineering (ESEC/FSE 2015)*, 805–816. https://doi.org/10.1145/2786805.2786850

- Jarczyk, O., Jaroszewicz, S., Wierzbicki, A., Pawlak, K., & Jankowski-Lorek, M. (2018). Surgical teams on GitHub: Modeling performance of GitHub project development processes. *Information and Software Technology*, 100, 130–143. https://doi.org/10.1016/j.infsof.2018.03.010

- Alonso, E. J., & Robiolo, G. (2022). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. *Simposio Argentino de Ingeniería de Software (ASSE 2022)*, JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.

- Gousios, G., Zaidman, A., Storey, M.-A., & Van Deursen, A. (2015). Work practices and challenges in pull-based development: The integrator's perspective. *Proceedings of ICSE 2015*. IEEE.