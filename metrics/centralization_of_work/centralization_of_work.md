# M13 – Centralization of Work (Centralización del Trabajo)

---

## 1. Descripción

La métrica **Centralization of Work** cuantifica el grado de concentración del trabajo de desarrollo entre los colaboradores de un repositorio, medido a través del coeficiente de Gini aplicado sobre la distribución de commits por desarrollador.

Su fundamento empírico proviene de Jarczyk et al. (2018), quienes calcularon el coeficiente de Gini sobre los commits de los miembros del equipo (`gini_member`) y encontraron que tiene un impacto positivo significativo sobre la tasa de cierre de issues a largo plazo (coeficiente estandarizado 0.128, p = 1.7×10⁻⁷). Este hallazgo da soporte empírico a la Hipótesis 2 del estudio: *"More centralized work distribution predicts an increase of the issue closure rate"*, derivada del concepto del *surgical team* de Brooks.

El razonamiento detrás es que en un equipo con trabajo centralizado, un grupo reducido de desarrolladores líderes concentra la mayor parte del trabajo y mantiene la coherencia conceptual del proyecto, lo que facilita la resolución de issues complejos de largo plazo.

> **Nota:** El paper calcula dos variantes del coeficiente Gini: `gini_member_author` (basado en el autor del commit) y `gini_member_commits` (basado en quien integró el commit). En el modelo reportado, ambas se agregan en la variable sintética `gini_member`. Aquí se operacionaliza sobre el autor del commit, que es el dato más directamente extraíble desde el historial Git.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | Sí |
| **Producto** | No | No |

La métrica mide una característica del **Proceso** de desarrollo (cómo se distribuye el trabajo), pero en la encuesta se presentó también bajo la dimensión **Persona**, dado que la concentración del trabajo refleja el rol y la carga de trabajo de los desarrolladores individuales.

Ítem de encuesta asociado: **C53 – La eficacia en la asignación de tareas** (orden ISL: 22). 

---

## 3. Fórmula de cálculo

$$G = \frac{\sum_{i=1}^{n}(2i - n - 1) \cdot y_i}{n^2 \cdot \bar{y}}$$

Donde:
- **n**: número de colaboradores del repositorio
- **y_i**: número de commits del colaborador i (ordenados de menor a mayor)
- **ȳ**: promedio de commits por colaborador

El resultado es un valor ∈ [0, 1]:
- **G → 0**: trabajo distribuido equitativamente entre todos los colaboradores
- **G → (n−1)/n ≈ 1**: todo el trabajo concentrado en un único desarrollador

Esta es la fórmula exacta utilizada por Jarczyk et al. (2018), sección 3.5.

### Implementación Python

Sigue el mismo patrón que `DeveloperContribution` y `CommitEntropy`: clase que extiende `Metrica`, recibe `GitExtractor` en el constructor y expone `calcular(owner=None, repo=None)`. No requiere la API de GitHub; opera íntegramente sobre el historial local de commits.

Pasos internos de `calcular()`:

1. **Iterar commits** — `extractor.iter_commits()` → acumular `counts[commit.author.name] += 1` (con soporte de caché incremental via `load_cache` / `save_cache`).
2. **Construir vector** — extraer `values()` del dict y ordenar de menor a mayor → lista `y`.
3. **Aplicar fórmula Gini** — con `n = len(y)` y `ȳ = mean(y)`, calcular el sumatorio y dividir por `n² · ȳ`.
4. **Retornar dict** con `n_contributors`, `commits_per_contributor` y `gini_commits`.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|---|---|---|---|
| `commits_per_contributor` | Dict autor → cantidad de commits | entero ≥ 0 por autor | `GitExtractor.iter_commits()` → `commit.author.name` |
| `n` | Número total de colaboradores con al menos 1 commit | entero ≥ 1 | `len(commits_per_contributor)` |
| `gini_commits` | Coeficiente de Gini sobre la distribución de commits | valor ∈ [0, 1] | Calculado con la fórmula de la sección 3 |

---

## 5. Fuente de datos en el historial Git

