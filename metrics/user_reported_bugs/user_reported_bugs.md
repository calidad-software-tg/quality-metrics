# M39 – Number of Bugs Detected by Users (Número de Bugs Detectados por Usuarios)

---

## 1. Descripción

La métrica **Number of Bugs Detected by Users** cuantifica la cantidad de defectos o errores detectados y reportados por usuarios externos al equipo de desarrollo, es decir, personas que no forman parte del equipo core del proyecto.

Su fundamento empírico proviene de Vasilescu et al. (2015), quienes operacionalizan la calidad externa del software (`n_user_bugs`) como el conteo mensual de issues etiquetados como bugs y reportados por contribuyentes externos — personas que nunca fueron parte del equipo core del proyecto. El paper demuestra que la adopción de integración continua (CI) no incrementa el número de bugs reportados por usuarios, lo que valida esta métrica como indicador de calidad externa experimentada por el usuario final.

> **Nota de correspondencia:** La métrica del catálogo ISL/JAIIO 2022 "Number of Bugs Detected by Users" tiene correspondencia directa con `n_user_bugs` de Vasilescu et al. (2015). Sin embargo, la operacionalización exacta del paper requiere dos condiciones que presentan limitaciones en tldr-pages: (1) etiquetado consistente de issues como bugs (el paper usó solo proyectos donde ≥75% de los issues tenían tags), y (2) identificación de usuarios externos como personas que nunca fueron core developers. Ambas condiciones requieren adaptaciones metodológicas para este repositorio específico.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión | Clasificación Original ISL | Clasificación en Encuesta |
|-----------|---------------------------|---------------------------|
| **Proceso** | Sí | Sí |
| **Persona** | No | Sí |
| **Producto** | Sí | Sí |

Ítem de encuesta asociado: **C35 – Número de Bugs detectados por Usuarios** (ID Consigna: 35).

La relación con el ítem es **directa**: la consigna reproduce prácticamente sin transformación la definición de la métrica original.

---

## 3. Fórmula de cálculo

$$\text{User Bugs} = \text{count}(\text{issues}_{\text{bug}} \cap \text{reporter} \notin \text{core\_developers})$$

Donde:
- **issues\_bug**: issues identificados como reportes de defectos o errores.
- **core\_developers**: conjunto de usuarios con rol de maintainer o con historial de commits directos al repositorio.
- Un issue es de **usuario** si quien lo reportó nunca fue parte del equipo core.

### Identificación de bugs en tldr-pages

Dado que tldr-pages **no usa etiquetado consistente de bugs**, se proponen dos aproximaciones en orden de preferencia:

**Aproximación 1 — Por labels existentes (preferida si hay labels):**
```
issues con label que contenga: "bug", "error", "incorrect", "outdated", "wrong"
reportados por usuarios no-core
```

**Aproximación 2 — Por keywords en título/descripción:**
```
issues cuyo título o body contenga: "wrong", "incorrect", "outdated",
"deprecated", "broken", "error", "not working", "fix"
reportados por usuarios no-core
```

**Definición de usuario no-core para tldr-pages:**
Usuario que cumple TODAS las condiciones:
- Nunca tuvo acceso de escritura al repositorio
- No aparece en `MAINTAINERS.md`
- No tiene commits directos en la rama principal (fuera de PRs)

### Implementación Python

Requiere dos fases:
1. **Identificar core developers**: obtener lista de maintainers via `MAINTAINERS.md` + usuarios con commits directos via Git log.
2. **Filtrar issues de usuarios**: issues abiertos por personas fuera de esa lista, que contengan keywords de bug en labels o título.

---

## 4. Variables necesarias y unidades

| Variable | Descripción | Unidad | Origen |
|----------|-------------|--------|--------|
| `core_developers` | Set de logins de maintainers y contributors con commit directo | set de strings | `MAINTAINERS.md` + `GitExtractor.iter_commits()` |
| `all_issues` | Todos los issues del repositorio | lista | REST `GET /repos/{owner}/{repo}/issues?state=all` |
| `bug_issues` | Issues identificados como bugs por label o keyword | lista filtrada | Filtro sobre `all_issues` |
| `user_bug_issues` | Issues de bug reportados por usuarios no-core | lista filtrada | `bug_issues` donde `reporter not in core_developers` |
| `n_user_bugs` | Conteo final | entero ≥ 0 | `len(user_bug_issues)` |

---

## 5. Fuente de datos

Combina **API de GitHub** y **historial local de Git**.

| Llamada | Método | Dato obtenido |
|---------|--------|---------------|
| REST `GET /repos/{owner}/{repo}/issues?state=all` paginado | `extractor.get_paginated(endpoint)` | todos los issues con reporter y labels |
| Git log commits directos | `GitExtractor.iter_commits()` | usuarios con commits directos |
| Contenido de `MAINTAINERS.md` | `extractor.get_file_content()` o lectura local | lista de maintainers |

---

## 6. Calculabilidad en tldr-pages/tldr

**Parcialmente calculable — con limitaciones metodológicas significativas.**

**Lo que SÍ es calculable:**
- Identificar el conjunto de core developers (maintainers + contributors con commits directos) via GitHub API y Git log.
- Filtrar issues reportados por usuarios fuera de ese conjunto.
- Aproximar bugs por keywords en título/body de issues.

**Limitaciones importantes:**

