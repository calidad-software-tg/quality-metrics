# M42 – Number of Active Development Branches (Cantidad de Branches de Desarrollo Activas)

---

## 1. Descripción

La métrica **Number of Active Development Branches** cuantifica la cantidad de ramas de desarrollo que presentan actividad reciente en el repositorio principal, excluyendo ramas inactivas o archivadas.

Su fundamento empírico proviene de Jarczyk et al. (2014), quienes incluyen `branches_count` como variable predictora en sus modelos de calidad de proyectos OSS en GitHub, encontrando que un mayor número de ramas se correlaciona positivamente con el rendimiento del proyecto en términos de corrección de bugs. El paper justifica esta relación señalando que el workflow típico de git para corregir errores implica crear una rama dedicada, realizar los cambios y fusionarla de vuelta — por lo que un alto número de ramas refleja un proceso de desarrollo activo y ordenado.

> **Nota de correspondencia:** La consigna C41 especifica "branches **activas**", mientras que Jarczyk et al. (2014) utilizan el conteo total de ramas (`branches_count`). La operacionalización propuesta aquí agrega el criterio de actividad reciente (commits en los últimos 90 días) para alinearse con la consigna, excluyendo ramas abandonadas o de larga data sin actividad.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | No |
| **Producto** | Sí | Sí |

Ítem de encuesta asociado: **C41 – Cantidad de branches de desarrollo activas que existen en su repositorio principal** (ID Consigna: 41).

La relación con el ítem es **directa**: la consigna reproduce prácticamente sin transformación la definición de la métrica, solicitando el conteo de ramas activas en el repositorio principal.

---

## 3. Fórmula de cálculo

$$\text{Active Branches} = \text{count}(\{b \in \text{branches} \mid \text{last\_commit}(b) \geq t_{now} - 90\text{ días}\})$$

Donde:
- **branches**: conjunto de todas las ramas del repositorio (excluyendo ramas remotas de forks).
- **last\_commit(b)**: fecha del commit más reciente en la rama b.
- **90 días**: umbral de actividad — rama con al menos 1 commit en los últimos 90 días se considera activa.

> **Decisión metodológica:** El umbral de 90 días es una convención estándar en la literatura de minería de repositorios para distinguir ramas activas de ramas abandonadas. Puede ajustarse a 30 días (actividad reciente) o 180 días (actividad semestral) según los requerimientos del análisis. Se recomienda reportar el umbral usado junto al valor calculado.

### Variantes

**Variante 1 — Conteo total (siguiendo Jarczyk et al., 2014):**
$$\text{Total Branches} = \text{count}(\text{all\_branches})$$

**Variante 2 — Activas en los últimos 30 días:**
$$\text{Active Branches}_{30d} = \text{count}(\{b \mid \text{last\_commit}(b) \geq t_{now} - 30\text{ días}\})$$

### Implementación Python

Puede implementarse via **GitHub API** o **Git local**. La opción Git local es más eficiente para repositorios grandes:

**Opción A — Git local (recomendada):**
```python
# Usando GitExtractor
branches = extractor.repo.branches  # lista de ramas locales
active = [b for b in branches if b.commit.committed_date >= threshold]
```

**Opción B — GitHub API REST:**
```
GET /repos/{owner}/{repo}/branches
```
Retorna lista de ramas con el SHA del último commit. Luego se consulta la fecha de cada commit para aplicar el filtro de actividad.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `all_branches` | Lista de todas las ramas del repositorio | lista de strings | `GitExtractor.repo.branches` o REST `GET /repos/{owner}/{repo}/branches` |
| `last_commit_date` | Fecha del último commit por rama | timestamp | `GitExtractor.iter_commits(branch)` o REST `GET /repos/{owner}/{repo}/commits?sha={branch}` |
| `threshold_date` | Fecha límite de actividad (`now - 90 días`) | timestamp | Calculado en ejecución |
| `active_branches_count` | Ramas con último commit ≥ threshold | entero ≥ 0 | Calculado |
| `total_branches_count` | Total de ramas sin filtro | entero ≥ 0 | Calculado |

---

## 5. Fuente de datos

Esta métrica puede extraerse desde el **historial local de Git** o la **API de GitHub**. La opción Git local es preferida por eficiencia.

| Llamada | Método | Dato obtenido |
|---------|--------|---------------|
| Lista de ramas locales | `GitExtractor.repo.branches` | `all_branches` |
| Último commit por rama | `GitExtractor.repo.commit(branch.name)` | `last_commit_date` por rama |
| REST `GET /repos/{owner}/{repo}/branches` | `extractor.get_paginated(endpoint)` | alternativa via API |

---

## 6. Calculabilidad en tldr-pages/tldr

**Sí, calculable.**