Esta métrica se extrae directamente del **historial de commits Git**, sin necesidad de la API de GitHub. Utiliza `GitExtractor` (wrapper sobre `gitpython`), igual que `CommitEntropy` y `DeveloperContribution`.

| Llamada | Método en `GitExtractor` | Dato obtenido |
|---|---|---|
| Iterar todos los commits de HEAD | `extractor.iter_commits()` | Objeto `commit` con `commit.author.name` y `commit.hexsha` |
| Agrupar por autor | `dict` acumulado en `calcular()` | `commits_per_contributor`: `{autor: n_commits}` |
| Calcular Gini | Lógica interna de `calcular()` | `gini_commits` ∈ [0, 1] |

---

## 6. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | Sobre todos los commits del repositorio desde su creación. Es la granularidad de Jarczyk et al. (2018). **Recomendada como valor primario.** |
| **Anual** | Calcular Gini sobre commits del año calendario para capturar evolución temporal. |
| **Por release** | Commits entre dos tags consecutivos. |

Para tldr-pages/tldr se recomienda el valor global más una serie anual para observar si la concentración del trabajo varía a lo largo del ciclo de vida del proyecto.

---

## 7. Rangos de interpretación

No existen umbrales formales en la literatura. Los siguientes rangos son orientativos, basados en la interpretación estándar del coeficiente de Gini:

| Rango G | Interpretación |
|---------|---------------|
| **0.00 – 0.30** | Distribución relativamente equitativa. Trabajo repartido entre muchos colaboradores. |
| **0.31 – 0.60** | Concentración moderada. Algunos colaboradores contribuyen significativamente más que otros. |
| **0.61 – 0.80** | Alta concentración. Un grupo reducido realiza la mayor parte del trabajo. |
| **0.81 – 1.00** | Concentración muy alta. Uno o pocos desarrolladores dominan casi toda la actividad de commits. Correlaciona positivamente con tasas de cierre de issues a largo plazo (Jarczyk et al., 2018). |

---

## 8. Ejemplo de cálculo

```python
from config.settings import REPO_PATH
from core.git_extractor import GitExtractor
from metrics.centralization_of_work.centralization_of_work import CentralizationOfWork

extractor = GitExtractor(repo_path=REPO_PATH)
metrica = CentralizationOfWork(extractor)
resultado = metrica.calcular()
```

Salida esperada (valores orientativos para tldr-pages/tldr):

```python
{
    "n_contributors": 3279,
    "commits_per_contributor": {"user_a": 3241, "user_b": 1102, "user_c": 874, ...},
    "gini_commits": 0.7916
}
```

$$G = \frac{\sum_{i=1}^{3279}(2i - 3279 - 1) \cdot y_i}{3279^2 \cdot \bar{y}} \approx 0.79$$

Un valor G ≈ 0.79 indica alta concentración: un grupo reducido de desarrolladores líderes acumula la mayor parte de los commits, patrón esperable en proyectos open source maduros con pocos *core developers* activos. Correlaciona positivamente con la tasa de cierre de issues a largo plazo (Jarczyk et al., 2018).

### Última ejecución real (junio 2026)

```json
{"n_contributors": 3279, "gini_commits": 0.7916}
```

---

## 9. Relación con el ítem de encuesta

> **C53 – La eficacia en la asignación de tareas**

La relación es **indirecta**: un alto coeficiente de Gini es una consecuencia observable de que la asignación de tareas está funcionando bien (los líderes del proyecto concentran el trabajo relevante), pero no mide la práctica de asignación en sí. 

---

## 10. Referencias

- Jarczyk, O., Jaroszewicz, S., Wierzbicki, A., Pawlak, K., & Jankowski-Lorek, M. (2018). Surgical teams on GitHub: Modeling performance of GitHub project development processes. *Information and Software Technology*, 100, 130–143. https://doi.org/10.1016/j.infsof.2018.03.010

- Brooks, F.P. (1995). *The Mythical Man-Month*. Addison-Wesley. [Citado en Jarczyk et al., 2018]

- Gini, C. (1921). Measurement of inequality of incomes. *The Economic Journal*, 31(121), 124–126. [Citado en Jarczyk et al., 2018]

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.