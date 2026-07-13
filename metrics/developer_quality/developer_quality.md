# M14 – Developer Quality (Calidad del Desarrollador)

---

## 1. Descripción

La métrica **Developer Quality** cuantifica la calidad de un desarrollador a partir de su historial de contribuciones, midiendo la proporción de commits "limpios" (que no introdujeron bugs) sobre el total de commits realizados por ese desarrollador durante el proceso de desarrollo.

Su fundamento empírico proviene de Wu et al. (2014), quienes definieron esta métrica como base para construir ocho métricas de calidad de archivo (*file quality metrics*) y encontraron que, usadas junto con las métricas de proceso tradicionales, mejoran significativamente el rendimiento de los modelos de predicción de *fault-proneness* en siete de los ocho sistemas open-source estudiados.

El razonamiento detrás es que los desarrolladores difieren ampliamente en su capacidad de escribir código libre de fallos, por lo que la proporción histórica de *bug-introduce commits* de un desarrollador es un buen indicador de su probabilidad futura de introducir defectos. Esta calidad, una vez calculada por desarrollador, se propaga a nivel de archivo combinando la calidad de todos sus *actual authors* (autores con líneas de código vigentes en el archivo, identificados vía `git blame`).

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | No | No |
| **Persona** | Sí | Sí |
| **Producto** | No | No |

---

## 3. Fórmula de cálculo

$$Q(d_j) = 1 - \frac{\displaystyle\sum_{i=1}^{n} B(b_i, d_j)}{\displaystyle\sum_{i=1}^{n} C(c_i, d_j)}$$

Donde:
- **k**: total de desarrolladores del sistema
- **n**: total de commits desde el inicio del sistema hasta la release de la versión actual
- **m**: total de bug-introduce commits ocurridos en ese período
- **C(c_i, d_j)**: 1 si el desarrollador *d_j* contribuyó al commit *c_i*, 0 en caso contrario
- **B(b_i, d_j)**: 1 si el desarrollador *d_j* contribuyó al bug-introduce commit *b_i*, 0 en caso contrario

El resultado es un valor ∈ [0, 1]:
- **Q → 1**: el desarrollador nunca introdujo bugs (calidad máxima)
- **Q → 0**: casi todos los commits del desarrollador introdujeron bugs (calidad mínima)

Esta es la fórmula exacta utilizada por Wu et al. (2014), sección II.B.

**Pasos previos requeridos** para identificar los *bug-introduce commits*:

1. Identificar *bug-fix commits* vinculando los mensajes de commit con los IDs de bugs registrados en JIRA.
2. Identificar las líneas de código defectuosas (modificadas o eliminadas) dentro de esos bug-fix commits.
3. Rastrear con `git blame` qué commit anterior introdujo originalmente esas líneas → ese es el *bug-introduce commit*.

### Implementación Python

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|---|---|---|---|
| `k` | Total de desarrolladores del sistema | entero ≥ 1 | `len(total_commits)` |
| `n` | Total de commits desde el inicio del sistema hasta la release actual | entero ≥ 0 | `extractor.iter_commits()` |
| `m` | Total de bug-introduce commits en ese período | entero ≥ 0 | `len(bug_introduce_commits)` |
| `C(c_i, d_j)` | Indicador binario de autoría de commit | {0, 1} | `commit.author.name` |
| `B(b_i, d_j)` | Indicador binario de autoría de bug-introduce commit | {0, 1} | `git blame` sobre bug-fix commits |
| `Q(d_j)` | Calidad del desarrollador | ratio ∈ [0, 1] | Calculado con la fórmula de la sección 3 |

---

## 5. Fuente de datos en el historial Git


## 6. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global (acumulativa)** | Sobre todo el historial, desde el inicio del sistema hasta la release actual. Es la granularidad usada por Wu et al. (2014). **Recomendada como valor primario.** |
| **Por release** | Recalcular Q(d_j) considerando solo commits hasta cada tag/release, para observar evolución de la calidad del desarrollador a lo largo del tiempo. |
| **Ventana móvil reciente** | El propio paper señala como limitación que la métrica no distingue commits recientes de antiguos, y sugiere como trabajo futuro ponderar por antigüedad o usar solo bug-introduce commits recientes para reflejar mejor la calidad *actual* del desarrollador. |