El repositorio tldr-pages/tldr es un repositorio Git estándar con historial de ramas accesible tanto via Git local como via GitHub API. La métrica es directamente extraíble sin ambigüedades metodológicas.

**Consideraciones específicas para tldr-pages:**
- tldr-pages usa un modelo de contribución **basado en PRs desde forks**, no desde ramas del repositorio principal. Esto significa que la mayoría de las contribuciones no crean ramas en el repositorio principal — los contributors trabajan en sus propios forks.
- Las ramas en el repositorio principal son principalmente ramas de mantenimiento y desarrollo del equipo core (maintainers).
- Se espera un **número bajo de ramas activas** en el repositorio principal (probablemente < 10), lo cual es consistente con el modelo de contribución del proyecto.

> **Advertencia metodológica:** Si el valor resultante es muy bajo (1-3 ramas activas), puede indicar que el repositorio usa principalmente la rama `main` y gestiona el trabajo a través de forks externos en lugar de ramas internas. Esto es válido para el modelo de tldr-pages y debe documentarse en el análisis.

---

## 7. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Snapshot puntual** | Ramas activas al momento de la extracción. Es la granularidad natural de esta métrica. **Recomendada como valor primario.** |
| **Serie temporal** | Calcular en diferentes fechas para observar evolución del número de ramas activas. |

---

## 8. Rangos de interpretación

Jarczyk et al. (2014) señalan que el número de ramas se correlaciona positivamente con la corrección de bugs, ya que refleja el uso del workflow de branching para aislar cambios. Sin embargo, no proveen umbrales formales. Los siguientes rangos son orientativos:

| Rango | Interpretación |
|-------|---------------|
| **1 – 3** | Desarrollo centralizado en pocas ramas. Típico de proyectos con modelo de contribución via forks externos (como tldr-pages). |
| **4 – 10** | Actividad moderada de branching. Equipo pequeño con ramas de feature/fix dedicadas. |
| **11 – 30** | Alta actividad de branching. Equipo activo con múltiples líneas de desarrollo paralelas. |
| **> 30** | Muy alta actividad. Proyectos grandes con muchos contributors con acceso directo al repositorio. |

---

## 9. Ejemplo de cálculo

```python
from config.settings import REPO_PATH
from core.git_extractor import GitExtractor
from metrics.active_branches.active_branches import NumberOfActiveBranches

extractor = GitExtractor(repo_path=REPO_PATH)
metrica = NumberOfActiveBranches(extractor)
resultado = metrica.calcular(threshold_days=90)
```

Salida esperada (valores orientativos para tldr-pages/tldr):

```python
{
    "total_branches": 4,
    "active_branches_90d": 2,
    "active_branches_30d": 1,
    "threshold_days": 90,
    "extraction_date": "2026-06-06T19:00:00Z",
    "branch_details": [
        {"name": "main", "last_commit": "2026-06-06", "active": True},
        {"name": "gh-pages", "last_commit": "2026-05-15", "active": True},
        {"name": "v1.x", "last_commit": "2024-01-10", "active": False},
        {"name": "archive/old-format", "last_commit": "2023-06-01", "active": False}
    ]
}
```

$$\text{Active Branches}_{90d} = 2$$

Un valor de 2 ramas activas es esperable para tldr-pages dado su modelo de contribución basado en forks externos. El trabajo de los contributors no crea ramas en el repositorio principal.

---

## 10. Relación con el ítem de encuesta

> **C41 – Cantidad de branches de desarrollo activas que existen en su repositorio principal**

La relación es **directa**: el ítem pregunta exactamente por el conteo de ramas activas en el repositorio principal. La única decisión metodológica es definir qué se considera "activa" — se usa el criterio de commits en los últimos 90 días como umbral estándar.

---

## 11. Observaciones metodológicas

- La métrica tiene **Fidelidad Operacional Alta** y **Riesgo de Sesgo Computacional Bajo** según la planilla: es una métrica objetiva y directamente observable en la estructura del repositorio.
- **Importante para tldr-pages:** El modelo de contribución via forks hace que el número de ramas activas en el repositorio principal sea inherentemente bajo. Esto no indica baja calidad — es una característica del modelo de desarrollo del proyecto. Debe contextualizarse en el análisis final.
- Se recomienda reportar tanto el **total de ramas** (consistente con Jarczyk et al., 2014) como las **ramas activas** (consistent con la consigna C41) para dar una imagen completa.

---

## 12. Referencias

- Jarczyk, O., Gruszka, B., Jaroszewicz, S., Bukowski, L., & Wierzbicki, A. (2014). GitHub Projects. Quality Analysis of Open-Source Software. In L. M. Aiello & D. McFarland (Eds.), *Social Informatics* (Vol. 8851, pp. 80–94). Springer. https://doi.org/10.1007/978-3-319-13734-6_6

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.