# M42 – Number of Active Development Branches (Cantidad de Branches de Desarrollo Activas)

---

## 1. Descripción

La métrica **Number of Active Development Branches** cuantifica la cantidad de ramas de desarrollo que presentan actividad reciente en el repositorio principal, excluyendo ramas inactivas o archivadas.

Su fundamento empírico proviene de Jarczyk et al. (2014), quienes incluyen `branches_count` como variable predictora en sus modelos de calidad de proyectos OSS en GitHub, encontrando que un mayor número de ramas se correlaciona positivamente con el rendimiento del proyecto en términos de corrección de bugs. El paper justifica esta relación señalando que el workflow típico de git para corregir errores implica crear una rama dedicada, realizar los cambios y fusionarla de vuelta — por lo que un alto número de ramas refleja un proceso de desarrollo activo y ordenado.

> **Nota de correspondencia:** La consigna C41 especifica "branches activas", mientras que Jarczyk et al. (2014) utilizan el conteo total de ramas (`branches_count`). La operacionalización propuesta aquí agrega el criterio de actividad reciente (commits en los últimos 90 días) para alinearse con la consigna, excluyendo ramas abandonadas o de larga data sin actividad.

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
- **branches**: conjunto de todas las ramas del repositorio principal (excluyendo ramas de forks, que pertenecen a repos separados).
- **last\_commit(b)**: fecha del commit más reciente en la rama b.
- **90 días**: umbral de actividad — rama con al menos 1 commit en los últimos 90 días se considera activa.

> **Decisión metodológica:** El umbral de 90 días es una convención estándar en la literatura de minería de repositorios para distinguir ramas activas de ramas abandonadas. Puede ajustarse a 30 días (actividad reciente) o 180 días (actividad semestral). Se recomienda reportar el umbral usado junto al valor calculado.

### Variantes
- **Variante 1 — Conteo total** (siguiendo Jarczyk et al., 2014): $\text{Total Branches} = \text{count}(\text{all\_branches})$
- **Variante 2 — Activas en los últimos 30 días**: $\text{Active Branches}_{30d}$

### Implementación Python

> **Corrección de implementación (jun 2026):** la ficha original recomendaba Git local (`GitExtractor.repo.branches`). **No es viable en este proyecto**, porque el clon local es el **fork** (`calidad-software-tg/tldr`): un clon de fork solo tiene `main` como rama local, y el fork en GitHub conserva una foto desactualizada de las branches (al momento de medición estaba 473 commits atrás, con 46 branches vs. 34 del original). Para medir "su repositorio principal" hay que ir contra `tldr-pages/tldr` vía la **API de GitHub**.

**Opción usada — GitHub API (GraphQL):** una sola query con `refs(refPrefix: "refs/heads/")` devuelve todas las ramas del repo principal con la fecha de su último commit (`committedDate`), sin necesidad de una llamada por rama y excluyendo automáticamente las ramas de forks (son repos separados).

```graphql
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    refs(refPrefix: "refs/heads/", first: 100, after: $cursor) {
      pageInfo { hasNextPage endCursor }
      nodes { name target { ... on Commit { committedDate } } }
    }
  }
}
```

**Opción alternativa — REST:** `GET /repos/{owner}/{repo}/branches` (lista ramas con el SHA del último commit, pero **sin** la fecha, obligando a una llamada de commit por rama).

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `all_branches` | Lista de todas las ramas del repo principal | lista de strings | GraphQL `refs(refPrefix:"refs/heads/")` |
| `last_commit_date` | Fecha del último commit por rama | timestamp | GraphQL `target { ... on Commit { committedDate } }` |
| `threshold_date` | Fecha límite de actividad (now − 90 días) | timestamp | Calculado en ejecución |
| `active_branches_count` | Ramas con último commit ≥ threshold | entero ≥ 0 | Calculado |
| `total_branches_count` | Total de ramas sin filtro | entero ≥ 0 | Calculado |

---

## 5. Fuente de datos

Esta métrica se extrae de la **API de GitHub (GraphQL)** contra el **repositorio original** `tldr-pages/tldr`. (Ver corrección en la sección 3: el Git local no sirve porque el clon disponible es el fork.)

| Llamada | Método en `GitHubExtractor` | Dato obtenido |
|---------|-----------------------------|---------------|
| GraphQL `refs(refPrefix:"refs/heads/")` | `extractor.graphql(query, vars)` | nombre + `committedDate` por rama |
| REST `GET /repos/{owner}/{repo}/branches` | `extractor.get_paginated(endpoint)` | alternativa (requiere commit por rama) |

---

## 6. Calculabilidad en tldr-pages/tldr

**Sí, calculable.** Métrica objetiva y directamente observable vía la API de GitHub.

### Resultado real (medición del 22/06/2026)

| Métrica | Valor |
|---------|-------|
| `total_branches` | **34** (coincide exacto con el badge del repo → validado) |
| `active_branches_90d` | **33** |
| `active_branches_30d` | **28** |

