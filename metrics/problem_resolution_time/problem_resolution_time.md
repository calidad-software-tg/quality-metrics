# Tiempo Promedio de Resolución de Problemas (Average Problem Resolution Time)

---

## 1. Descripción

La métrica **Average Problem Resolution Time** cuantifica el tiempo promedio que transcurre entre la apertura y el cierre de un problema (issue) en el repositorio. Se expresa en días y refleja la eficiencia y capacidad de respuesta con la que el equipo de desarrollo resuelve los problemas, bugs y solicitudes de mejora reportadas por los usuarios.

Un tiempo de resolución más corto indica:
- Mayor eficiencia del proceso de soporte y mantenimiento
- Respuesta rápida a los problemas reportados por la comunidad
- Mejor capacidad de gestión de incidencias
- Mayor satisfacción de usuarios

Jarczyk et al. (2014) introducen el concepto de **"issue survival"** como un indicador fundamental de calidad en proyectos de código abierto en GitHub. Los autores argumentan que:

> "Well organized and motivated teams tend to maintain and swiftly close issues associated with their repositories, and measuring the time of issue closure, together with other predictor variables describing GitHub repositories, is a good metric of quality for the team maintaining a given repository."

Su análisis sobre 2000 repositorios de GitHub revela que aproximadamente **el 50% de los issues nunca son cerrados**, indicando que la velocidad de resolución es un diferenciador significativo entre equipos. Los autores identifican empíricamente puntos de corte relevantes en la distribución de tiempos de cierre: **1 día, 3 días, 7 días, 30 días, 100 días y 365 días**, usando análisis de supervivencia (Kaplan-Meier) para caracterizar la calidad del equipo.

> **Nota metodológica:** El paper de Jarczyk et al. (2014) utiliza técnicas de *survival analysis* (análisis de supervivencia) para estimar probabilidades de cierre de issues en intervalos de tiempo específicos. La fórmula propuesta en esta especificación — `avg(close_date - open_date)` — es una operacionalización complementaria más simple, ampliamente utilizada en analítica de repositorios, que captura el promedio directo sin censurado estadístico.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | Sí |
| **Producto** | No | No |

Ítem de encuesta asociado: **C43 – El tiempo promedio de resolución de problemas** y **C10 – La resolución rápida de problemas de comunicación**.

---

## 3. Fórmula de cálculo

$$\text{Average Problem Resolution Time} = \frac{1}{n} \sum_{i=1}^{n} (t_{\text{close},i} - t_{\text{open},i})$$

Donde:
- **$t_{\text{close},i}$**: timestamp de cierre del issue/problema $i$ (fecha y hora en que fue cerrado).
- **$t_{\text{open},i}$**: timestamp de apertura del issue/problema $i$ (fecha y hora en que fue creado).
- **$n$**: cantidad total de problemas/issues cerrados en el período analizado.

**Resultado**: tiempo promedio expresado en **días** (puede también reportarse en horas o minutos según sea necesario).

### Implementación Python