1. **tldr-pages no es software ejecutable.** Los "bugs" en este repositorio son páginas de documentación incorrectas, desactualizadas o faltantes — no fallos de código en ejecución. El concepto de "bug detectado por usuario" difiere del contexto del paper, donde un usuario ejecuta software y encuentra un crash o comportamiento incorrecto.

2. **Etiquetado inconsistente.** Vasilescu et al. (2015) trabajaron exclusivamente con proyectos donde ≥75% de los issues tenían tags. tldr-pages no cumple ese criterio, lo que obliga a usar aproximaciones por keywords con menor precisión.

3. **Ambigüedad entre bug y feature request.** En tldr-pages, un issue de "página incorrecta" es técnicamente un bug de documentación, pero un issue de "página faltante" es una solicitud de nueva funcionalidad. La distinción no siempre es clara en el título o body del issue.

4. **Dependencia de la lista de core developers.** Esteban debe proveer o confirmar la lista definitiva de core developers/maintainers para poder calcular correctamente qué issues son de "usuarios externos".

---

## 7. Granularidad temporal

| Granularidad | Descripción |
|--------------|-------------|
| **Global** | Total histórico de user bugs desde la creación del repositorio. **Valor primario.** |
| **Anual** | Bugs de usuario por año para observar evolución. |
| **Mensual** | Consistente con la metodología de Vasilescu et al. (2015), que calculó `n_user_bugs` mensualmente. |

---

## 8. Rangos de interpretación

No existen umbrales formales. Los siguientes rangos son orientativos para el **total histórico** en un repositorio de documentación:

| Rango | Interpretación |
|-------|---------------|
| **0 – 50** | Muy pocos reportes de errores por usuarios. Documentación estable o comunidad pequeña. |
| **51 – 200** | Reportes moderados. Comunidad activa que detecta y reporta inconsistencias. |
| **> 200** | Alto volumen de reportes. Repositorio ampliamente usado, con muchas páginas susceptibles de quedar desactualizadas. |

Vasilescu et al. (2015) encontraron que la adopción de CI no aumenta los bugs reportados por usuarios, lo que sugiere que esta métrica refleja principalmente la **calidad percibida por el usuario final** y no es directamente modificable por prácticas de integración continua.

---

## 9. Ejemplo de cálculo

```python
from config.settings import GITHUB_TOKEN, API_BASE, REPO_PATH
from core.github_extractor import GitHubExtractor
from core.git_extractor import GitExtractor
from metrics.user_reported_bugs.user_reported_bugs import UserReportedBugs

github_extractor = GitHubExtractor(token=GITHUB_TOKEN, api_base=API_BASE)
git_extractor = GitExtractor(repo_path=REPO_PATH)
metrica = UserReportedBugs(github_extractor, git_extractor)
resultado = metrica.calcular(owner="tldr-pages", repo="tldr")
```

Salida esperada (valores orientativos para tldr-pages/tldr):

```python
{
    "core_developers_count": 47,
    "total_issues": 14203,
    "bug_issues_by_label": 0,
    "bug_issues_by_keyword": 312,
    "user_bug_issues": 287,
    "n_user_bugs": 287,
    "identification_method": "keyword",
    "keywords_used": ["wrong", "incorrect", "outdated", "deprecated", "broken", "error"]
}
```

> **Nota:** El valor de `bug_issues_by_label` es 0 porque tldr-pages no usa labels de bug de forma sistemática. La identificación por keyword es la única aproximación viable.

---

## 10. Relación con el ítem de encuesta

> **C35 – Número de Bugs detectados por Usuarios**

La relación es **directa**: el ítem pregunta exactamente por la cantidad de bugs o errores detectados por usuarios, que es lo que mide `n_user_bugs`. La limitación es que en tldr-pages el concepto de "bug" aplica a documentación incorrecta, no a código ejecutable, lo que introduce una diferencia conceptual respecto al contexto original del paper.

---

## 11. Observaciones metodológicas

- **Pendiente de validación con Esteban:** confirmar la lista definitiva de core developers/maintainers para garantizar la correcta clasificación de issues como "de usuario" vs "de equipo core".
- La métrica es **sensible a la definición de core developer**: si se define de forma muy amplia (incluyendo todo contributor con al menos 1 PR mergeado), el número de "usuarios externos" se reduce significativamente.
- Se recomienda registrar explícitamente el método de identificación de bugs usado (label vs keyword) y las keywords empleadas, para garantizar reproducibilidad.
- Esta métrica tiene **Fidelidad Operacional Media** para tldr-pages: la fórmula es directamente aplicable pero la naturaleza del repositorio (documentación vs software ejecutable) introduce una brecha conceptual respecto al paper de referencia.

---

## 12. Referencias

- Vasilescu, B., Yu, Y., Wang, H., Devanbu, P., & Filkov, V. (2015). Quality and productivity outcomes relating to continuous integration in GitHub. *Proceedings of the 2015 10th Joint Meeting on Foundations of Software Engineering (ESEC/FSE 2015)*, 805–816. ACM. https://doi.org/10.1145/2786805.2786850

- Alonso, E. J., & Robiolo, G. (2022b, octubre). Determinación de la calidad de producto, persona y proceso en entornos de desarrollo con GitHub: un estudio sistemático de la literatura [ponencia]. Simposio Argentino de Ingeniería de Software (ASSE 2022), JAIIO 51, Universidad Abierta Interamericana, Buenos Aires, Argentina.