> **⚠️ Corrección empírica — la expectativa original era incorrecta.** La ficha preveía "un número bajo (< 10)" / "1-3 ramas activas" bajo el supuesto de que tldr-pages trabaja **solo** vía forks. **El dato real lo refuta:** hay 33 ramas activas sobre 34. El supuesto "todo vía forks" aplica a los **contribuidores externos**, pero el **equipo extendido (maintainers y traductores con acceso de escritura) ramifica directamente en el repositorio principal**. Los nombres de las ramas lo explican:
>
> - **Ramas de traducción** por página (esfuerzo de traducción al italiano marcado): `pip_ita_1..5`, `dnf_italian_1..4`, `eselect_ita_1/2`, `cpufreq_ita`, `dpkg-italian-1`, etc.
> - **Ramas de web-editor** del tipo `usuario-patch-N`, que GitHub crea automáticamente cuando alguien con acceso de escritura edita un archivo desde la interfaz web: `kant-patch-9`, `kant-patch-2`, `SpikeTheDragon40k-patch-15`, etc.
>
> Solo 1 de las 34 ramas estaba inactiva (`username-check-improvements`, último commit en enero 2026).

---

## 7. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Snapshot puntual** | Ramas activas al momento de la extracción. Granularidad natural. **Valor primario.** |
| **Serie temporal** | Calcular en distintas fechas para observar la evolución. |

---

## 8. Rangos de interpretación

Jarczyk et al. (2014) señalan que el número de ramas se correlaciona positivamente con la corrección de bugs, ya que refleja el uso del workflow de branching para aislar cambios. No proveen umbrales formales; los siguientes son orientativos:

| Rango | Interpretación |
|-------|---------------|
| **1 – 3** | Desarrollo centralizado en pocas ramas. Típico de proyectos chicos o que gestionan todo el trabajo vía forks externos. |
| **4 – 10** | Actividad moderada de branching. Equipo pequeño con ramas de feature/fix dedicadas. |
| **11 – 30** | Alta actividad de branching. Equipo activo con múltiples líneas de desarrollo en paralelo. |
| **> 30** | Muy alta actividad. Proyectos con muchos contribuidores con acceso directo al repositorio. **tldr-pages cae aquí (33 activas)**, impulsado por traducción y ediciones de web-editor del equipo extendido. |

> **Nota:** la ubicación de tldr-pages en ">30" (y no en "1-3" como se asumía originalmente) es uno de los hallazgos de la medición real.

---

## 9. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, GITHUB_API_BASE
from core.github_extractor import GitHubExtractor
from metrics.active_branches.active_branches import NumberOfActiveBranches

gh = GitHubExtractor(GITHUB_TOKEN, GITHUB_API_BASE)
metrica = NumberOfActiveBranches(gh, threshold_days=90)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")
```

Salida **real** (22/06/2026, recortada):

```python
{
    "total_branches": 34,
    "active_branches_90d": 33,
    "active_branches_30d": 28,
    "threshold_days": 90,
    "extraction_date": "2026-06-22T01:57:07Z",
    "branch_details": [
        {"name": "kant-patch-9", "last_commit": "2026-06-21", "active": True},
        {"name": "main", "last_commit": "2026-06-21", "active": True},
        {"name": "pip_ita_3", "last_commit": "2026-06-16", "active": True},
        {"name": "username-check-improvements", "last_commit": "2026-01-02", "active": False}
    ]
}
```

---

## 10. Relación con el ítem de encuesta

> **C41 – Cantidad de branches de desarrollo activas que existen en su repositorio principal**

La relación es **directa**: el ítem pregunta exactamente por el conteo de ramas activas en el repositorio principal. La única decisión metodológica es definir "activa" — se usa el criterio de commits en los últimos 90 días.

---

## 11. Observaciones metodológicas

- La métrica tiene **Fidelidad Operacional Alta** y **Riesgo de Sesgo Computacional Bajo**: es objetiva y directamente observable en la estructura del repositorio. El `total_branches` (34) se validó contra el badge del repo.

- **Decisión de fuente:** se mide contra `tldr-pages/tldr` (el repo principal de la consigna) vía API de GitHub. No se usa el clon local porque es el fork del equipo, cuyas branches no representan al repo principal (clon local ≈ solo `main`; fork en GitHub ≈ foto vieja con 46 branches).

- **Corrección del supuesto original (importante para el análisis del TG):** el modelo de forks **no** hace que el número de ramas activas del repo principal sea bajo. La medición real (33/34 activas) muestra que el equipo extendido ramifica directo en el repo principal. Esto **no** es un problema de la métrica (el total coincide con el badge); es una **corrección de la expectativa documentada** en versiones previas de esta ficha.

- **Matiz interpretativo:** muchas de las ramas activas son **efímeras** — ramas `usuario-patch-N` de un solo commit (web-editor) y ramas de traducción por página que se borran al mergear el PR. No son ramas de feature de larga vida como las que tiene en mente Jarczyk et al. (2014). Por eso el conteo alto refleja **trabajo de edición en curso** más que líneas de desarrollo paralelas sostenidas. Conviene aclararlo al interpretar el valor.

- Se recomienda reportar tanto el total de ramas (consistente con Jarczyk et al., 2014) como las ramas activas a 90 y 30 días (consistente con la consigna C41) para dar una imagen completa.

---

## 12. Referencias

- Jarczyk, O., Gruszka, B., Jaroszewicz, S., Bukowski, L., & Wierzbicki, A. (2014). GitHub Projects. Quality Analysis of Open-Source Software. In L. M. Aiello & D. McFarland (Eds.), *Social Informatics* (Vol. 8851, pp. 80–94). Springer. https://doi.org/10.1007/978-3-319-13734-6_6

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.