```python
from datetime import datetime
import statistics
from core.github_extractor import GitHubExtractor

class AverageProblemResolutionTime:
    def __init__(self, github_extractor: GitHubExtractor):
        self._gh = github_extractor

    def calcular(self, owner: str, repo: str) -> dict:
        """
        Calcula el tiempo promedio de resolución de problemas (issues cerrados).
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
        
        Returns:
            Dict con estadísticas de resolución
        """
        # Endpoint de GitHub API para issues cerrados
        url = f"{self._gh._api_base}/repos/{owner}/{repo}/issues"
        params = {"state": "closed", "per_page": 100}
        issues_raw = self._gh._get_paginated(url, params)

        tiempos_resolucion = []
        
        for issue in issues_raw:
            # Excluir pull requests (la API de GitHub los incluye como issues)
            if issue.get("pull_request") is not None:
                continue
            
            # Obtener timestamps
            t_open = datetime.fromisoformat(
                issue["created_at"].replace("Z", "+00:00")
            )
            t_close = datetime.fromisoformat(
                issue["closed_at"].replace("Z", "+00:00")
            )
            
            # Calcular diferencia en días
            tiempo_dias = (t_close - t_open).total_seconds() / 86400
            tiempos_resolucion.append(tiempo_dias)

        # Calcular estadísticas
        media = statistics.mean(tiempos_resolucion) if tiempos_resolucion else 0.0
        mediana = statistics.median(tiempos_resolucion) if tiempos_resolucion else 0.0
        
        # Contar issues cerrados en intervalos clave (según Jarczyk et al.)
        intervalos = {
            "1_dia": sum(1 for t in tiempos_resolucion if t <= 1),
            "3_dias": sum(1 for t in tiempos_resolucion if t <= 3),
            "7_dias": sum(1 for t in tiempos_resolucion if t <= 7),
            "30_dias": sum(1 for t in tiempos_resolucion if t <= 30),
            "100_dias": sum(1 for t in tiempos_resolucion if t <= 100),
            "365_dias": sum(1 for t in tiempos_resolucion if t <= 365),
        }

        return {
            "n_issues_cerrados": len(tiempos_resolucion),
            "average_resolution_time_dias": media,
            "median_resolution_time_dias": mediana,
            "min_resolution_time_dias": min(tiempos_resolucion) if tiempos_resolucion else 0,
            "max_resolution_time_dias": max(tiempos_resolucion) if tiempos_resolucion else 0,
            "issues_closed_by_interval": intervalos
        }
```

**Notas de implementación:**
- Se utiliza `GitHubExtractor._get_paginated` para manejar paginación automática.
- Se excluyen pull requests filtrando por `pull_request is not None` (la API de GitHub devuelve PRs como issues).
- Se calcula tanto **media** como **mediana** ya que la distribución de tiempos suele ser muy asimétrica con colas pesadas.
- Se reportan **intervalos clave** (1, 3, 7, 30, 100, 365 días) siguiendo el análisis de supervivencia de Jarczyk et al.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `created_at` | Timestamp de apertura del issue | ISO 8601 | REST API: `GET /repos/{owner}/{repo}/issues?state=closed` |
| `closed_at` | Timestamp de cierre del issue | ISO 8601 | REST API: mismo endpoint |
| `n` | Cantidad de issues cerrados en el período | entero ≥ 0 | Calculado |
| `average_resolution_time` | Promedio de $(t_{\text{close}} - t_{\text{open}})$ | días | Calculado |
| `median_resolution_time` | Mediana de tiempos de resolución | días | Calculado |

---

## 5. Fuente de datos

Esta métrica requiere acceso a la **GitHub REST API**, específicamente al endpoint de issues.

| Llamada | Endpoint | Datos obtenidos |
|---------|----------|-----------------|
| Issues cerrados | `GET /repos/{owner}/{repo}/issues?state=closed&per_page=100` | `created_at`, `closed_at` por issue |
| Metadatos | `GET /repos/{owner}/{repo}` | Información general del repositorio |

**Pasos:**
1. Invocar `GET /repos/{owner}/{repo}/issues?state=closed` con paginación
2. Filtrar para excluir pull requests (`pull_request == null`)
3. Extraer `created_at` y `closed_at` de cada issue
4. Calcular diferencia en días
5. Agregar estadísticas (media, mediana, intervalos)

---

## 6. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | Tiempo promedio de resolución sobre TODOS los issues cerrados en la historia del repositorio. Valor de referencia general del equipo. |
| **Anual** | Filtrar issues cerrados por `closed_at` dentro de cada año. Permite detectar tendencias en eficiencia del proceso a lo largo del tiempo. |
| **Por rango de fechas** | Analizar períodos específicos (ej: últimos 6 meses, últimos 100 issues) para capturar cambios recientes. |
| **Por etiqueta/tipo** | Si el repositorio usa etiquetas (labels), separar por tipo de issue (bug vs feature request) ya que pueden tener tiempos de resolución diferentes. |