---

## 7. Rangos de interpretación

No existen umbrales formales en el paper. Los siguientes rangos son orientativos, basados en la naturaleza de la métrica (proporción inversa a la tasa histórica de introducción de bugs):

| Rango Q(d_j) | Interpretación |
|---|---|
| **1.00** | Calidad máxima: ningún commit del desarrollador introdujo bugs. |
| **0.70 – 0.99** | Calidad alta: baja proporción histórica de bugs introducidos. |
| **0.40 – 0.69** | Calidad media. |
| **0.01 – 0.39** | Calidad baja: alta proporción de commits que introdujeron bugs. |
| **0.00** | Calidad mínima: todos los commits del desarrollador introdujeron bugs. |

---

## 8. Ejemplo de cálculo

---

## 9. Relación con el ítem de encuesta

> **La calidad percibida en el código desarrollado**

La relación es **directa**: Developer Quality es la contraparte **objetiva y cuantitativa** de esta percepción subjetiva. Mientras el ítem de encuesta captura la *percepción* que se tiene sobre la calidad del código producido por un desarrollador, esta métrica la *mide empíricamente* a partir del historial real de defectos introducidos, pudiendo servir como validación o contraste de la percepción reportada por los equipos.

---
## 10. Métricas de calidad de archivo derivadas

A partir de Q(d_j), el paper propone ocho métricas de calidad de archivo (*file quality metrics*), aplicadas sobre A(f) (autores actuales del archivo *f*):

| # | Métrica | Fórmula | Sentido |
|---|---------|---------|---------|
| 1 | **MulDQ** | $\prod_{d_j \in A(f)} Q(d_j)$ | Directo (+calidad) |
| 2 | **PMulDQ** | $\prod_{d_j \in A(f)} Q(d_j)^{M(f,d_j)}$ | Directo (+calidad) |
| 3 | **WDQ** | $\sum_{d_j \in A(f)} \frac{M(f,d_j)}{\lvert C(f) \rvert} \times Q(d_j)$ | Directo (+calidad) |
| 4 | **MeanDQ** | $\frac{1}{\lvert A(f) \rvert}\sum_{d_j \in A(f)} Q(d_j)$ | Directo (+calidad) |
| 5 | **GMeanDQ** | $\left(\prod_{d_j \in A(f)} Q(d_j)\right)^{1/\lvert A(f) \rvert}$ | Directo (+calidad) |
| 6 | **MinDQ** | $\min_{d_j \in A(f)} \{Q(d_j)\}$ | Directo (+calidad) |
| 7 | **EWODQ** | $\sum_{d_j \in A(f)} \frac{1-Q(d_j)}{2^{Rank(d_j,f)-1}}$ | Inverso (+fault-proneness) |
| 8 | **TWODQ** | $\sum_{d_j \in A(f)} \frac{1-Q(d_j)}{T(d_j,f)}$ | Inverso (+fault-proneness) |

**Notas:**
- Las 6 primeras están asociadas positivamente con la calidad del archivo (a mayor valor, mejor calidad).
- EWODQ y TWODQ son inversas: a mayor valor, peor calidad esperada (mayor probabilidad de fault-proneness).
- Según los resultnados empíricos del paper (RQ2), **MulDQ, PMulDQ, MinDQ y TWODQ** resultaron las más consistentemente significativas como predictoras de fault-proneness.

---
## 11. Referencias

- Wu, Y., Yang, Y., Zhao, Y., Lu, H., Zhou, Y., & Xu, B. (2014). The influence of developer quality on software fault-proneness prediction. En *2014 Eighth International Conference on Software Security and Reliability (SERE)* (pp. 11–19). IEEE. https://doi.org/10.1109/SERE.2014.14