# CXX – Frecuencia de Participación en Discusiones Técnicas (Developer Communication Skill)

---

## 1. Descripción

La métrica **Developer Communication Skill** cuantifica la comunicación escrita realizada por los desarrolladores mediante los comentarios asociados a sus commits. En el estudio de Salamea et al., esta habilidad se operacionaliza utilizando el tamaño de los comentarios de commit (*Commit Comment Size*), medido como la cantidad de líneas empleadas por un desarrollador para documentar sus cambios.

La comunicación efectiva constituye un aspecto relevante de la colaboración en proyectos de software, ya que facilita la comprensión de modificaciones, decisiones de diseño y contexto técnico. Aunque la métrica no mide directamente la participación en discusiones técnicas entre desarrolladores, puede utilizarse como un indicador indirecto de actividad comunicacional dentro del proceso de desarrollo.

En el contexto de esta investigación, la métrica se utiliza como un **proxy** de la frecuencia de participación en discusiones técnicas. La relación conceptual surge de que los comentarios de commit representan una forma de comunicación técnica escrita asociada al código fuente. Sin embargo, debe destacarse que la métrica no captura conversaciones bidireccionales ni debates realizados en Pull Requests, Issues o canales externos de comunicación.

> **Nota metodológica:** Salamea et al. miden explícitamente la cantidad de líneas utilizadas para comentar commits. La interpretación de esta métrica como participación en discusiones técnicas constituye una adaptación conceptual realizada para vincularla con el ítem de encuesta analizado.

---

## 2. Clasificación – Dimensiones 3P

| Dimensión    | Clasificación Original ISL | Clasificación en Encuesta |
| ------------ | -------------------------- | ------------------------- |
| **Proceso**  | Sí                         | Sí                        |
| **Persona**  | Sí                         | Sí                        |
| **Producto** | No                         | No                        |

Ítem de encuesta asociado:

**"La frecuencia de participación en discusiones técnicas"**

---

## 3. Fórmula de cálculo

[
Developer\ Communication\ Skill = \sum_{i=1}^{n} comment_lines_i
]

Donde:

* `comment_lines_i`: cantidad de líneas presentes en el mensaje del commit (i).
* `n`: cantidad total de commits realizados por el desarrollador durante el período analizado.

Alternativamente puede normalizarse por cantidad de commits:

[
Average\ Comment\ Size =
\frac{\sum comment_lines_i}{n}
]

Resultado:

Cantidad promedio de líneas de comentario por commit.

### Implementación Python

```python
from collections import defaultdict

class DeveloperCommunicationSkill:

    def calcular(self, commits):
        total_lines = 0

        for commit in commits:
            mensaje = commit["commit"]["message"]
            total_lines += len(mensaje.splitlines())

        return {
            "comment_lines_total": total_lines,
            "average_comment_lines":
                total_lines / len(commits) if commits else 0
        }
```

---

## 4. Variables necesarias y unidades

| Variable                | Descripción                    | Unidad        | Origen     |
| ----------------------- | ------------------------------ | ------------- | ---------- |
| `message`               | Mensaje del commit             | Texto         | GitHub API |
| `comment_lines`         | Cantidad de líneas del mensaje | Líneas        | Calculado  |
| `n`                     | Cantidad de commits            | Entero        | Calculado  |
| `average_comment_lines` | Promedio de líneas por commit  | Líneas/commit | Calculado  |

---

## 5. Fuente de datos

La métrica utiliza la REST API de GitHub.

| Llamada | Endpoint                            | Datos obtenidos                  |
| ------- | ----------------------------------- | -------------------------------- |
| Commits | `GET /repos/{owner}/{repo}/commits` | mensaje del commit, autor, fecha |

Para análisis por desarrollador puede utilizarse el campo:

```text
commit.author.name
```

y agrupar los commits por autor.

---

## 6. Granularidad temporal

| Granularidad      | Descripción                  |
| ----------------- | ---------------------------- |
| Global            | Todos los commits históricos |
| Anual             | Filtrado por año             |
| Mensual           | Evolución temporal detallada |
| Por desarrollador | Comunicación individual      |

---

## 7. Rangos de interpretación

No existen umbrales formalmente definidos en la literatura.

| Rango               | Interpretación        |
| ------------------- | --------------------- |
| < 1 línea/commit    | Comunicación mínima   |
| 1 – 3 líneas/commit | Comunicación básica   |
| 3 – 6 líneas/commit | Comunicación moderada |
| > 6 líneas/commit   | Comunicación extensa  |

Estos rangos deben interpretarse únicamente como referencia exploratoria.

---

## 8. Calculabilidad en tldr-pages/tldr

**Calculable.**

Todos los commits del repositorio contienen mensajes accesibles mediante la API de GitHub.

La implementación requiere:

1. Obtener el historial de commits.
2. Extraer el mensaje asociado a cada commit.
3. Contar la cantidad de líneas.
4. Agregar por desarrollador o para el proyecto completo.

No requiere minería de Issues ni Pull Requests, por lo que presenta una complejidad de extracción baja.

---

## 9. Ejemplo de cálculo

Supóngase un desarrollador con tres commits:

```text
Commit 1:
Fix typo in curl page

Commit 2:
Add docker compose examples
Update examples section

Commit 3:
Refactor command descriptions
Improve formatting
Update aliases
```

Cantidad de líneas:

```text
1 + 2 + 3 = 6 líneas
```

Promedio:

```text
6 / 3 = 2 líneas por commit
```

---

## 10. Relación con el ítem de encuesta

> "La frecuencia de participación en discusiones técnicas"

La relación es **indirecta**.

La métrica mide comunicación escrita asociada a commits, mientras que el ítem de encuesta se refiere a participación en discusiones técnicas entre desarrolladores.

Los comentarios de commit representan una forma de comunicación técnica y pueden utilizarse como indicador parcial de actividad comunicacional. Sin embargo, no capturan interacciones bidireccionales, debates técnicos ni conversaciones realizadas mediante Pull Requests, Issues o canales externos.

La fidelidad operacional es **media-baja**. La métrica debe interpretarse como un proxy de comunicación técnica más que como una medición directa de participación en discusiones.

---

## 11. Referencias

Salamea, H., Shimabukuro, D., Suescún, M., Fuentes, M., González, J., & Robiolo, G. Developer Communication Skill and Documentation Quality as Characteristics of Software Quality.