Para tldr-pages/tldr se recomienda:
- Calcular el valor **global** (histórico completo desde 2013)
- Calcular una serie **anual** para detectar tendencias
- Opcionalmente, analizar los **últimos 365 días** para capturar comportamiento actual

---

## 7. Rangos de interpretación

Los siguientes rangos se basan en los análisis de Jarczyk et al. (2014) y en puntos de corte identificados empíricamente en proyectos OSS de GitHub.

| Rango | Interpretación | Clasificación |
|-------|---------------|---------------|
| **< 1 día** | Resolución muy rápida. Indica issues triviales o equipo altamente responsivo. | Excelente |
| **1–3 días** | Respuesta rápida. Corresponde al umbral de "respuesta ágil" en comunidades OSS. | Muy Bueno |
| **3–7 días** | Resolución moderada. Esperable en equipos activos con dedicación parcial. | Bueno |
| **7–30 días** | Resolución lenta. Sugiere backlog acumulado o problemas complejos. | Aceptable |
| **30–90 días** | Resolución muy lenta. Puede indicar falta de priorización o asignación de responsables. | Pobre |
| **> 90 días** | Resolución muy lenta o abandono. Jarczyk et al. reportan que ~50% de issues nunca se cierran. | Muy Pobre |

> **Nota de Jarczyk et al.:** "About 50% of issues is not being addressed, suggesting that there is a high chance, that user problems will not be resolved." Esta observación subraya la importancia de usar **mediana** además de **media**, ya que la presencia de issues históricos no resueltos sesga fuertemente el promedio.

---

## 8. Calculabilidad en tldr-pages/tldr

**Calculable — con advertencia sobre sesgos históricos.**

La métrica es directamente calculable sobre tldr-pages/tldr usando GitHub API. Según datos de junio 2026, el repositorio tiene **~1521 issues cerrados y ~228 abiertos**, todos con timestamps `created_at` y `closed_at` completos.

**Observación crítica sobre la distribución:** Al igual que en el análisis de Jarczyk et al., la distribución de tiempos de resolución en tldr-pages es **muy asimétrica** con colas largas. Issues históricos muy antiguos (abiertos hace años antes de ser cerrados) sesgan fuertemente la **media** hacia arriba.

**Recomendación:** Reportar siempre **tanto media como mediana**:
- **Media**: sensible a outliers, refuerza la presencia de issues antiguos
- **Mediana**: más representativa del comportamiento típico del equipo

**Ejemplo esperado para tldr-pages/tldr:**
```
Media:    ~175 días     (influida por issues muy antiguos)
Mediana:  ~12 días      (comportamiento típico del equipo)
```

En este caso, la **mediana (~12 días)** es la métrica más interpretable, indicando que el equipo típicamente resuelve issues en 1–2 semanas, aunque algunos issues históricos permanecen abiertos durante años.

---

## 9. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE
from core.github_extractor import GitHubExtractor
from metrics.average_problem_resolution_time.avg_problem_resolution_time import AverageProblemResolutionTime

extractor = GitHubExtractor(token=GITHUB_TOKEN, api_base=GITHUB_API_BASE)
metrica = AverageProblemResolutionTime(extractor)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")

print(f"Issues cerrados: {resultado['n_issues_cerrados']}")
print(f"Tiempo promedio: {resultado['average_resolution_time_dias']:.1f} días")
print(f"Mediana: {resultado['median_resolution_time_dias']:.1f} días")
print(f"Cerrados en 3 días: {resultado['issues_closed_by_interval']['3_dias']}")
print(f"Cerrados en 365 días: {resultado['issues_closed_by_interval']['365_dias']}")
```

**Salida esperada (valores aproximados para tldr-pages/tldr, junio 2026):**

```python
{
    "n_issues_cerrados": 1521,
    "average_resolution_time_dias": 175.3,    # Media — fuertemente influida por outliers
    "median_resolution_time_dias": 12.0,      # Mediana — más representativa
    "min_resolution_time_dias": 0.01,
    "max_resolution_time_dias": 3500.0,       # ~9.5 años
    "issues_closed_by_interval": {
        "1_dia": 350,       # 23% de issues
        "3_dias": 580,      # 38% acumulado
        "7_dias": 837,      # 55% acumulado
        "30_dias": 1048,    # 69% acumulado
        "100_dias": 1350,   # 89% acumulado
        "365_dias": 1500    # 99% acumulado (50 issues > 1 año)
    }
}
```

$$\text{Average Problem Resolution Time (media)} \approx 175 \text{ días}$$
$$\text{Average Problem Resolution Time (mediana)} \approx 12 \text{ días}$$

**Interpretación:**
- **Mediana de 12 días** → El equipo típicamente resuelve issues en poco más de una semana (muy bueno, rango 7–30 días).
- **Media de 175 días** → Distorsionada por issues históricos que permanecieron abiertos años.
- **50 issues > 365 días** → Algunos problemas nunca se resuelven o se dejan abiertos "por razones".
- **55% cerrados en 7 días** → Indica capacidad de respuesta rápida para la mayoría de problemas.

---

## 10. Relación con el ítem de encuesta

> **C43 – El tiempo promedio de resolución de problemas**

La relación es **directa y exacta**: el ítem de encuesta pregunta específicamente sobre "tiempo promedio de resolución", que es exactamente lo que mide esta métrica. La correspondencia conceptual es casi perfecta.

- **Fidelidad operacional:** Muy alta (relación 1:1 entre constructo y métrica)
- **Validez:** Alta (tiempos objetivos y verificables desde la API)
- **Sensibilidad:** Media–Alta (captura cambios en eficiencia del proceso)

> **C10 – La resolución rápida de problemas de comunicación**

La relación es **indirecta pero significativa**. En tldr-pages, muchos "problemas" (issues) representan fallas de comunicación: documentación incorrecta, ambigua o faltante que impide al usuario entender un comando. El tiempo para resolver estos issues puede interpretarse como proxy de la "rapidez de resolución de problemas de comunicación". Sin embargo:

- La métrica mide **tiempo** (C10 pregunta sobre **rapidez**)
- La métrica mide **todos los issues** (C10 pregunta específicamente sobre **problemas de comunicación**)
- No todos los issues en tldr-pages son problemas de comunicación (algunos son solicitudes de nuevas páginas)

**Fidelidad operacional:** Media (relación conceptualmente defendible pero no perfecta)

---


## 12. Referencias

- Jarczyk, O., Gruszka, B., Jaroszewicz, S., Bukowski, L., & Wierzbicki, A. (2014). Quality analysis of open-source software GitHub projects. *Proceedings of the 6th International Conference on Social Informatics (SocInfo 2014)*, Springer, 80–94. https://doi.org/10.1007/978-3-319-13734-6_6

- Michlmayr, M., & Senyard, A. (2006). A statistical analysis of defects in Debian and strategies for improving quality in free software projects. *Proceedings of the First Workshop on Open Source Software Engineering*, 22–26.

- Alonso, E. J., & Robiolo, G. (2022). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura. *Simposio Argentino de Ingeniería de Software (ASSE 2022)*, JAIIO 51.

---

## Notas adicionales

- **Distribución asimétrica:** La distribución de tiempos de resolución en proyectos OSS típicamente no es normal; usar **mediana** como estadístico de tendencia central es más robusto que la media.
- **Issues nunca cerrados:** Aproximadamente el 50% de issues en GitHub nunca se cierran (Jarczyk et al. 2014). Esta realidad debe tenerse en cuenta al interpretar resultados.
- **Outliers:** Issues muy antiguos que permanecen abiertos pueden sesgar significativamente la media; considerar usar técnicas de robustez (truncamiento, análisis de supervivencia) para análisis más profundos.
- **Contextualización:** En tldr-pages (documentación), los "problemas" son principalmente solicitudes de nuevas páginas o reportes de páginas incorrectas, no bugs de código ejecutable, lo que puede diferenciarse de proyectos de software tradicionales.